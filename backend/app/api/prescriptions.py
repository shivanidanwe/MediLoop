from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_pharmacist, oauth2_scheme
from app.core.security import decode_access_token
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.schemas.prescription import PrescriptionResponse, PrescriptionReviewRequest
from app.services import prescription_service

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
    
    # Try finding in User database
    user = db.query(User).filter(User.id == int(sub)).first()
    if user:
        return user
        
    # Try finding in Pharmacist database
    pharmacist = db.query(Pharmacist).filter(Pharmacist.id == int(sub)).first()
    if pharmacist:
        return pharmacist
        
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
    Enqueues OCR extraction and AI parsing as a background task.
    """
    # Enforce file format constraints
    allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
    file_ext = (file.filename or "").lower()
    if not any(file_ext.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Supported formats: JPG, JPEG, PNG, PDF."
        )

    # 1. Save uploaded file on disk
    file_path = prescription_service.save_uploaded_file(file)
    
    # 2. Register prescription entry in database
    prescription = prescription_service.create_prescription_record(
        db=db,
        customer_id=current_user.id,
        file_path=file_path,
        original_filename=file.filename or "prescription",
        pharmacy_id=pharmacy_id
    )
    
    # 3. Schedule asynchronous OCR + AI processing
    background_tasks.add_task(prescription_service.process_prescription_background, prescription.id)
    
    return prescription

@router.get("", response_model=List[PrescriptionResponse])
def read_all_prescriptions(
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Endpoint for pharmacists to list all uploaded prescriptions.
    """
    return prescription_service.get_all_prescriptions(db)

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
    return prescription_service.get_prescriptions_by_pharmacy(db, pharmacy_id)

@router.get("/{id}", response_model=PrescriptionResponse)
def read_prescription_by_id(
    id: int,
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve detailed prescription record (including extracted medicine items).
    Accessible by either the prescription owner (customer) or a verified pharmacist.
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
        
    return prescription

@router.put("/{id}/approve", response_model=PrescriptionResponse)
def approve_prescription(
    id: int,
    review: Optional[PrescriptionReviewRequest] = None,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Endpoint for pharmacists to approve a prescription and add optional validation comments.
    """
    comments = review.pharmacist_comments if review else None
    prescription = prescription_service.approve_prescription(db, id, comments)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    return prescription

@router.put("/{id}/reject", response_model=PrescriptionResponse)
def reject_prescription(
    id: int,
    review: Optional[PrescriptionReviewRequest] = None,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Endpoint for pharmacists to reject a prescription (e.g. invalid signature/expired) with mandatory/optional comments.
    """
    comments = review.pharmacist_comments if review else None
    prescription = prescription_service.reject_prescription(db, id, comments)
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    return prescription
