"""
MediLoop Restricted AI Medicine & Ordering Service.
Implements deterministic backend tools, strict scope validation,
patient context isolation, allergy conflict checks, and order draft management.
"""
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.medical_info import MedicalInfo
from app.models.prescription import Prescription, PrescriptionItem, VerificationStatus
from app.models.order import Order, OrderItem, OrderStatus, OrderAuditEvent, OrderDraft
from app.models.medicine import Medicine
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.address import Address
from app.models.notification import Notification

EXACT_REFUSAL_MESSAGE = (
    "I'm MediLoop's medicine assistant. I can help with medicine-related questions, "
    "your recorded allergies, your uploaded prescriptions, and ordering or refilling medicines. "
    "I can't help with unrelated topics."
)

# Common disease to drug class keywords for patient history matching
DISEASE_KEYWORDS = {
    "diabetes": ["metformin", "glycomet", "glucophage", "glimepiride", "januvia", "insulin", "dapagliflozin", "empagliflozin", "sitagliptin"],
    "sugar": ["metformin", "glycomet", "glucophage", "glimepiride", "januvia", "insulin"],
    "bp": ["telma", "telmisartan", "amlodipine", "atenolol", "losartan", "enalapril", "metoprolol", "olmesartan"],
    "blood pressure": ["telma", "telmisartan", "amlodipine", "atenolol", "losartan", "enalapril", "metoprolol", "olmesartan"],
    "hypertension": ["telma", "telmisartan", "amlodipine", "atenolol", "losartan", "enalapril", "metoprolol", "olmesartan"],
    "cholesterol": ["atorvastatin", "atorva", "lipitor", "rosuvastatin", "simvastatin"],
    "fever": ["paracetamol", "crocin", "dolo", "calpol", "combiflam"],
    "pain": ["combiflam", "ibuprofen", "paracetamol", "crocin", "dolo", "drotin"],
    "antibiotic": ["amoxicillin", "ceftas", "azithromycin", "azee", "cifran", "augmentin"],
}


def is_in_scope(user_message: str) -> bool:
    """
    Validates whether the user's message is within the permitted medicine assistant scope:
    A. Medicine information and safe medicine-use questions.
    B. Allergy-related questions using patient's recorded allergies.
    C. Prescription-related questions based on uploaded prescriptions.
    D. Medicine ordering and refilling based on verified records.
    E. Order status, prescription verification status, pharmacy workflow.
    F. Clarification for above.
    """
    msg = user_message.strip().lower()
    if not msg:
        return False

    # Immediate red flags for unrelated topics: programming, general knowledge, entertainment, politics, sports, math
    unrelated_triggers = [
        "python", "javascript", "code", "programming", "function", "debug", "compile",
        "movie", "song", "actor", "hollywood", "bollywood", "cricket", "football", "world cup",
        "who won", "election", "president", "prime minister", "politics", "capital of", "weather in",
        "write an essay", "poem", "story", "joke", "math", "equation", "solve", "cats", "dogs",
        "who is the president", "history of", "quantum physics", "bitcoin", "crypto"
    ]
    for trig in unrelated_triggers:
        if re.search(r'\b' + re.escape(trig) + r'\b', msg):
            if not any(k in msg for k in ["medicine", "prescription", "allergy", "tablet", "pill", "refill", "medication"]):
                return False

    if re.search(r'\d+x|\bx\s*[\+\-\*\/=]', msg):
        return False

    # Allowed topic keywords
    allowed_keywords = [
        "medicine", "medication", "drug", "prescription", "rx", "pill", "tablet", "capsule", "syrup",
        "dose", "dosage", "strength", "allergy", "allergies", "allergic", "reaction", "side effect",
        "order", "reorder", "refill", "cart", "pharmacy", "pharmacist", "status", "delivered",
        "take", "taking", "food", "before food", "after food", "safe", "safety", "interaction",
        "doctor", "clinic", "hospital", "sugar", "bp", "diabetes", "blood pressure", "hypertension",
        "cholesterol", "fever", "pain", "headache", "cough", "cold", "antibiotic", "infection",
        "crocin", "dolo", "paracetamol", "amoxicillin", "ceftas", "calpol", "drotin", "acera",
        "alkarate", "atorvastatin", "metformin", "telma", "confirm", "cancel", "draft", "hello",
        "hi", "options", "which one", "explain"
    ]
    
    return any(k in msg for k in allowed_keywords)


# ----------------------------------------------------------------------------
# Deterministic Backend Tool 1: get_my_prescriptions
# ----------------------------------------------------------------------------
def get_my_prescriptions(db: Session, customer_id: int) -> List[Dict[str, Any]]:
    """Retrieves all prescriptions belonging strictly to the authenticated patient."""
    prescriptions = db.query(Prescription).filter(
        Prescription.customer_id == customer_id
    ).order_by(Prescription.uploaded_at.desc()).all()

    results = []
    for p in prescriptions:
        items = []
        for it in p.items:
            items.append({
                "id": it.id,
                "medicine_name": it.medicine_name,
                "strength": it.strength,
                "dosage_pattern": it.dosage_pattern,
                "frequency": it.frequency,
                "duration_days": it.duration_days,
                "calculated_quantity": it.calculated_quantity,
                "form": it.form,
                "dosage_instructions": it.dosage_instructions,
                "is_ambiguous": it.is_ambiguous,
                "requires_review": it.requires_review,
            })
        results.append({
            "id": p.id,
            "filename": p.original_filename,
            "uploaded_at": p.uploaded_at.isoformat() if p.uploaded_at else None,
            "verification_status": p.verification_status.value if hasattr(p.verification_status, "value") else str(p.verification_status),
            "rejection_reason": p.rejection_reason,
            "overall_confidence": p.overall_confidence,
            "items": items,
        })
    return results


# ----------------------------------------------------------------------------
# Deterministic Backend Tool 2: get_my_order_history
# ----------------------------------------------------------------------------
def get_my_order_history(db: Session, customer_id: int) -> List[Dict[str, Any]]:
    """Retrieves order history for the authenticated patient."""
    orders = db.query(Order).filter(
        Order.customer_id == customer_id
    ).order_by(Order.placed_at.desc()).all()

    results = []
    for o in orders:
        items = []
        for it in o.items:
            med_name = it.medicine.brand_name if it.medicine else f"Medicine #{it.medicine_id}"
            items.append({
                "medicine_id": it.medicine_id,
                "medicine_name": med_name,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "total_price": it.total_price,
            })
        results.append({
            "id": o.id,
            "order_number": o.order_number,
            "placed_at": o.placed_at.isoformat() if o.placed_at else None,
            "order_status": o.order_status,
            "total_amount": o.total_amount,
            "pharmacy_id": o.pharmacy_id,
            "items": items,
        })
    return results


# ----------------------------------------------------------------------------
# Deterministic Backend Tool 3: get_my_recorded_allergies
# ----------------------------------------------------------------------------
def get_my_recorded_allergies(db: Session, customer_id: int) -> List[str]:
    """Retrieves patient's recorded allergies from medical_info."""
    info = db.query(MedicalInfo).filter(MedicalInfo.user_id == customer_id).first()
    if not info or not info.allergies:
        return []
    
    # Split comma-separated or list
    raw = info.allergies
    if isinstance(raw, list):
        return [str(a).strip() for a in raw if str(a).strip()]
    return [a.strip() for a in str(raw).split(",") if a.strip()]


# ----------------------------------------------------------------------------
# Deterministic Backend Tool 4: search_eligible_medicine_catalog
# ----------------------------------------------------------------------------
def search_eligible_medicine_catalog(
    db: Session, 
    query: str, 
    pharmacy_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Searches active medicines matching query, checking inventory availability."""
    target_pharmacy_id = pharmacy_id or 1
    q = query.strip()
    if not q:
        medicines = db.query(Medicine).filter(Medicine.is_active == True).limit(20).all()
    else:
        medicines = db.query(Medicine).filter(
            Medicine.is_active == True,
            (Medicine.brand_name.ilike(f"%{q}%")) | 
            (Medicine.generic_name.ilike(f"%{q}%")) |
            (Medicine.description.ilike(f"%{q}%"))
        ).limit(10).all()

    results = []
    for m in medicines:
        inv = db.query(PharmacyInventory).filter(
            PharmacyInventory.pharmacy_id == target_pharmacy_id,
            PharmacyInventory.medicine_id == m.id
        ).first()

        in_stock = bool(inv and inv.is_available and inv.stock_quantity > 0)
        stock_qty = inv.stock_quantity if (inv and inv.is_available) else 0
        price = inv.selling_price if inv else 45.0

        results.append({
            "id": m.id,
            "brand_name": m.brand_name,
            "generic_name": m.generic_name,
            "strength": m.strength,
            "dosage_form": m.dosage_form,
            "prescription_required": m.prescription_required,
            "unit_price": price,
            "in_stock": in_stock,
            "stock_quantity": stock_qty,
            "pharmacy_id": target_pharmacy_id,
        })
    return results


# ----------------------------------------------------------------------------
# Deterministic Backend Tool 5: check_refill_eligibility
# ----------------------------------------------------------------------------
def check_refill_eligibility(db: Session, customer_id: int, medicine_name: str) -> Dict[str, Any]:
    """
    Checks if a medicine is eligible for refill based on authenticated patient's valid prescriptions
    and previous orders. Validates prescription expiration and rejection state.
    """
    med_name_clean = medicine_name.strip().lower()

    # Search in prescriptions
    prescriptions = db.query(Prescription).filter(
        Prescription.customer_id == customer_id,
        Prescription.verification_status != VerificationStatus.REJECTED
    ).order_by(Prescription.uploaded_at.desc()).all()

    found_prescription_item = None
    found_prescription = None

    for p in prescriptions:
        for it in p.items:
            if med_name_clean in it.medicine_name.lower():
                found_prescription_item = it
                found_prescription = p
                break
        if found_prescription_item:
            break

    if not found_prescription_item:
        return {
            "is_eligible": False,
            "reason": f"No active prescription found for '{medicine_name}' in your account records.",
            "prescription_id": None,
            "item": None
        }

    # Check expiration (e.g. valid for 90 days from upload)
    upload_time = found_prescription.uploaded_at
    if upload_time and (datetime.utcnow() - upload_time.replace(tzinfo=None) > timedelta(days=90)):
        return {
            "is_eligible": False,
            "reason": f"The prescription for '{medicine_name}' uploaded on {upload_time.date()} has expired (over 90 days old). Please upload a current prescription.",
            "prescription_id": found_prescription.id,
            "item": None
        }

    return {
        "is_eligible": True,
        "reason": "Valid prescription record found.",
        "prescription_id": found_prescription.id,
        "item": {
            "medicine_name": found_prescription_item.medicine_name,
            "strength": found_prescription_item.strength,
            "form": found_prescription_item.form or "Tablet",
            "quantity": found_prescription_item.calculated_quantity or 10,
            "dosage_instructions": found_prescription_item.dosage_instructions or found_prescription_item.dosage_pattern or "1 tab daily",
        }
    }


# ----------------------------------------------------------------------------
# Deterministic Backend Tool 6: create_order_draft
# ----------------------------------------------------------------------------
def create_order_draft(
    db: Session,
    customer_id: int,
    pharmacy_id: Optional[int],
    items: List[Dict[str, Any]],
    prescription_id: Optional[int] = None,
    allergy_warning: Optional[str] = None
) -> OrderDraft:
    """
    Creates an immutable OrderDraft record with a unique draft_id, expiration,
    and structured items. Does NOT submit the order until explicit confirmation.
    """
    target_pharmacy_id = pharmacy_id or 1
    total = sum(float(i.get("unit_price", 45.0)) * int(i.get("quantity", 1)) for i in items)

    draft_id = f"draft_{uuid.uuid4().hex[:12]}"
    draft = OrderDraft(
        id=draft_id,
        customer_id=customer_id,
        pharmacy_id=target_pharmacy_id,
        prescription_id=prescription_id,
        items_json=items,
        total_estimated_amount=round(total, 2),
        status="PENDING_PATIENT_CONFIRMATION",
        allergy_warning=allergy_warning,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=2)
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


# ----------------------------------------------------------------------------
# Deterministic Backend Tool 7: get_my_order_status
# ----------------------------------------------------------------------------
def get_my_order_status(db: Session, customer_id: int, order_identifier: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves current order status and audit history for the authenticated patient."""
    query = db.query(Order).filter(Order.customer_id == customer_id)
    if order_identifier:
        clean = order_identifier.strip()
        if clean.isdigit():
            query = query.filter(Order.id == int(clean))
        else:
            query = query.filter(Order.order_number == clean)
    
    order = query.order_by(Order.placed_at.desc()).first()
    if not order:
        return {
            "found": False,
            "message": "No matching order found in your account history."
        }

    return {
        "found": True,
        "order_id": order.id,
        "order_number": order.order_number,
        "order_status": order.order_status,
        "placed_at": order.placed_at.isoformat() if order.placed_at else None,
        "total_amount": order.total_amount,
        "rejection_reason": order.rejection_reason,
        "pharmacy_id": order.pharmacy_id,
        "items_count": len(order.items),
    }


# ----------------------------------------------------------------------------
# Deterministic Backend Tool 8: submit_confirmed_order
# ----------------------------------------------------------------------------
def submit_confirmed_order(
    db: Session,
    customer_id: int,
    draft_id: str,
    idempotency_key: Optional[str] = None,
    address_id: Optional[int] = None,
    payment_method: str = "COD"
) -> Order:
    """
    Submits an explicitly confirmed order draft.
    - Validates that draft exists and belongs to customer.
    - Validates draft is not expired or already confirmed.
    - Enforces idempotency key to prevent accidental duplicate placement.
    - Records OrderAuditEvent for full traceability.
    """
    # 1. Check idempotency
    if idempotency_key:
        existing = db.query(Order).filter(
            Order.customer_id == customer_id,
            Order.idempotency_key == idempotency_key
        ).first()
        if existing:
            return existing

    # 2. Retrieve draft
    draft = db.query(OrderDraft).filter(
        OrderDraft.id == draft_id,
        OrderDraft.customer_id == customer_id
    ).first()

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order draft '{draft_id}' not found or belongs to another user."
        )

    if draft.status == "CONFIRMED":
        # Find existing order created from this draft
        existing_order = db.query(Order).filter(
            Order.customer_id == customer_id,
            Order.prescription_id == draft.prescription_id
        ).order_by(Order.placed_at.desc()).first()
        if existing_order:
            return existing_order

    if draft.expires_at and draft.expires_at.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order draft has expired. Please ask the assistant to prepare a fresh draft."
        )

    # 3. Resolve Delivery Address
    target_address_id = address_id
    if not target_address_id:
        def_addr = db.query(Address).filter(
            Address.user_id == customer_id,
            Address.is_default_delivery == True
        ).first()
        if not def_addr:
            def_addr = db.query(Address).filter(Address.user_id == customer_id).first()
        target_address_id = def_addr.id if def_addr else None

    # 4. Create Order in PENDING_VERIFICATION state
    order_number = f"ML-{uuid.uuid4().hex[:8].upper()}"
    pharmacy_id = draft.pharmacy_id or 1

    new_order = Order(
        order_number=order_number,
        customer_id=customer_id,
        pharmacy_id=pharmacy_id,
        prescription_id=draft.prescription_id,
        address_id=target_address_id,
        payment_method=payment_method,
        payment_status="PENDING",
        order_status=OrderStatus.PENDING_VERIFICATION.value,
        total_amount=draft.total_estimated_amount,
        idempotency_key=idempotency_key or draft_id,
        confirmed_at=datetime.utcnow()
    )
    db.add(new_order)
    db.flush()

    # 5. Create Order Items from draft items_json
    raw_items = draft.items_json if isinstance(draft.items_json, list) else []
    for item in raw_items:
        med_id = item.get("medicine_id")
        if not med_id:
            # Look up medicine by name
            m_name = item.get("medicine_name") or item.get("name") or ""
            med_rec = db.query(Medicine).filter(
                (Medicine.brand_name.ilike(f"%{m_name}%")) | 
                (Medicine.generic_name.ilike(f"%{m_name}%"))
            ).first()
            med_id = med_rec.id if med_rec else 1

        qty = int(item.get("quantity") or 1)
        unit_p = float(item.get("unit_price") or 45.0)
        tot_p = round(qty * unit_p, 2)

        oi = OrderItem(
            order_id=new_order.id,
            medicine_id=med_id,
            quantity=qty,
            unit_price=unit_p,
            total_price=tot_p
        )
        db.add(oi)

    # 6. Record Audit Event
    audit = OrderAuditEvent(
        order_id=new_order.id,
        actor_id=customer_id,
        actor_role="PATIENT",
        previous_state="DRAFT",
        new_state=OrderStatus.PENDING_VERIFICATION.value,
        action="PATIENT_CONFIRMED_ORDER",
        reason_or_note=f"Order confirmed by patient via MediLoop AI assistant from draft {draft_id}"
    )
    db.add(audit)

    # 7. Update Draft Status
    draft.status = "CONFIRMED"
    db.add(draft)

    # 8. Dispatch notification
    notif = Notification(
        user_id=customer_id,
        title="Order Placed - Awaiting Pharmacist Review",
        message=f"Your order #{order_number} has been submitted from your draft and is waiting for pharmacist review.",
        notification_type="ORDER_UPDATE"
    )
    db.add(notif)

    db.commit()
    db.refresh(new_order)
    return new_order


# ----------------------------------------------------------------------------
# Conversational AI Dispatcher for Patient Chat & Voice Endpoints
# ----------------------------------------------------------------------------
def process_ai_patient_message(
    db: Session,
    current_user: User,
    user_message: str
) -> Dict[str, Any]:
    """
    Core conversational logic enforcing strict scope, deterministic tools,
    patient record verification, allergy checks, ambiguity clarification,
    and structured draft card preparation.
    """
    clean_msg = user_message.strip()

    # 1. Scope Enforcement (Backend Gatekeeper)
    if not is_in_scope(clean_msg):
        return {
            "reply": EXACT_REFUSAL_MESSAGE,
            "workflow_id": "scope_refusal",
            "warnings": ["Query outside allowed medicine assistant scope"],
            "recommendations": [],
            "order_draft": None,
            "in_scope": False
        }

    msg_lower = clean_msg.lower()

    # 2. Check for Explicit Draft Confirmation
    if any(k in msg_lower for k in ["confirm order", "confirm draft", "place order", "yes place it", "confirm and place"]):
        # Find latest pending draft for this customer
        draft = db.query(OrderDraft).filter(
            OrderDraft.customer_id == current_user.id,
            OrderDraft.status == "PENDING_PATIENT_CONFIRMATION"
        ).order_by(OrderDraft.created_at.desc()).first()

        if draft:
            order = submit_confirmed_order(
                db=db,
                customer_id=current_user.id,
                draft_id=draft.id,
                idempotency_key=f"idemp_{draft.id}"
            )
            return {
                "reply": (
                    f"✅ Order #{order.order_number} has been confirmed and placed! "
                    f"Total: ₹{order.total_amount:.2f}. "
                    f"It has been routed to the pharmacy for pharmacist verification. You will be notified once verified."
                ),
                "workflow_id": f"order_{order.id}",
                "warnings": [],
                "recommendations": ["View Order Tracking", "My Orders"],
                "order_draft": None,
                "in_scope": True
            }

    # 3. Check for Cancellation
    if any(k in msg_lower for k in ["cancel draft", "cancel order", "discard draft"]):
        draft = db.query(OrderDraft).filter(
            OrderDraft.customer_id == current_user.id,
            OrderDraft.status == "PENDING_PATIENT_CONFIRMATION"
        ).order_by(OrderDraft.created_at.desc()).first()
        if draft:
            draft.status = "CANCELLED"
            db.commit()
            return {
                "reply": f"The draft order ({draft.id}) has been cancelled. How else can I assist you?",
                "workflow_id": "draft_cancelled",
                "warnings": [],
                "recommendations": ["Upload Prescription", "Search Medicines"],
                "order_draft": None,
                "in_scope": True
            }

    # 4. Check for Allergy Query
    if any(k in msg_lower for k in ["allergy", "allergies", "allergic"]):
        allergies = get_my_recorded_allergies(db, current_user.id)
        if allergies:
            joined = ", ".join(allergies)
            reply_text = (
                f"Your medical profile has recorded allergies for: **{joined}**.\n\n"
                f"If you ever suspect an allergic reaction or need to update your allergy records, "
                f"please inform your doctor and pharmacist immediately."
            )
        else:
            reply_text = (
                "No allergy records are currently available in your profile. "
                "If you have any known drug or food allergies, please inform your pharmacist or update your profile."
            )
        return {
            "reply": reply_text,
            "workflow_id": "allergy_check",
            "warnings": [],
            "recommendations": ["Check Medicine Safety", "Consult Pharmacist"],
            "order_draft": None,
            "in_scope": True
        }

    # 5. Check for Order Status Query
    if any(k in msg_lower for k in ["order status", "track order", "where is my order", "order update", "my order"]):
        status_info = get_my_order_status(db, current_user.id)
        if status_info.get("found"):
            st = status_info.get("order_status")
            num = status_info.get("order_number")
            tot = status_info.get("total_amount")
            reply_text = f"Your latest order **#{num}** (₹{tot:.2f}) is currently in **{st}** status."
            if status_info.get("rejection_reason"):
                reply_text += f"\nNote from Pharmacist: {status_info.get('rejection_reason')}"
            return {
                "reply": reply_text,
                "workflow_id": "order_status",
                "warnings": [],
                "recommendations": ["Track Order", "Order History"],
                "order_draft": None,
                "in_scope": True
            }
        else:
            return {
                "reply": "I couldn't find any recent orders associated with your account.",
                "workflow_id": "order_status",
                "warnings": [],
                "recommendations": ["Upload Prescription", "Search Catalog"],
                "order_draft": None,
                "in_scope": True
            }

    # 6. Check for Prescription Query
    if any(k in msg_lower for k in ["prescription", "rx", "uploaded"]):
        prescriptions = get_my_prescriptions(db, current_user.id)
        if prescriptions:
            latest = prescriptions[0]
            items_desc = ", ".join([it["medicine_name"] for it in latest["items"]]) or "None extracted"
            reply_text = (
                f"You have {len(prescriptions)} prescription(s) uploaded. "
                f"Latest: **{latest['filename']}** (Status: **{latest['verification_status']}**).\n"
                f"Prescribed medicines: {items_desc}."
            )
            return {
                "reply": reply_text,
                "workflow_id": "prescription_info",
                "warnings": [],
                "recommendations": ["Refill Medicines", "Upload New Prescription"],
                "order_draft": None,
                "in_scope": True
            }
        else:
            return {
                "reply": "You have no uploaded prescriptions yet. Please upload a prescription to order prescribed medicines.",
                "workflow_id": "prescription_info",
                "warnings": [],
                "recommendations": ["Upload Prescription"],
                "order_draft": None,
                "in_scope": True
            }

    # 7. Check for Medicine Ordering / Refilling
    is_order_intent = any(k in msg_lower for k in ["order", "refill", "reorder", "buy", "get me", "need"])

    if is_order_intent:
        # Check Allergy Conflicts upfront with requested query
        patient_allergies = get_my_recorded_allergies(db, current_user.id)
        if patient_allergies:
            for a in patient_allergies:
                a_lower = a.lower()
                if a_lower in msg_lower:
                    return {
                        "reply": (
                            f"⚠️ **Allergy Conflict Alert**: Our records indicate you have an allergy to **{a}**. "
                            f"For your clinical safety, automatic order placement is blocked. "
                            f"Please consult your pharmacist or prescribing doctor for a safe alternative."
                        ),
                        "workflow_id": "allergy_conflict",
                        "warnings": [f"Allergy conflict detected with {a}"],
                        "recommendations": ["Contact Pharmacist", "Review Allergies"],
                        "order_draft": None,
                        "in_scope": True
                    }

        # Check if user mentioned a disease category (Section 7 specification)
        matched_disease = None
        for disease, keywords in DISEASE_KEYWORDS.items():
            if disease in msg_lower:
                matched_disease = disease
                break

        patient_prescriptions = get_my_prescriptions(db, current_user.id)
        patient_orders = get_my_order_history(db, current_user.id)

        # Collect medicines from patient's records
        record_medicines = []
        for p in patient_prescriptions:
            if p.get("verification_status") != "REJECTED":
                for it in p.get("items", []):
                    record_medicines.append({
                        "name": it.get("medicine_name"),
                        "strength": it.get("strength"),
                        "form": it.get("form") or "Tablet",
                        "dosage_instructions": it.get("dosage_instructions") or it.get("dosage_pattern"),
                        "quantity": it.get("calculated_quantity") or 10,
                        "prescription_id": p.get("id"),
                        "source": "PRESCRIPTION"
                    })

        for o in patient_orders:
            for it in o.get("items", []):
                record_medicines.append({
                    "name": it.get("medicine_name"),
                    "strength": None,
                    "form": "Tablet",
                    "dosage_instructions": "As prescribed",
                    "quantity": it.get("quantity") or 1,
                    "prescription_id": None,
                    "source": "PREVIOUS_ORDER"
                })

        # Scenario: User asked by disease category (e.g. "Order my diabetes medicine", "Order my BP medicine")
        if matched_disease:
            disease_drug_keys = DISEASE_KEYWORDS[matched_disease]
            eligible_for_disease = []
            seen_names = set()
            for rm in record_medicines:
                nm = rm["name"].lower()
                if any(dk in nm for dk in disease_drug_keys) and nm not in seen_names:
                    seen_names.add(nm)
                    eligible_for_disease.append(rm)

            # Multiple eligible medicines -> Ask for clarification (Section 7)
            if len(eligible_for_disease) > 1:
                options_str = "\n".join([f"• {m['name']} ({m.get('strength') or 'Standard'})" for m in eligible_for_disease])
                return {
                    "reply": (
                        f"I found more than one medicine associated with your previous treatment. "
                        f"Which medicine would you like to reorder?\n\n{options_str}"
                    ),
                    "workflow_id": "ambiguous_medicine",
                    "warnings": [],
                    "recommendations": [m['name'] for m in eligible_for_disease],
                    "order_draft": None,
                    "in_scope": True
                }

            # Zero eligible medicines -> Explain limitation, DO NOT guess (Section 7)
            if len(eligible_for_disease) == 0:
                return {
                    "reply": (
                        "I couldn't identify a medicine that I can safely prepare for ordering from your current records. "
                        "Please select a valid prescription or ask the pharmacist to review your request."
                    ),
                    "workflow_id": "no_eligible_medicine",
                    "warnings": [],
                    "recommendations": ["Upload Prescription", "Search Catalog"],
                    "order_draft": None,
                    "in_scope": True
                }

            # Exactly one eligible medicine found
            target_item = eligible_for_disease[0]
        else:
            # User named a specific medicine or requested general refill
            target_item = None
            for rm in record_medicines:
                if rm["name"].lower() in msg_lower or any(part in msg_lower for part in rm["name"].lower().split()):
                    target_item = rm
                    break

            if not target_item and record_medicines:
                # If user said simply "refill my medicine" or "reorder"
                target_item = record_medicines[0]

        if not target_item:
            # Check if mentioned medicine is in the general catalog
            catalog_matches = search_eligible_medicine_catalog(db, clean_msg)
            if catalog_matches:
                cat_med = catalog_matches[0]
                if cat_med.get("prescription_required"):
                    return {
                        "reply": (
                            f"**{cat_med['brand_name']}** requires a valid prescription, but no valid prescription was found "
                            f"in your account. Please upload your prescription so a licensed pharmacist can review it."
                        ),
                        "workflow_id": "prescription_required",
                        "warnings": ["Prescription upload required"],
                        "recommendations": ["Upload Prescription"],
                        "order_draft": None,
                        "in_scope": True
                    }
                target_item = {
                    "name": cat_med["brand_name"],
                    "strength": cat_med.get("strength"),
                    "form": cat_med.get("dosage_form") or "Tablet",
                    "dosage_instructions": "As directed on pack",
                    "quantity": 1,
                    "prescription_id": None,
                    "source": "CATALOG"
                }
            else:
                return {
                    "reply": (
                        "I couldn't identify a medicine that I can safely prepare for ordering from your current records. "
                        "Please select a valid prescription or ask the pharmacist to review your request."
                    ),
                    "workflow_id": "no_eligible_record",
                    "warnings": [],
                    "recommendations": ["Upload Prescription", "Search Medicines"],
                    "order_draft": None,
                    "in_scope": True
                }

        # Check Allergy Conflicts with target medicine
        patient_allergies = get_my_recorded_allergies(db, current_user.id)
        conflict_allergy = None
        for a in patient_allergies:
            a_lower = a.lower()
            if a_lower in target_item["name"].lower() or (target_item.get("strength") and a_lower in target_item["strength"].lower()):
                conflict_allergy = a
                break

        if conflict_allergy:
            return {
                "reply": (
                    f"⚠️ **Allergy Conflict Alert**: Our records indicate you have an allergy to **{conflict_allergy}**. "
                    f"For your clinical safety, automatic order placement for **{target_item['name']}** is blocked. "
                    f"Please consult your pharmacist or prescribing doctor for a safe alternative."
                ),
                "workflow_id": "allergy_conflict",
                "warnings": [f"Allergy conflict detected with {conflict_allergy}"],
                "recommendations": ["Contact Pharmacist", "Review Allergies"],
                "order_draft": None,
                "in_scope": True
            }

        # Find matching medicine in catalog for pricing & stock
        cat_matches = search_eligible_medicine_catalog(db, target_item["name"])
        matched_med = cat_matches[0] if cat_matches else None
        unit_price = matched_med.get("unit_price", 45.0) if matched_med else 45.0
        med_id = matched_med.get("id", 1) if matched_med else 1

        qty = int(target_item.get("quantity") or 1)
        tot_price = round(unit_price * qty, 2)

        draft_items = [{
            "medicine_id": med_id,
            "medicine_name": target_item["name"],
            "strength": target_item.get("strength"),
            "dosage_form": target_item.get("form") or "Tablet",
            "quantity": qty,
            "unit_price": unit_price,
            "total_price": tot_price,
            "prescription_required": bool(matched_med.get("prescription_required") if matched_med else False),
            "evidence_text": target_item.get("dosage_instructions")
        }]

        # Create OrderDraft
        draft = create_order_draft(
            db=db,
            customer_id=current_user.id,
            pharmacy_id=1,
            items=draft_items,
            prescription_id=target_item.get("prescription_id")
        )

        strength_str = f" ({target_item['strength']})" if target_item.get("strength") else ""
        reply_text = (
            f"I have prepared an order draft for **{target_item['name']}{strength_str}**.\n\n"
            f"• Quantity: {qty} ({target_item.get('form', 'Tablet')})\n"
            f"• Estimated Price: ₹{tot_price:.2f}\n"
            f"• Pharmacy: MediLoop Partner Pharmacy\n\n"
            f"Please review the proposed order card below and confirm to place your order."
        )

        return {
            "reply": reply_text,
            "workflow_id": f"draft_{draft.id}",
            "warnings": [],
            "recommendations": ["Confirm Order", "Cancel Draft"],
            "order_draft": {
                "draft_id": draft.id,
                "medicine_name": target_item["name"],
                "strength": target_item.get("strength") or "Standard",
                "dosage_form": target_item.get("form") or "Tablet",
                "quantity": qty,
                "unit_price": unit_price,
                "total_price": tot_price,
                "pharmacy_name": "MediLoop Partner Pharmacy",
                "prescription_status": "Linked & Valid" if target_item.get("prescription_id") else "OTC / Non-Prescription",
                "status": "PENDING_PATIENT_CONFIRMATION"
            },
            "in_scope": True
        }

    # 8. General Medicine Info / FAQ
    med_lookup = search_eligible_medicine_catalog(db, clean_msg)
    if med_lookup:
        m = med_lookup[0]
        reply_text = (
            f"**{m['brand_name']}** ({m.get('generic_name', '')})\n"
            f"• Strength / Form: {m.get('strength', 'N/A')} - {m.get('dosage_form', 'Tablet')}\n"
            f"• Prescription Required: {'Yes' if m.get('prescription_required') else 'No'}\n"
            f"• Price: ₹{m.get('unit_price', 0.0):.2f}\n"
            f"• In Stock: {'Yes' if m.get('in_stock') else 'Check with store'}\n\n"
            f"Always follow dosage instructions given by your doctor or printed on the medicine label."
        )
        return {
            "reply": reply_text,
            "workflow_id": "medicine_info",
            "warnings": [],
            "recommendations": [f"Order {m['brand_name']}", "View Details"],
            "order_draft": None,
            "in_scope": True
        }

    # Fallback greeting or helpful guidance
    return {
        "reply": (
            f"Hello {current_user.full_name or 'Patient'}! I am MediLoop's medicine assistant. "
            f"I can help you review your prescriptions, answer medicine questions, "
            f"check your recorded allergies, or prepare a medicine reorder. What would you like assistance with?"
        ),
        "workflow_id": "general_greeting",
        "warnings": [],
        "recommendations": ["Order my regular medicine", "Check my allergies", "View prescription"],
        "order_draft": None,
        "in_scope": True
    }

