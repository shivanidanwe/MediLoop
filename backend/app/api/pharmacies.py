from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_pharmacist
from app.models.pharmacist import Pharmacist
from app.models.user import User
from app.models.order import Order
from app.schemas.pharmacy import PharmacyResponse, PharmacyDetail, PharmacyCreate, PharmacyUpdate, PharmacyCustomerResponse
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

@router.get("/customers", response_model=List[PharmacyCustomerResponse])
def get_pharmacy_customers(
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Retrieve customer directory for the authenticated pharmacist's pharmacy store.
    Provides customer name, phone, email, address, total orders, and last order date directly from database.
    """
    pharmacy_id = current_pharmacist.pharmacy_id
    users = db.query(User).filter(User.is_active == True).all()
    
    results = []
    for u in users:
        # Check orders for this user at this pharmacy first
        pharmacy_orders = (
            db.query(Order)
            .filter(Order.customer_id == u.id, Order.pharmacy_id == pharmacy_id)
            .order_by(Order.placed_at.desc())
            .all()
        )
        all_orders = (
            db.query(Order)
            .filter(Order.customer_id == u.id)
            .order_by(Order.placed_at.desc())
            .all()
        )
        
        pharmacy_count = len(pharmacy_orders)
        total_count = len(all_orders)
        
        # Determine last order date
        latest_order = pharmacy_orders[0] if pharmacy_orders else (all_orders[0] if all_orders else None)
        if latest_order and latest_order.placed_at:
            last_order_str = latest_order.placed_at.strftime("%Y-%m-%d")
            last_order_iso = latest_order.placed_at.isoformat()
        else:
            last_order_str = "N/A"
            last_order_iso = None
            
        address_str = "Pandharpur, Maharashtra"
        if latest_order and latest_order.delivery_address:
            address_str = latest_order.delivery_address
        elif u.addresses:
            addr = u.addresses[0]
            parts = [addr.house_number, addr.street, addr.city, addr.state, addr.pincode]
            address_str = ", ".join([str(p).strip() for p in parts if p and str(p).strip()])
            
        order_count = pharmacy_count if pharmacy_count > 0 else total_count

        results.append({
            "id": u.id,
            "name": u.full_name.strip() if u.full_name else f"Customer #{u.id}",
            "phone": u.mobile_number or "+91 9876543210",
            "email": u.email,
            "address": address_str,
            "orders": order_count,
            "total_orders": total_count,
            "last_order": last_order_str,
            "last_order_date": last_order_iso
        })
        
    results.sort(key=lambda x: (x["orders"] > 0, x["last_order_date"] or ""), reverse=True)
    return results

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

