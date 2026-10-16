from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_pharmacist
from app.models.pharmacist import Pharmacist
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate, MedicineUpdate, MedicineResponse

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.get("", response_model=List[MedicineResponse])
def read_all_medicines(
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """
    List active catalog medicines with pagination.
    """
    return db.query(Medicine).filter(Medicine.is_active == True).offset(skip).limit(limit).all()

@router.get("/search", response_model=List[MedicineResponse])
def search_medicines_catalog(
    q: str = Query(..., description="Query string matching brand name or generic name"),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Fuzzy/partial matching search by brand name or generic name.
    """
    cleaned_query = f"%{q.lower().strip()}%"
    return db.query(Medicine).filter(
        Medicine.is_active == True,
        (Medicine.brand_name.ilike(cleaned_query) | Medicine.generic_name.ilike(cleaned_query))
    ).limit(limit).all()

@router.get("/{id}", response_model=MedicineResponse)
def read_medicine_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieve specific medicine catalog item details.
    """
    medicine = db.query(Medicine).filter(Medicine.id == id, Medicine.is_active == True).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found in catalog"
        )
    return medicine

@router.post("", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine_catalog_item(
    medicine_data: MedicineCreate,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Add a new medicine to the system catalog. Restricted to authenticated pharmacists.
    """
    # Check if duplicate brand/generic/strength combo exists
    existing = db.query(Medicine).filter(
        Medicine.brand_name.ilike(medicine_data.brand_name),
        Medicine.generic_name.ilike(medicine_data.generic_name),
        Medicine.strength == medicine_data.strength
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine item with same brand name, generic name, and strength already exists."
        )

    db_medicine = Medicine(**medicine_data.model_dump())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@router.put("/{id}", response_model=MedicineResponse)
def update_medicine_catalog_item(
    id: int,
    medicine_data: MedicineUpdate,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Update detailed metadata of a catalog item. Restricted to pharmacists.
    """
    medicine = db.query(Medicine).filter(Medicine.id == id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found in catalog"
        )
        
    for key, val in medicine_data.model_dump(exclude_unset=True).items():
        setattr(medicine, key, val)
        
    db.commit()
    db.refresh(medicine)
    return medicine

@router.delete("/{id}", response_model=MedicineResponse)
def deactivate_medicine_catalog_item(
    id: int,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Soft delete/deactivate a medicine catalog item. Restricted to pharmacists.
    """
    medicine = db.query(Medicine).filter(Medicine.id == id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicine not found in catalog"
        )
        
    medicine.is_active = False
    db.commit()
    db.refresh(medicine)
    return medicine
