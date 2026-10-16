from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_pharmacist
from app.models.pharmacist import Pharmacist
from app.schemas.pharmacy_inventory import (
    PharmacyInventoryResponse, 
    StockCheckResponse, 
    PharmacyInventoryUpdate
)
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/pharmacy/{pharmacy_id}", response_model=List[PharmacyInventoryResponse])
def get_pharmacy_inventory(
    pharmacy_id: int,
    db: Session = Depends(get_db)
):
    """
    List entire stock inventory for a pharmacy.
    """
    return inventory_service.get_inventory_by_pharmacy(db, pharmacy_id)

@router.get("/check", response_model=StockCheckResponse)
def check_stock_availability(
    pharmacy_id: int = Query(...),
    medicine_id: int = Query(...),
    quantity: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    """
    Utility endpoint to verify stock availability for a specific medicine at a pharmacy.
    Used by Carts, Orders, and safety verification processes.
    """
    is_available, current_stock = inventory_service.check_stock(db, pharmacy_id, medicine_id, quantity)
    return {
        "pharmacy_id": pharmacy_id,
        "medicine_id": medicine_id,
        "requested_quantity": quantity,
        "available_quantity": current_stock,
        "is_available": is_available
    }

@router.put("/update", response_model=PharmacyInventoryResponse)
def update_pharmacy_stock(
    medicine_id: int = Query(...),
    inventory_data: PharmacyInventoryUpdate = ...,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Update inventory quantity, price, or details for a medicine.
    Only accessible by pharmacists, and restricts them to updating their own pharmacy's inventory.
    """
    pharmacy_id = current_pharmacist.pharmacy_id
    if not pharmacy_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pharmacist is not assigned to any pharmacy store."
        )
        
    try:
        updated_item = inventory_service.create_or_update_inventory(
            db=db,
            pharmacy_id=pharmacy_id,
            medicine_id=medicine_id,
            inventory_data=inventory_data
        )
        return updated_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
