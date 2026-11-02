"""
MediLoop Order Recommendation Agent.
Synthesizes clinical safety reviews, inventory availability, and pharmacy metrics
into an optimal order recommendation strategy.
"""
from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


class OrderRecommendationAgent(BaseAgent):
    """
    Agent responsible for analyzing outputs from Drug Safety, Inventory Availability,
    and Medicine Matching agents to formulate the optimal order fulfillment strategy.
    """

    @property
    def name(self) -> str:
        return "order_recommendation_agent"

    @property
    def description(self) -> str:
        return (
            "Synthesizes drug safety reports, inventory availability, and pharmacy metrics "
            "into an optimal order recommendation strategy."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [
            AgentEvent.INVENTORY_CHECKED,
            AgentEvent.SAFETY_VALIDATION_COMPLETED,
            AgentEvent.MEDICINES_MATCHED,
            AgentEvent.MEDICINES_EXTRACTED,
            AgentEvent.OCR_COMPLETED,
            AgentEvent.PRESCRIPTION_UPLOADED,
        ]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Handles event if matched_medicines or extracted_medicines exists.
        """
        has_matched = len(context.matched_medicines) > 0
        has_extracted = len(context.extracted_medicines) > 0
        return event in self.handled_events and (has_matched or has_extracted)

    async def validate(self, context: AgentContext) -> bool:
        """
        Validates presence of medicine records in context before recommendation.
        """
        if not context.matched_medicines and not context.extracted_medicines:
            raise AgentValidationError(
                "OrderRecommendationAgent validation failed: No medicines available in context to formulate recommendation."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Formulates order recommendation and updates context.metadata['order_recommendation'].
        """
        safety_report = context.metadata.get("drug_safety", {})
        inventory_report = context.metadata.get("inventory", {})

        selected_pharmacy = inventory_report.get("selected_pharmacy") or {
            "id": context.pharmacy_id or 1,
            "name": "MediLoop Central Pharmacy",
        }
        alt_pharmacies = inventory_report.get("alternative_pharmacies", [])
        inventory_complete = inventory_report.get("complete_order", True)
        safety_requires_review = safety_report.get("requires_pharmacist_review", False)
        risk_level = safety_report.get("risk_level", "LOW")

        reasoning: List[str] = []
        recommended_pharmacy = selected_pharmacy

        # 1. Optimal Pharmacy Selection
        if inventory_complete:
            reasoning.append(
                f"Selected pharmacy '{selected_pharmacy.get('name')}' has 100% medicine stock available."
            )
        elif alt_pharmacies and alt_pharmacies[0].get("fulfillment_percentage", 0.0) == 100.0:
            top_alt = alt_pharmacies[0]
            recommended_pharmacy = {
                "id": top_alt["pharmacy_id"],
                "name": top_alt["pharmacy_name"],
                "address": top_alt["address"],
                "rating": top_alt["rating"],
            }
            reasoning.append(
                f"Recommending switch to '{top_alt['pharmacy_name']}' to achieve 100% complete order fulfillment."
            )
        else:
            reasoning.append(
                f"Pharmacy '{selected_pharmacy.get('name')}' offers partial fulfillment. Additional items queued for alternative sourcing."
            )

        # 2. Safety Review Awareness
        if safety_requires_review:
            reasoning.append(
                f"Clinical Drug Safety Agent flagged {risk_level} risk level. Mandatory pharmacist review required prior to order checkout."
            )
        else:
            reasoning.append("Clinical drug safety checks passed with LOW/MEDIUM risk.")

        # 3. Order Status Determination
        if safety_requires_review:
            order_status = "REQUIRES_PHARMACIST_REVIEW"
        elif inventory_complete or (recommended_pharmacy != selected_pharmacy):
            order_status = "READY_FOR_CHECKOUT"
        elif inventory_report.get("overall_status") == "PARTIAL_FULFILLMENT":
            order_status = "PARTIAL_RECOMMENDED"
        else:
            order_status = "CANNOT_FULFILL"

        # 4. Confidence Score Calculation
        confidence = 0.95
        if safety_requires_review:
            confidence -= 0.15
        if order_status == "PARTIAL_RECOMMENDED":
            confidence -= 0.10
        elif order_status == "CANNOT_FULFILL":
            confidence -= 0.40

        confidence = max(0.50, min(0.98, round(confidence, 2)))

        recommendation_result = {
            "recommended_pharmacy": recommended_pharmacy,
            "order_status": order_status,
            "recommendation_confidence": confidence,
            "requires_pharmacist_review": safety_requires_review,
            "reasoning": reasoning,
            "suggested_alternatives": inventory_report.get("alternative_medicines", []),
        }

        context.metadata["order_recommendation"] = recommendation_result

        # Auto-populate active Cart in PostgreSQL if order is ready or partially ready
        if getattr(context, "db", None) and not safety_requires_review and order_status in ("READY_FOR_CHECKOUT", "PARTIAL_FULFILLMENT"):
            try:
                from app.models.cart import Cart, CartItem, CartStatus, CartItemSource
                c_id = int(context.metadata.get("customer_id") or getattr(context, "user_id", 1))
                p_id = int(recommended_pharmacy.get("id") or 1)
                active_cart = context.db.query(Cart).filter(
                    Cart.customer_id == c_id,
                    Cart.status == CartStatus.ACTIVE
                ).first()
                if not active_cart:
                    active_cart = Cart(customer_id=c_id, pharmacy_id=p_id, status=CartStatus.ACTIVE)
                    context.db.add(active_cart)
                    context.db.commit()
                    context.db.refresh(active_cart)
                else:
                    # Clear preexisting cart items so older, unrelated items do not pollute this prescription
                    context.db.query(CartItem).filter(CartItem.cart_id == active_cart.id).delete()

                subtotal = 0.0
                for med_item in (context.matched_medicines or []):
                    m_id = med_item.get("id") or med_item.get("medicine_id")
                    if m_id:
                        qty_val = str(med_item.get("quantity") or "10").strip()
                        qty = int(qty_val) if qty_val.isdigit() else 1
                        u_price = float(med_item.get("price") or 45.0)
                        subtotal += (qty * u_price)
                        existing_ci = context.db.query(CartItem).filter(
                            CartItem.cart_id == active_cart.id,
                            CartItem.medicine_id == m_id
                        ).first()
                        if not existing_ci:
                            new_ci = CartItem(
                                cart_id=active_cart.id,
                                medicine_id=m_id,
                                quantity=qty,
                                unit_price=u_price,
                                total_price=qty * u_price,
                                source=CartItemSource.PRESCRIPTION
                            )
                            context.db.add(new_ci)
                active_cart.subtotal = subtotal
                active_cart.total_amount = subtotal
                context.db.commit()
            except Exception:
                pass

        # Update context recommendations for frontend/user display
        context.add_recommendation(
            f"AI Recommendation: Order status is {order_status} at '{recommended_pharmacy.get('name')}'. Confidence: {confidence:.2f}."
        )

        return context
