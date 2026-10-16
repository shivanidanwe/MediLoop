from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.pharmacist import PharmacistResponse, PharmacistCreate
from app.services import pharmacy_service, pharmacist_service

router = APIRouter(prefix="/pharmacists", tags=["Pharmacists"])

@router.post("", response_model=PharmacistResponse, status_code=status.HTTP_201_CREATED)
def create_new_pharmacist(pharmacist_data: PharmacistCreate, db: Session = Depends(get_db)):
    """
    Create a new pharmacist belonging to a pharmacy.
    """
    # Verify the pharmacy exists
    db_pharmacy = pharmacy_service.get_pharmacy_by_id(db, pharmacist_data.pharmacy_id)
    if not db_pharmacy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pharmacy not found"
        )
    return pharmacist_service.create_pharmacist(db, pharmacist_data)
