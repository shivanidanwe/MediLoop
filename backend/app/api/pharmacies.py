from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.pharmacy import PharmacyResponse, PharmacyDetail, PharmacyCreate, PharmacyUpdate
from app.services import pharmacy_service

router = APIRouter(prefix="/pharmacies", tags=["Pharmacies"])

@router.get("", response_model=List[PharmacyResponse])
def read_all_pharmacies(db: Session = Depends(get_db)):
    """
    Get all active pharmacies.
    """
    return pharmacy_service.get_all_pharmacies(db)

@router.get("/nearby", response_model=List[PharmacyResponse])
def read_nearby_pharmacies(
    latitude: Optional[float] = None, 
    longitude: Optional[float] = None, 
    db: Session = Depends(get_db)
):
    """
    Get nearby active pharmacies. Geolocation support to be implemented in the future.
    """
    return pharmacy_service.get_nearby_pharmacies(db, latitude, longitude)

@router.get("/{id}", response_model=PharmacyDetail)
def read_pharmacy_by_id(id: int, db: Session = Depends(get_db)):
    """
    Get pharmacy details by ID, including its pharmacists.
    """
    db_pharmacy = pharmacy_service.get_pharmacy_by_id(db, id)
    if not db_pharmacy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy not found"
        )
    return db_pharmacy

@router.post("", response_model=PharmacyResponse, status_code=status.HTTP_201_CREATED)
def create_new_pharmacy(pharmacy_data: PharmacyCreate, db: Session = Depends(get_db)):
    """
    Create a new pharmacy.
    """
    return pharmacy_service.create_pharmacy(db, pharmacy_data)

@router.put("/{id}", response_model=PharmacyResponse)
def update_existing_pharmacy(id: int, pharmacy_data: PharmacyUpdate, db: Session = Depends(get_db)):
    """
    Update an existing pharmacy.
    """
    db_pharmacy = pharmacy_service.update_pharmacy(db, id, pharmacy_data)
    if not db_pharmacy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pharmacy not found"
        )
    return db_pharmacy

