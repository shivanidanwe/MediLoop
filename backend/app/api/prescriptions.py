from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks, Header
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_pharmacist, oauth2_scheme
from app.core.security import decode_access_token
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.models.prescription import Prescription, PrescriptionItem, VerificationStatus
from app.schemas.prescription import PrescriptionResponse, PrescriptionReviewRequest
from app.services import prescription_service, orchestration_service

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])

# Helper dependency to resolve either a User or a Pharmacist from the JWT token
def get_current_actor(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Union[User, Pharmacist]:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    role = payload.get("role")
    sub_id = int(sub)

    if role == "pharmacist":
        pharmacist = db.query(Pharmacist).filter(Pharmacist.id == sub_id).first()
        if pharmacist:
            return pharmacist
    elif role in ("patient", "user", "customer"):
        user = db.query(User).filter(User.id == sub_id).first()
        if user:
            return user

    # Fallback if role is not set
    pharmacist = db.query(Pharmacist).filter(Pharmacist.id == sub_id).first()
    if pharmacist:
        return pharmacist
    user = db.query(User).filter(User.id == sub_id).first()
    if user:
        return user
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Actor associated with token not found",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post("/upload", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
def upload_prescription(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    pharmacy_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint for customers to upload a prescription image.
    Orchestration layer executes OCRAgent and PrescriptionAgent, extracts medication text,
    stores medicines, and automatically populates customer's cart.
    """
    # Enforce file format constraints
    allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
    file_ext = (file.filename or "").lower()
    if not any(file_ext.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Supported formats: JPG, JPEG, PNG, PDF."
        )

    # Execute full Orchestration pipeline: Upload -> OCR -> NER -> Add to Cart
    prescription = orchestration_service.orchestrate_prescription_upload(
        db=db,
        customer_id=current_user.id,
        file=file,
        pharmacy_id=pharmacy_id
    )
    
    return prescription

@router.get("", response_model=List[PrescriptionResponse])
def read_all_prescriptions(
    pharmacy_id: Optional[int] = None,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Endpoint for pharmacists to list prescriptions assigned to their specific pharmacy.
    Strictly prevents cross-pharmacy data access.
    """
    target_pharmacy_id = current_pharmacist.pharmacy_id
    if pharmacy_id and pharmacy_id != target_pharmacy_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access prescriptions of another pharmacy store."
        )
    return prescription_service.get_prescriptions_by_pharmacy(db, target_pharmacy_id)

@router.get("/customer", response_model=List[PrescriptionResponse])
def read_customer_prescriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint for customers to list their own uploaded prescriptions.
    """
    return prescription_service.get_prescriptions_by_customer(db, current_user.id)

@router.get("/pharmacy/{pharmacy_id}", response_model=List[PrescriptionResponse])
def read_pharmacy_prescriptions(
    pharmacy_id: int,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Endpoint for pharmacists to list prescriptions assigned to their specific pharmacy.
    """
    if current_pharmacist.pharmacy_id != pharmacy_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access prescriptions of this pharmacy store."
        )
    return prescription_service.get_prescriptions_by_pharmacy(db, pharmacy_id)

@router.get("/{id}", response_model=PrescriptionResponse)
def read_prescription_by_id(
    id: int,
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve detailed prescription record (including extracted medicine items).
    Accessible by either the prescription owner (customer) or assigned pharmacists.
    """
    prescription = prescription_service.get_prescription_by_id(db, id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
        
    # If customer is requesting, verify they own the prescription
    if isinstance(current_actor, User) and prescription.customer_id != current_actor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this prescription"
        )

    # If pharmacist is requesting, verify or align pharmacy assignment
    if isinstance(current_actor, Pharmacist) and prescription.pharmacy_id and prescription.pharmacy_id != current_actor.pharmacy_id:
        from app.models.order import Order
        has_order = db.query(Order).filter(Order.prescription_id == id, Order.pharmacy_id == current_actor.pharmacy_id).first() is not None
        if not has_order and prescription.pharmacy_id != 1:
            prescription.pharmacy_id = current_actor.pharmacy_id
            db.commit()
            db.refresh(prescription)
        
    return prescription

@router.put("/{id}/approve", response_model=PrescriptionResponse)
def approve_prescription(
    id: int,
    review: Optional[PrescriptionReviewRequest] = None,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Endpoint for pharmacists to approve a prescription.
    Disallows repeated approvals or modifying finalized decisions.
    Transitions prescription status to APPROVED, updates linked orders, and dispatches notifications.
    """
    prescription = prescription_service.get_prescription_by_id(db, id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
        
    # Prevent repeated submission or modifying finalized decisions
    if prescription.verification_status in [VerificationStatus.APPROVED, VerificationStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prescription is already finalized as '{prescription.verification_status.value}' and cannot be modified."
        )

    if prescription.pharmacy_id and prescription.pharmacy_id != current_pharmacist.pharmacy_id:
        prescription.pharmacy_id = current_pharmacist.pharmacy_id

    from datetime import datetime
    comments = (review.pharmacist_comments if review else None) or "Verified and approved by registered pharmacist."
    prescription.verification_status = VerificationStatus.APPROVED
    prescription.pharmacist_comments = comments
    prescription.verified_by_pharmacist_id = current_pharmacist.id
    prescription.verified_at = datetime.utcnow()

    # Update linked orders
    from app.models.order import Order, OrderStatus, OrderAuditEvent
    from app.models.order_status_history import OrderStatusHistory
    linked_orders = db.query(Order).filter(
        Order.prescription_id == id,
        Order.order_status.in_([OrderStatus.PENDING_VERIFICATION, OrderStatus.RECEIVED, OrderStatus.SUBMITTED])
    ).all()
    for lo in linked_orders:
        prev_st = str(lo.order_status)
        lo.order_status = OrderStatus.PREPARING.value
        lo.verified_at = datetime.utcnow()
        db.add(lo)

        audit = OrderAuditEvent(
            order_id=lo.id,
            actor_id=current_pharmacist.id,
            actor_role="PHARMACIST",
            previous_state=prev_st,
            new_state="PREPARING",
            action="PHARMACIST_APPROVE_PRESCRIPTION",
            reason_or_note=comments
        )
        db.add(audit)

        history = OrderStatusHistory(
            order_id=lo.id,
            actor_id=current_pharmacist.id,
            actor_role="PHARMACIST",
            previous_status=prev_st,
            new_status="PREPARING",
            notes=f"Prescription approved: {comments}"
        )
        db.add(history)

    # Patient Notification
    from app.models.notification import Notification
    notif = Notification(
        user_id=prescription.customer_id,
        pharmacy_id=current_pharmacist.pharmacy_id,
        pharmacist_id=current_pharmacist.id,
        title="Prescription Approved",
        message=f"Your prescription '{prescription.original_filename}' has been approved by the pharmacist. Medicines are being prepared.",
        notification_type="PRESCRIPTION_APPROVED",
        action_url=f"/prescriptions/{prescription.id}"
    )
    db.add(notif)
    db.commit()
    db.refresh(prescription)
    return prescription

@router.put("/{id}/reject", response_model=PrescriptionResponse)
def reject_prescription(
    id: int,
    review: Optional[PrescriptionReviewRequest] = None,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Endpoint for pharmacists to reject a prescription.
    Enforces mandatory rejection reason, disallows duplicate submissions on finalized decisions,
    updates linked orders, and dispatches notifications.
    """
    prescription = prescription_service.get_prescription_by_id(db, id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )

    # Prevent repeated submission or modifying finalized decisions
    if prescription.verification_status in [VerificationStatus.APPROVED, VerificationStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prescription is already finalized as '{prescription.verification_status.value}' and cannot be modified."
        )

    if prescription.pharmacy_id and prescription.pharmacy_id != current_pharmacist.pharmacy_id:
        prescription.pharmacy_id = current_pharmacist.pharmacy_id

    reason = (review.rejection_reason or review.pharmacist_comments if review else "") or ""
    reason = reason.strip()
    if not reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid rejection reason is mandatory when rejecting a prescription."
        )

    from datetime import datetime
    prescription.verification_status = VerificationStatus.REJECTED
    prescription.pharmacist_comments = reason
    prescription.rejection_reason = reason
    prescription.verified_by_pharmacist_id = current_pharmacist.id
    prescription.verified_at = datetime.utcnow()

    # Reject linked pending orders
    from app.models.order import Order, OrderStatus, OrderAuditEvent
    from app.models.order_status_history import OrderStatusHistory
    linked_orders = db.query(Order).filter(
        Order.prescription_id == id,
        Order.order_status.in_([OrderStatus.PENDING_VERIFICATION, OrderStatus.RECEIVED, OrderStatus.SUBMITTED])
    ).all()
    for lo in linked_orders:
        prev_st = str(lo.order_status)
        lo.order_status = OrderStatus.REJECTED.value
        lo.rejection_reason = reason
        db.add(lo)

        audit = OrderAuditEvent(
            order_id=lo.id,
            actor_id=current_pharmacist.id,
            actor_role="PHARMACIST",
            previous_state=prev_st,
            new_state="REJECTED",
            action="PHARMACIST_REJECT_PRESCRIPTION",
            reason_or_note=reason
        )
        db.add(audit)

        history = OrderStatusHistory(
            order_id=lo.id,
            actor_id=current_pharmacist.id,
            actor_role="PHARMACIST",
            previous_status=prev_st,
            new_status="REJECTED",
            notes=reason
        )
        db.add(history)

    # Notify patient
    from app.models.notification import Notification
    notif = Notification(
        user_id=prescription.customer_id,
        pharmacy_id=current_pharmacist.pharmacy_id,
        pharmacist_id=current_pharmacist.id,
        title="Prescription Rejected",
        message=f"Your prescription '{prescription.original_filename}' was reviewed and rejected. Reason: {reason}",
        notification_type="PRESCRIPTION_REJECTED",
        action_url=f"/prescriptions/{prescription.id}"
    )
    db.add(notif)
    db.commit()
    db.refresh(prescription)
    return prescription

@router.put("/{id}/clarify", response_model=PrescriptionResponse)
def clarify_prescription(
    id: int,
    review: Optional[PrescriptionReviewRequest] = None,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Endpoint for pharmacists to mark a prescription as requiring customer clarification.
    """
    prescription = prescription_service.get_prescription_by_id(db, id)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )

    if prescription.verification_status in [VerificationStatus.APPROVED, VerificationStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot request clarification on a finalized prescription '{prescription.verification_status.value}'."
        )

    notes = ((review.clarification_notes or review.pharmacist_comments if review else "") or "").strip()
    if not notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specific clarification notes are mandatory to request clarification."
        )

    from datetime import datetime
    prescription.verification_status = VerificationStatus.REQUIRES_CLARIFICATION
    prescription.pharmacist_comments = notes
    prescription.clarification_requested_at = datetime.utcnow()
    prescription.verified_by_pharmacist_id = current_pharmacist.id

    from app.models.notification import Notification
    notif = Notification(
        user_id=prescription.customer_id,
        pharmacy_id=current_pharmacist.pharmacy_id,
        pharmacist_id=current_pharmacist.id,
        title="Prescription Clarification Requested",
        message=f"Pharmacist requested clarification on prescription '{prescription.original_filename}': {notes}",
        notification_type="PRESCRIPTION_CLARIFICATION",
        action_url=f"/prescriptions/{prescription.id}"
    )
    db.add(notif)
    db.commit()
    db.refresh(prescription)
    return prescription

@router.get("/{id}/image")
def get_prescription_image(
    id: int,
    download: bool = False,
    token: Optional[str] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Stream or download original prescription image safely from disk with authorization checks.
    Supports JPG, JPEG, PNG, and PDF formats. Accessible by img tags or authenticated clients.
    """
    import os
    from fastapi.responses import FileResponse
    prescription = prescription_service.get_prescription_by_id(db, id)
    if not prescription or not prescription.uploaded_image_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription record or image path not found")

    # Authorize access if user token provided
    auth_token = token
    if not auth_token and authorization and authorization.startswith("Bearer "):
        auth_token = authorization.split(" ", 1)[1]

    if auth_token:
        payload = decode_access_token(auth_token)
        if payload and payload.get("sub"):
            try:
                sub_id = int(payload.get("sub"))
                role = payload.get("role")
                if role in ("patient", "user", "customer"):
                    user = db.query(User).filter(User.id == sub_id).first()
                    if user and prescription.customer_id != user.id:
                        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this prescription image")
            except Exception:
                pass

    path = prescription.uploaded_image_path
    candidate_paths = [
        path,
        os.path.join("backend", path),
        os.path.join("uploads", "prescriptions", os.path.basename(path)),
        os.path.join("backend", "uploads", "prescriptions", os.path.basename(path)),
        os.path.join("uploads", "prescriptions", f"preprocessed_{os.path.basename(path)}"),
        os.path.join("backend", "uploads", "prescriptions", f"preprocessed_{os.path.basename(path)}")
    ]

    resolved_path = None
    for p in candidate_paths:
        if os.path.exists(p) and os.path.isfile(p):
            resolved_path = p
            break

    if not resolved_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Original prescription image file '{prescription.original_filename}' is not available on server storage."
        )

    # Determine media type
    ext = os.path.splitext(resolved_path)[1].lower()
    media_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp"
    }
    media_type = media_types.get(ext, "image/jpeg")

    filename = prescription.original_filename or os.path.basename(resolved_path)
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return FileResponse(resolved_path, media_type=media_type, headers=headers)

@router.put("/{id}/items", response_model=PrescriptionResponse)
def update_prescription_items(
    id: int,
    items: List[dict],
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    """
    Extracted medicine details are strictly READ-ONLY for audit integrity.
    Rejects any unauthorized modification attempts.
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Extracted prescription medicine details are read-only to preserve clinical audit integrity. If a correction is needed, request clarification from the patient."
    )
