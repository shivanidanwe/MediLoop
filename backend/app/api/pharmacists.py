from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.dependencies import get_current_pharmacist
from app.core.security import verify_password, hash_password
from app.models.pharmacist import Pharmacist
from app.schemas.pharmacist import PharmacistResponse, PharmacistCreate
from app.services import pharmacy_service, pharmacist_service

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

router = APIRouter(prefix="/pharmacists", tags=["Pharmacists"])

@router.post("", response_model=PharmacistResponse, status_code=status.HTTP_201_CREATED)
def create_new_pharmacist(pharmacist_data: PharmacistCreate, db: Session = Depends(get_db)):
    """
    Create a new pharmacist belonging to a pharmacy and store credentials in database.
    """
    # Verify the pharmacy exists
    db_pharmacy = pharmacy_service.get_pharmacy_by_id(db, pharmacist_data.pharmacy_id)
    if not db_pharmacy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pharmacy not found"
        )
    return pharmacist_service.create_pharmacist(db, pharmacist_data)

@router.put("/me/password")
def change_pharmacist_password(
    data: ChangePasswordRequest,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Update password for the authenticated pharmacist and store updated hash in PostgreSQL.
    """
    if not verify_password(data.current_password, current_pharmacist.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password does not match."
        )
    current_pharmacist.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"success": True, "message": "Password updated successfully in database."}
