"""
MediLoop Multi-Agent Orchestration Layer - Agent 4: Order Agent.
Prepares a ready-to-place order draft after safety screening has passed:
- Evaluates stock availability against pharmacy_inventory.
- Respects patient medicine selections without altering prescribed strengths.
- Computes decimal-safe pricing and snapshots unit prices.
- Prepares Cart and generates draft Order with READY_TO_PLACE status.
- Implements strict idempotency to prevent duplicate orders.
"""
import uuid
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.medicine import Medicine
from app.models.prescription import Prescription
from app.schemas.orchestration import (
    OrderPreparationSchema,
    OrderItemPreparationSchema,
    UnavailableItemSchema,
    ExtractedMedicineSchema,
    DrugSafetyAssessmentSchema
)

logger = logging.getLogger(__name__)


class OrderAgent:
    """
    Agent 4: Order Agent
    Prepares Cart and READY_TO_PLACE order draft based on extracted medicines,
    patient selection, safety screening output, and live inventory.
    """
    AGENT_ID = "order_agent"
    VERSION = "2.0.0"

    def __init__(self, db: Session):
        self.db = db

    async def execute(
        self,
        prescription_id: int,
        patient_id: int,
        extracted_medicines: List[ExtractedMedicineSchema],
        safety_assessment: DrugSafetyAssessmentSchema,
        pharmacy_id: int = 1,
        patient_selection: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None
    ) -> OrderPreparationSchema:
        """
        Executes order preparation and draft order generation.
        """
        start_time = time.perf_counter()

        # Step 1: Safety Gate Enforcement
        if not safety_assessment.can_proceed and not safety_assessment.pharmacist_cleared:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return OrderPreparationSchema(
                prescription_id=prescription_id,
                patient_id=patient_id,
                pharmacy_id=pharmacy_id,
                order_status="SAFETY_BLOCKED",
                safety_status=safety_assessment.safety_status,
                items=[],
                unavailable_items=[],
                subtotal=0.0,
                delivery_charge=0.0,
                discount=0.0,
                total_amount=0.0,
                next_action="AWAITING_CLINICAL_CLEARANCE",
                processing_time_ms=round(duration_ms, 2)
            )

        # Step 2: Check Idempotency (Prevent Duplicate Order Creation)
        derived_key = idempotency_key or f"rx_{prescription_id}_pat_{patient_id}_draft"
        existing_order = self.db.query(Order).filter(
            Order.prescription_id == prescription_id,
            Order.customer_id == patient_id,
            Order.order_status.in_(["READY_TO_PLACE", "DRAFT", "PENDING_PATIENT_CONFIRMATION"])
        ).first()

        if existing_order:
            # Reconstitute items from existing order
            items = []
            for oi in existing_order.items:
                med = oi.medicine
                items.append(OrderItemPreparationSchema(
                    medicine_id=oi.medicine_id,
                    medicine_name=med.brand_name if med else "Medicine",
                    generic_name=med.generic_name if med else None,
                    strength=med.strength if med else None,
                    prescribed_quantity=oi.quantity,
                    ordered_quantity=oi.quantity,
                    unit_price=float(oi.unit_price),
                    subtotal=float(oi.total_price),
                    is_available=True,
                    available_stock=oi.quantity
                ))
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return OrderPreparationSchema(
                draft_order_id=existing_order.id,
                order_number=existing_order.order_number,
                cart_id=existing_order.cart_id,
                prescription_id=prescription_id,
                patient_id=patient_id,
                pharmacy_id=pharmacy_id,
                order_status="READY_TO_PLACE",
                safety_status=safety_assessment.safety_status,
                items=items,
                unavailable_items=[],
                subtotal=float(existing_order.total_amount),
                delivery_charge=0.0,
                discount=0.0,
                total_amount=float(existing_order.total_amount),
                next_action="PATIENT_CONFIRMATION_REQUIRED",
                processing_time_ms=round(duration_ms, 2)
            )

        # Step 3: Determine Orderable Medicines & Apply Patient Selection
        selected_medicines: List[ExtractedMedicineSchema] = []
        patient_qty_map: Dict[int, int] = {}

        # Parse patient selection if provided
        selected_med_ids: Optional[List[int]] = None
        if patient_selection:
            # May be {"selected_ids": [1, 2], "quantities": {1: 10}}
            if "selected_ids" in patient_selection:
                selected_med_ids = [int(i) for i in patient_selection["selected_ids"]]
            if "quantities" in patient_selection:
                patient_qty_map = {int(k): int(v) for k, v in patient_selection["quantities"].items()}

        for med in extracted_medicines:
            if not med.catalogue_match:
                continue

            med_id = med.catalogue_match.medicine_id
            if selected_med_ids is not None and med_id not in selected_med_ids:
                # Patient explicitly excluded this medicine
                continue

            selected_medicines.append(med)

        # Step 4: Inventory & Stock Check against pharmacy_inventory
        available_order_items: List[OrderItemPreparationSchema] = []
        unavailable_items: List[UnavailableItemSchema] = []
        subtotal = 0.0

        for med in selected_medicines:
            match = med.catalogue_match
            med_id = match.medicine_id

            # Determine requested quantity: cannot exceed prescribed quantity
            prescribed_qty = med.quantity or 10
            requested_qty = patient_qty_map.get(med_id, prescribed_qty)
            requested_qty = min(requested_qty, prescribed_qty)  # Strictly enforce upper bound

            # Check inventory
            inv = self.db.query(PharmacyInventory).filter(
                PharmacyInventory.pharmacy_id == pharmacy_id,
                PharmacyInventory.medicine_id == med_id
            ).first()

            current_stock = inv.stock_quantity if inv else 0
            unit_price = float(inv.selling_price) if inv and inv.selling_price else match.unit_price

            if current_stock >= requested_qty:
                # Fully available
                line_total = round(requested_qty * unit_price, 2)
                subtotal += line_total
                available_order_items.append(OrderItemPreparationSchema(
                    medicine_id=med_id,
                    medicine_name=match.brand_name,
                    generic_name=match.generic_name,
                    strength=match.strength,
                    prescribed_quantity=prescribed_qty,
                    ordered_quantity=requested_qty,
                    unit_price=unit_price,
                    subtotal=line_total,
                    is_available=True,
                    available_stock=current_stock
                ))
            elif current_stock > 0:
                # Partial stock available
                line_total = round(current_stock * unit_price, 2)
                subtotal += line_total
                available_order_items.append(OrderItemPreparationSchema(
                    medicine_id=med_id,
                    medicine_name=match.brand_name,
                    generic_name=match.generic_name,
                    strength=match.strength,
                    prescribed_quantity=prescribed_qty,
                    ordered_quantity=current_stock,
                    unit_price=unit_price,
                    subtotal=line_total,
                    is_available=True,
                    available_stock=current_stock
                ))
                unavailable_items.append(UnavailableItemSchema(
                    medicine_id=med_id,
                    medicine_name=match.brand_name,
                    requested_quantity=requested_qty,
                    available_quantity=current_stock,
                    reason=f"Partial stock only: {current_stock} of {requested_qty} available.",
                    can_fulfill_partially=True
                ))
            else:
                # Completely out of stock
                unavailable_items.append(UnavailableItemSchema(
                    medicine_id=med_id,
                    medicine_name=match.brand_name,
                    requested_quantity=requested_qty,
                    available_quantity=0,
                    reason="Medicine is currently out of stock at this pharmacy.",
                    can_fulfill_partially=False
                ))

        # Decimal-safe pricing
        delivery_charge = 40.0 if (subtotal < 500.0 and subtotal > 0.0) else 0.0
        discount = 0.0
        total_amount = round(subtotal + delivery_charge - discount, 2)

        # Step 5: Create or Update Patient's Cart
        cart = self.db.query(Cart).filter(
            Cart.customer_id == patient_id,
            Cart.pharmacy_id == pharmacy_id,
            Cart.status == "ACTIVE"
        ).first()

        if not cart:
            cart = Cart(
                customer_id=patient_id,
                pharmacy_id=pharmacy_id,
                status="ACTIVE",
                subtotal=subtotal,
                discount=discount,
                delivery_fee=delivery_charge,
                total_amount=total_amount
            )
            self.db.add(cart)
            self.db.commit()
            self.db.refresh(cart)
        else:
            # Clear old draft items in active cart
            self.db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            cart.subtotal = subtotal
            cart.delivery_fee = delivery_charge
            cart.total_amount = total_amount
            self.db.commit()

        # Add CartItems
        for item in available_order_items:
            cart_item = CartItem(
                cart_id=cart.id,
                medicine_id=item.medicine_id,
                quantity=item.ordered_quantity,
                unit_price=item.unit_price,
                total_price=item.subtotal,
                source="PRESCRIPTION"
            )
            self.db.add(cart_item)
        self.db.commit()

        # Step 6: Create READY_TO_PLACE Draft Order
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        draft_order = Order(
            order_number=order_number,
            customer_id=patient_id,
            pharmacy_id=pharmacy_id,
            cart_id=cart.id,
            prescription_id=prescription_id,
            order_status="READY_TO_PLACE",
            payment_method="CASH_ON_DELIVERY",
            payment_status="PENDING",
            total_amount=total_amount,
            idempotency_key=derived_key,
            placed_at=datetime.now(timezone.utc)
        )
        self.db.add(draft_order)
        self.db.commit()
        self.db.refresh(draft_order)

        # Add OrderItems with unit price snapshot
        for item in available_order_items:
            order_item = OrderItem(
                order_id=draft_order.id,
                medicine_id=item.medicine_id,
                quantity=item.ordered_quantity,
                unit_price=item.unit_price,
                total_price=item.subtotal
            )
            self.db.add(order_item)
        self.db.commit()

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return OrderPreparationSchema(
            draft_order_id=draft_order.id,
            order_number=draft_order.order_number,
            cart_id=cart.id,
            prescription_id=prescription_id,
            patient_id=patient_id,
            pharmacy_id=pharmacy_id,
            order_status="READY_TO_PLACE",
            safety_status=safety_assessment.safety_status,
            items=available_order_items,
            unavailable_items=unavailable_items,
            subtotal=subtotal,
            delivery_charge=delivery_charge,
            discount=discount,
            total_amount=total_amount,
            next_action="PATIENT_CONFIRMATION_REQUIRED",
            processing_time_ms=round(duration_ms, 2),
            created_at=draft_order.placed_at
        )
