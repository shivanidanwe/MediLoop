"""
MediLoop Notification Agent.
Synthesizes intelligence from preceding AI agents to generate structured notification payloads
for Customers, Pharmacists, and System Administrators without directly calling external push APIs.
"""
from datetime import datetime
from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError


class NotificationAgent(BaseAgent):
    """
    Agent responsible for analyzing context metadata from Drug Safety, Inventory,
    Order Recommendation, and Refill Reminder agents to formulate structured notification payloads.
    """

    @property
    def name(self) -> str:
        return "notification_agent"

    @property
    def description(self) -> str:
        return (
            "Synthesizes outputs from preceding AI agents to generate structured notification "
            "payloads for Customers, Pharmacists, and System Administrators."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [
            AgentEvent.ORDER_RECOMMENDED,
            AgentEvent.REFILL_REMINDER,
            AgentEvent.SAFETY_VALIDATION_COMPLETED,
            AgentEvent.INVENTORY_CHECKED,
            AgentEvent.ORDER_CREATED,
            AgentEvent.ORDER_CONFIRMED,
            AgentEvent.MEDICINES_MATCHED,
            AgentEvent.MEDICINES_EXTRACTED,
            AgentEvent.OCR_COMPLETED,
            AgentEvent.PRESCRIPTION_UPLOADED,
        ]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Handles event if metadata or medicine entries exist.
        """
        has_metadata = bool(context.metadata)
        has_medicines = len(context.matched_medicines) > 0 or len(context.extracted_medicines) > 0
        return event in self.handled_events and (has_metadata or has_medicines)

    async def validate(self, context: AgentContext) -> bool:
        """
        Validates presence of metadata or medicine records in context.
        """
        if not context.metadata and not context.matched_medicines and not context.extracted_medicines:
            raise AgentValidationError(
                "NotificationAgent validation failed: No metadata or medicine records available in context to generate notifications."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Formulates notification payloads and updates context.metadata['notifications'].
        """
        now_str = datetime.now().isoformat()
        notifications: List[Dict[str, Any]] = []

        safety_report = context.metadata.get("drug_safety", {})
        inventory_report = context.metadata.get("inventory", {})
        order_rec = context.metadata.get("order_recommendation", {})
        refill_report = context.metadata.get("refill_report", {})

        # 1. Drug Safety Notifications
        if safety_report.get("requires_pharmacist_review") or safety_report.get("risk_level") in ("HIGH", "CRITICAL"):
            risk = safety_report.get("risk_level", "HIGH")
            notifications.append({
                "recipient": "pharmacist",
                "category": "SAFETY",
                "title": f"Clinical Safety Review Required ({risk} Risk)",
                "message": f"Prescription #{context.prescription_id or 'N/A'} requires manual pharmacist review. Risk level: {risk}.",
                "priority": "CRITICAL",
                "channel": "DASHBOARD",
                "created_at": now_str,
            })
            notifications.append({
                "recipient": "customer",
                "category": "SAFETY",
                "title": "Pharmacist Review in Progress",
                "message": "Your prescription requires verification by our clinical pharmacist before checkout.",
                "priority": "HIGH",
                "channel": "IN_APP",
                "created_at": now_str,
            })

        # 2. Inventory Availability Notifications
        if inventory_report.get("overall_status") == "PARTIAL_FULFILLMENT":
            notifications.append({
                "recipient": "customer",
                "category": "INVENTORY",
                "title": "Pharmacy Inventory Update",
                "message": "Some prescribed medicines are out of stock at your selected pharmacy. MediLoop AI has suggested optimal alternative options.",
                "priority": "MEDIUM",
                "channel": "IN_APP",
                "created_at": now_str,
            })

        # 3. Order Recommendation Notifications
        if order_rec.get("order_status") == "READY_FOR_CHECKOUT":
            pharm_name = order_rec.get("recommended_pharmacy", {}).get("name", "MediLoop Pharmacy")
            notifications.append({
                "recipient": "customer",
                "category": "AI",
                "title": "Order Ready for Checkout",
                "message": f"Your prescription is verified and ready for checkout at {pharm_name}.",
                "priority": "LOW",
                "channel": "PUSH_NOTIFICATION",
                "created_at": now_str,
            })

        # 4. Refill Reminder Notifications
        if refill_report.get("requires_notification"):
            days_rem = refill_report.get("days_remaining", 0)
            status = refill_report.get("status", "READY_FOR_REORDER")
            msg = (
                f"Your medication supply is OVERDUE for reorder!"
                if status == "OVERDUE"
                else f"Your medication supply finishes in {days_rem} days. Tap to reorder now."
            )
            notifications.append({
                "recipient": "customer",
                "category": "REFILL",
                "title": "Medicine Refill Reminder",
                "message": msg,
                "priority": "MEDIUM" if status == "READY_FOR_REORDER" else "HIGH",
                "channel": "IN_APP",
                "created_at": now_str,
            })

        # 5. General Prescription Processed Notification (Fallback if empty)
        if not notifications:
            notifications.append({
                "recipient": "customer",
                "category": "PRESCRIPTION",
                "title": "Prescription Processed",
                "message": f"Prescription scan #{context.prescription_id or 'N/A'} has been analyzed by MediLoop AI.",
                "priority": "LOW",
                "channel": "IN_APP",
                "created_at": now_str,
            })

        context.metadata["notifications"] = notifications

        # Persist customer notifications into PostgreSQL Notification table
        if getattr(context, "db", None):
            try:
                from app.models.notification import Notification
                c_id = context.metadata.get("customer_id") or getattr(context, "user_id", None)
                if c_id:
                    for notif in notifications:
                        if notif.get("recipient") == "customer":
                            db_notif = Notification(
                                user_id=int(c_id),
                                title=notif.get("title", "MediLoop Alert"),
                                message=notif.get("message", ""),
                                notification_type=notif.get("category", "SYSTEM_ALERT"),
                                is_read=False
                            )
                            context.db.add(db_notif)
                    context.db.commit()
            except Exception:
                pass

        for n in notifications:
            context.add_recommendation(
                f"Notification Payload Created [{n['recipient'].upper()}] - {n['title']} ({n['channel']})"
            )

        return context
