"""
MediLoop Backend Orchestration Layer.
Coordinates:
1. Prescription Upload -> OCR Agent -> Prescription Intelligence Agent -> Medicine Matching -> Add to Cart
2. Order Placement -> Pharmacy Stock Verification (Inventory Agent) -> Atomic Stock Reservation -> Pending Verification
3. Pharmacist Verification & Approval -> Update Order Status to 'Prescription Approved' + Patient Notifications
"""
import os
import re
import uuid
import logging
from datetime import datetime, date
from typing import Optional, Dict, Any, List, Tuple
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.models.prescription import Prescription, PrescriptionItem, VerificationStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import Cart, CartItem, CartStatus, CartItemSource
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.medicine import Medicine
from app.models.pharmacist import Pharmacist
from app.models.notification import Notification

from app.services import prescription_service, inventory_service, cart_service
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.factory import get_workflow_engine

logger = logging.getLogger(__name__)


# ============================================================================
# PHASE 1: Prescription Upload & Extraction Orchestration
# ============================================================================
def orchestrate_prescription_upload(
    db: Session,
    customer_id: int,
    file: UploadFile,
    pharmacy_id: Optional[int] = None
) -> Prescription:
    """
    1. Saves uploaded image safely.
    2. Runs OCRAgent to extract raw text.
    3. Runs PrescriptionIntelligenceAgent to extract structured medicines & dosages.
    4. Runs MedicineMatchingAgent to match catalog entries.
    5. Stores Prescription & PrescriptionItems.
    6. Automatically populates customer's active Cart with extracted medicines.
    """
    # 1. Save uploaded file on disk with security validation
    file_path = prescription_service.save_uploaded_file(file)

    # 2. Create Prescription database record
    db_prescription = Prescription(
        customer_id=customer_id,
        pharmacy_id=pharmacy_id or 1,
        uploaded_image_path=file_path,
        original_filename=file.filename or "prescription.png",
        verification_status=VerificationStatus.PROCESSING,
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)

    # 3. Execute Multi-Agent OCR & Extraction Pipeline
    try:
        abs_img_path = os.path.abspath(file_path) if not os.path.isabs(file_path) else file_path
        context = AgentContext(
            prescription_id=str(db_prescription.id),
            uploaded_image=abs_img_path
        )
        context.db = db
        context.metadata["prescription_id"] = db_prescription.id
        context.metadata["customer_id"] = customer_id
        context.metadata["image_path"] = abs_img_path
        context.metadata["file_path"] = abs_img_path

        engine = get_workflow_engine()
        
        # Execute workflow synchronously or via background engine
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                rec = pool.submit(asyncio.run, engine.execute_prescription_upload_workflow(context)).result()
        else:
            rec = loop.run_until_complete(engine.execute_prescription_upload_workflow(context))

        # Retrieve extracted results - prioritize clean structured output over raw OCR dump
        extracted_text = (
            rec.context.metadata.get("prescription_intelligence", {}).get("structured_summary")
            or rec.context.metadata.get("ocr", {}).get("extracted_text")
            or rec.context.ocr_text
            or "Extracted prescription details"
        )
        avg_confidence = (
            rec.context.metadata.get("prescription_intelligence", {}).get("average_confidence")
            or rec.context.metadata.get("ocr", {}).get("confidence_score") 
            or 0.95
        )
        matched_items = (
            rec.context.metadata.get("medicine_matching", {}).get("matched_medicines") 
            or rec.context.matched_medicines 
            or rec.context.extracted_medicines
            or []
        )

        unreadable_markers = [
            "image is too small", "image is too blurry", "blurry", "too small to read",
            "cannot read", "unable to read", "cannot be transcribed", "please provide a clearer",
            "clearer image", "i'd be happy to assist", "i would be happy to assist", "assist with ocr",
            "no readable text", "not readable", "unreadable", "low resolution"
        ]

        # 4. Save Valid Prescription Items
        valid_items_count = 0
        for item in matched_items:
            med_name = (item.get("medicine_name") or item.get("name") or item.get("matched_brand_name") or "").strip()
            # Skip invalid or conversational lines
            if not med_name or len(med_name) > 40 or len(med_name.split()) > 5:
                continue
            if any(marker in med_name.lower() for marker in unreadable_markers):
                continue
            # If item is unmatched in catalog, keep it for pharmacist review with review flag
            is_unmatched = (item.get("match_level") == "UNMATCHED") or not item.get("id")

            qty_val = str(item.get("quantity") or item.get("calculated_quantity") or "10").strip()
            qty = int(qty_val) if qty_val.isdigit() else 10

            freq_raw = str(item.get("frequency") or "").lower()
            if "3" in freq_raw or "thrice" in freq_raw or "tid" in freq_raw:
                freq_int = 3
            elif "4" in freq_raw or "qid" in freq_raw:
                freq_int = 4
            elif "1" in freq_raw or "once" in freq_raw or "od" in freq_raw:
                freq_int = 1
            else:
                freq_int = 2

            dosage_inst = item.get("dosage_instructions") or f"{item.get('dosage', '1 tab')} {item.get('frequency', '1-0-1')} {item.get('duration', '5 days')}".strip()
            raw_ev = item.get("raw_evidence_text") or med_name
            is_ambig = bool(item.get("is_ambiguous")) or (item.get("confidence") or 1.0) < 0.75 or not item.get("strength")

            db_item = PrescriptionItem(
                prescription_id=db_prescription.id,
                medicine_name=med_name,
                strength=item.get("strength"),
                dosage_pattern=item.get("dosage_pattern") or item.get("dosage") or "1-0-1",
                frequency=freq_int,
                duration_days=item.get("duration_days") or 5,
                calculated_quantity=qty,
                confidence_score=item.get("confidence") or avg_confidence,
                medicine_id=item.get("medicine_id") or item.get("id"),
                form=item.get("form"),
                dosage_instructions=dosage_inst,
                raw_evidence_text=raw_ev,
                is_ambiguous=is_ambig,
                requires_review=is_ambig,
            )
            db.add(db_item)
            valid_items_count += 1

        if "**Prescription Details:**" not in extracted_text:
            from app.agents.prescription_agent import format_exact_prescription_display
            entities = rec.context.metadata.get("prescription_intelligence", {}).get("clinical_entities") or {}
            extracted_text = format_exact_prescription_display(entities, matched_items)

        db_prescription.extracted_text = extracted_text
        db_prescription.overall_confidence = avg_confidence if valid_items_count > 0 else 0.0
        db_prescription.ocr_engine = "MedicalVisionOCRProvider"
        db_prescription.verification_status = VerificationStatus.PENDING_VERIFICATION
        db.commit()
        db.refresh(db_prescription)

        # 5. Automatically load extracted prescription medicines directly into Customer's Cart ONLY if valid medicines exist
        if valid_items_count > 0:
            add_prescription_medicines_to_cart(db, db_prescription.id)

    except Exception as e:
        logger.exception(f"Error in orchestration extraction pipeline for prescription {db_prescription.id}: {str(e)}")
        if not db_prescription.extracted_text:
            db_prescription.extracted_text = "Prescription image could not be transcribed automatically. Awaiting pharmacist review."
            db_prescription.verification_status = VerificationStatus.PENDING_VERIFICATION
            db_prescription.overall_confidence = 0.0
            db.commit()
            db.refresh(db_prescription)

    return db_prescription


def add_prescription_medicines_to_cart(db: Session, prescription_id: int) -> Cart:
    """
    Populates customer's active Cart with ONLY the medicines extracted from this prescription.
    Clears preexisting cart items so older, unrelated medicines do not pollute the prescription order.
    If an extracted medicine is unavailable in catalog or out of stock, records an explicit notification message.
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise ValueError(f"Prescription {prescription_id} not found.")

    pharmacy_id = prescription.pharmacy_id or 1
    cart = cart_service.get_or_create_active_cart(
        db, 
        customer_id=prescription.customer_id, 
        pharmacy_id=pharmacy_id
    )

    # 1. Clear preexisting cart items to prevent unrelated medicines from polluting the order
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

    if not prescription.items:
        logger.info(f"Prescription {prescription_id} has no valid items; cart cleared.")
        cart_service.recalculate_cart_totals(db, cart)
        db.commit()
        return cart

    unavailable_messages = []
    added_count = 0

    for item in prescription.items:
        raw_name = (item.medicine_name or "").strip()
        if not raw_name:
            continue

        raw_clean = re.sub(r'^(tab|cap|syp|inj|inhaler)\.?\s+', '', raw_name, flags=re.IGNORECASE).strip()
        raw_first_word = raw_clean.split()[0] if raw_clean else ""

        med = None
        if item.medicine_id:
            candidate = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
            if candidate and raw_first_word and (raw_first_word.lower() in candidate.brand_name.lower() or candidate.brand_name.lower().startswith(raw_first_word.lower())):
                med = candidate

        if not med and raw_first_word:
            # Try finding medicine by compatible brand name (never substitute with different brand)
            med = db.query(Medicine).filter(
                (Medicine.brand_name.ilike(raw_clean)) | 
                (Medicine.brand_name.ilike(f"{raw_first_word}%")) |
                (Medicine.brand_name.ilike(f"%{raw_first_word}%"))
            ).first()
            if med and (raw_first_word.lower() not in med.brand_name.lower() and not med.brand_name.lower().startswith(raw_first_word.lower())):
                med = None

        if not med:
            msg = f"Extracted medicine '{raw_name}' is not available in pharmacy inventory to add into cart."
            unavailable_messages.append(msg)
            logger.warning(msg)
            continue

        # Check stock in pharmacy inventory
        inv_item = db.query(PharmacyInventory).filter(
            PharmacyInventory.pharmacy_id == pharmacy_id,
            PharmacyInventory.medicine_id == med.id
        ).first()

        if not inv_item or (inv_item.stock_quantity or 0) <= 0:
            msg = f"Extracted medicine '{raw_name}' ({med.brand_name}) is currently out of stock at pharmacy to add into cart."
            unavailable_messages.append(msg)
            logger.warning(msg)
            continue

        unit_price = float(inv_item.selling_price if inv_item and inv_item.selling_price else 45.0)
        qty = item.calculated_quantity or 1

        cart_item = CartItem(
            cart_id=cart.id,
            medicine_id=med.id,
            quantity=qty,
            unit_price=unit_price,
            total_price=round(qty * unit_price, 2),
            source=CartItemSource.PRESCRIPTION
        )
        db.add(cart_item)
        added_count += 1

    if unavailable_messages:
        unavail_str = " | ".join(unavailable_messages)
        if prescription.pharmacist_comments:
            prescription.pharmacist_comments += f"\n[Stock Notice] {unavail_str}"
        else:
            prescription.pharmacist_comments = f"[Stock Notice] {unavail_str}"

    db.flush()
    cart_service.recalculate_cart_totals(db, cart)
    db.commit()
    db.refresh(cart)
    logger.info(f"Orchestration: Extracted prescription {prescription_id} medicines loaded to cart ID {cart.id} ({added_count} items added, {len(unavailable_messages)} unavailable)")
    return cart


# ============================================================================
# PHASE 2: Single-Click Order Placement with Stock Verification
# ============================================================================
def orchestrate_order_placement(
    db: Session,
    customer_id: int,
    pharmacy_id: int,
    address_id: int,
    payment_method: str,
    prescription_id: Optional[int] = None,
    items: Optional[List[Dict[str, Any]]] = None
) -> Order:
    """
    Single-click checkout orchestration:
    1. Fetches active cart for customer.
    2. Switches/verifies target pharmacy store.
    3. Runs Stock Verification for every medicine.
    4. IF stock is NOT available: Dispatches notification to user and raises 400.
    5. IF stock IS available: Atomically reserves stock, creates Order in PENDING_VERIFICATION state.
    """
    cart = db.query(Cart).filter(
        Cart.customer_id == customer_id,
        Cart.status == CartStatus.ACTIVE
    ).first()

    if not cart:
        cart = cart_service.get_or_create_active_cart(db, customer_id=customer_id, pharmacy_id=pharmacy_id)

    # Align cart with chosen pharmacy
    cart.pharmacy_id = pharmacy_id

    if items and len(items) > 0:
        # Sync cart with items passed from checkout client
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        for it in items:
            med_id = it.get("medicine_id") or it.get("id")
            if not med_id:
                continue
            qty = int(it.get("quantity") or 1)
            inv = db.query(PharmacyInventory).filter(
                PharmacyInventory.pharmacy_id == pharmacy_id,
                PharmacyInventory.medicine_id == med_id
            ).first()
            u_price = float(inv.selling_price) if inv and inv.selling_price else float(it.get("unit_price") or it.get("price") or 45.0)
            ci = CartItem(
                cart_id=cart.id,
                medicine_id=med_id,
                quantity=qty,
                unit_price=u_price,
                total_price=round(qty * u_price, 2),
                source=CartItemSource.PRESCRIPTION if prescription_id else CartItemSource.MANUAL_SEARCH
            )
            db.add(ci)
        db.flush()
        cart_service.recalculate_cart_totals(db, cart)
        db.commit()
        db.refresh(cart)
    elif not cart.items:
        # If cart is empty but prescription_id is provided, auto-load items from prescription first
        if prescription_id:
            cart = add_prescription_medicines_to_cart(db, prescription_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your cart is empty. Please add medicines or upload a prescription before ordering."
            )
    else:
        # Re-verify and ensure prices match pharmacy catalog
        for item in cart.items:
            inv = db.query(PharmacyInventory).filter(
                PharmacyInventory.pharmacy_id == pharmacy_id,
                PharmacyInventory.medicine_id == item.medicine_id
            ).first()
            if inv and inv.selling_price:
                item.unit_price = float(inv.selling_price)
                item.total_price = round(item.quantity * item.unit_price, 2)
        db.flush()
        cart_service.recalculate_cart_totals(db, cart)
        db.commit()
        db.refresh(cart)

    # Fetch Pharmacy Details
    pharmacy = db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()
    pharmacy_name = pharmacy.pharmacy_name if pharmacy else f"Pharmacy #{pharmacy_id}"

    # ---------------------------------------------------------
    # Orchestration Step: Stock Verification for Selected Pharmacy
    # ---------------------------------------------------------
    unavailable_medicines: List[Dict[str, Any]] = []

    for item in cart.items:
        inv_item = db.query(PharmacyInventory).filter(
            PharmacyInventory.pharmacy_id == pharmacy_id,
            PharmacyInventory.medicine_id == item.medicine_id
        ).first()

        med = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        med_name = med.brand_name if med else f"Medicine #{item.medicine_id}"

        if not inv_item or not inv_item.is_available or inv_item.stock_quantity < item.quantity:
            avail = inv_item.stock_quantity if (inv_item and inv_item.is_available) else 0
            unavailable_medicines.append({
                "medicine_id": item.medicine_id,
                "medicine_name": med_name,
                "requested_quantity": item.quantity,
                "available_stock": avail
            })
        elif inv_item.expiry_date and inv_item.expiry_date <= date.today():
            unavailable_medicines.append({
                "medicine_id": item.medicine_id,
                "medicine_name": med_name,
                "reason": "Batch expired",
                "requested_quantity": item.quantity,
                "available_stock": 0
            })

    # IF STOCK NOT AVAILABLE: Notify user and halt order placement
    if unavailable_medicines:
        unavail_names = ", ".join([m["medicine_name"] for m in unavailable_medicines])
        notif_msg = (
            f"Stock isn't available for: {unavail_names} at {pharmacy_name}. "
            f"Please choose another pharmacy branch or reduce item quantities."
        )

        # Dispatch real-time in-app notification to patient
        db_notif = Notification(
            user_id=customer_id,
            title="Medicine Stock Unavailable",
            message=notif_msg,
            notification_type="STOCK_ALERT"
        )
        db.add(db_notif)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "STOCK_UNAVAILABLE",
                "message": notif_msg,
                "pharmacy_id": pharmacy_id,
                "pharmacy_name": pharmacy_name,
                "unavailable_medicines": unavailable_medicines
            }
        )

    # ---------------------------------------------------------
    # IF STOCK IS AVAILABLE: Reserve Stock & Create Order Record
    # ---------------------------------------------------------
    try:
        # 1. Atomically reserve inventory stock
        for item in cart.items:
            inventory_service.reserve_stock(
                db, 
                pharmacy_id=pharmacy_id, 
                medicine_id=item.medicine_id, 
                quantity=item.quantity, 
                commit=False
            )

        # 2. Determine prescription linkage
        if not prescription_id:
            # Check if cart had items sourced from a prescription
            latest_rx = db.query(Prescription).filter(
                Prescription.customer_id == customer_id
            ).order_by(Prescription.uploaded_at.desc()).first()
            if latest_rx:
                prescription_id = latest_rx.id

        order_number = f"ML-{uuid.uuid4().hex[:8].upper()}"

        db_order = Order(
            order_number=order_number,
            customer_id=customer_id,
            pharmacy_id=pharmacy_id,
            cart_id=cart.id,
            prescription_id=prescription_id,
            address_id=address_id,
            payment_method=payment_method,
            payment_status="PAID" if payment_method.upper() in ["CARD", "UPI"] else "PENDING",
            order_status=OrderStatus.PENDING_VERIFICATION, # Awaiting pharmacist verification
            total_amount=cart.total_amount
        )
        db.add(db_order)
        db.flush()

        # 3. Create Order Items
        for item in cart.items:
            db_order_item = OrderItem(
                order_id=db_order.id,
                medicine_id=item.medicine_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )
            db.add(db_order_item)

        # 4. Mark Cart as Checked Out
        cart.status = CartStatus.CHECKED_OUT
        db.add(cart)

        # 5. Notify patient that order is placed & awaiting pharmacist verification
        db_notif = Notification(
            user_id=customer_id,
            title="Order Placed - Awaiting Pharmacist Review",
            message=(
                f"Your order #{order_number} has been placed successfully at {pharmacy_name}. "
                f"Prescribed medicines are secured. Waiting for pharmacist verification."
            ),
            notification_type="ORDER_UPDATE"
        )
        db.add(db_notif)

        db.commit()
        db.refresh(db_order)
        logger.info(f"Orchestration: Order #{order_number} created in PENDING_VERIFICATION state.")
        return db_order

    except Exception as e:
        db.rollback()
        logger.exception(f"Error creating order in orchestration layer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Order creation failed: {str(e)}"
        )


# ============================================================================
# PHASE 3: Pharmacist Verification & Status Update to 'Prescription Approved'
# ============================================================================
def orchestrate_pharmacist_approval(
    db: Session,
    prescription_id: int,
    pharmacist_id: int,
    comments: Optional[str] = None
) -> Tuple[Prescription, Optional[Order]]:
    """
    1. Pharmacist reviews uploaded image + OCR extracted text + extracted medicines.
    2. Pharmacist clicks approve.
    3. Updates prescription status to APPROVED.
    4. Updates associated Order status to 'Prescription Approved'.
    5. Dispatches real-time notification to patient.
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )

    # 1. Update Prescription verification status
    prescription.verification_status = VerificationStatus.APPROVED
    prescription.pharmacist_comments = comments or "Prescription verified and approved by licensed pharmacist."
    db.add(prescription)

    # 2. Find associated order(s) for this prescription
    order = db.query(Order).filter(
        (Order.prescription_id == prescription_id) |
        (
            (Order.customer_id == prescription.customer_id) & 
            (Order.order_status.in_([OrderStatus.PENDING_VERIFICATION, OrderStatus.RECEIVED]))
        )
    ).order_by(Order.placed_at.desc()).first()

    if order:
        # Update order status to exactly 'Prescription Approved'
        order.order_status = OrderStatus.PRESCRIPTION_APPROVED
        db.add(order)
        logger.info(f"Orchestration: Order #{order.order_number} status updated to '{OrderStatus.PRESCRIPTION_APPROVED.value}'.")

        # 3. Notify patient
        patient_notif = Notification(
            user_id=order.customer_id,
            title="Prescription Approved!",
            message=(
                f"Your prescription has been approved by the pharmacist. "
                f"Order #{order.order_number} is now 'Prescription Approved' and being prepared for dispatch."
            ),
            notification_type="PRESCRIPTION_APPROVED"
        )
        db.add(patient_notif)

    db.commit()
    db.refresh(prescription)
    if order:
        db.refresh(order)

    # 4. AI Orchestration Layer: Post-Verification Pharmacy Stock Availability Check
    # Check current inventory stock for the approved medicines at the assigned pharmacy.
    pharmacy_id = (order.pharmacy_id if order else None) or prescription.pharmacy_id or 1
    low_stock_medicines = []

    # Check medicines from prescription items or order items
    items_to_check = []
    if order and order.items:
        for oi in order.items:
            items_to_check.append({
                "medicine_id": oi.medicine_id,
                "medicine_name": oi.medicine.brand_name if oi.medicine else f"Medicine #{oi.medicine_id}",
                "unit_price": oi.unit_price or 50.0
            })
    elif prescription.items:
        for pi in prescription.items:
            items_to_check.append({
                "medicine_id": pi.medicine_id,
                "medicine_name": pi.medicine_name,
                "unit_price": 50.0
            })

    for item in items_to_check:
        med_id = item.get("medicine_id")
        if not med_id:
            continue
        inv_item = db.query(PharmacyInventory).filter(
            PharmacyInventory.pharmacy_id == pharmacy_id,
            PharmacyInventory.medicine_id == med_id
        ).first()

        current_stock = inv_item.stock_quantity if inv_item else 0
        threshold = 15  # Low-stock alert threshold
        if current_stock <= threshold:
            low_stock_medicines.append({
                "medicine_id": med_id,
                "medicine_name": item["medicine_name"],
                "current_stock": current_stock,
                "threshold": threshold,
                "unit_price": inv_item.selling_price if inv_item else item["unit_price"]
            })

    procurement_po = None
    if low_stock_medicines:
        # Generate alert message for pharmacist
        med_summary = ", ".join([f"{m['medicine_name']} ({m['current_stock']} left)" for m in low_stock_medicines])
        notif_msg = (
            f"AI Orchestration Alert: Stock for approved medicine(s) has over or is low: {med_summary}. "
            f"Autonomous Procurement Agent has generated Supplier Restock Invoice."
        )
        logger.warning(f"Orchestration Stock Alert for Pharmacy #{pharmacy_id}: {notif_msg}")

        # Send alert notification
        from app.models.user import User
        pharmacist_record = db.query(Pharmacist).filter(Pharmacist.id == pharmacist_id).first()
        ph_user = db.query(User).filter(User.email == pharmacist_record.email).first() if pharmacist_record else None
        target_uid = ph_user.id if ph_user else (order.customer_id if order else 1)
        p_notif = Notification(
            user_id=target_uid,
            title="Low Stock Alert - Procurement Invoice Ready",
            message=notif_msg,
            notification_type="LOW_STOCK_ALERT"
        )
        db.add(p_notif)

        # Trigger Autonomous Procurement Agent to generate ready-to-send Supplier Invoice
        from app.agents.procurement_agent import ProcurementAgent
        procurement_po = ProcurementAgent.generate_supplier_invoice(
            db=db,
            pharmacy_id=pharmacy_id,
            low_stock_items=low_stock_medicines,
            notes=f"Auto-generated for Order #{order.order_number if order else 'RX-' + str(prescription_id)} post-pharmacist approval."
        )
        db.commit()

    return prescription, order
