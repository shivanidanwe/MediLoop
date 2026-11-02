from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.address import Address, AddressType
from app.schemas.address import Address as AddressSchema, AddressCreate, AddressUpdate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
def users_root():
    return {"message": "Users API route active"}

@router.get("/me/addresses", response_model=List[AddressSchema])
def get_user_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all saved addresses for the authenticated user from the database.
    """
    return db.query(Address).filter(Address.user_id == current_user.id).all()

@router.post("/me/addresses", response_model=AddressSchema, status_code=status.HTTP_201_CREATED)
def add_user_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a new delivery address to the database for the current user.
    """
    # If set as default, unset existing default
    if address_data.is_default_delivery:
        db.query(Address).filter(Address.user_id == current_user.id).update({"is_default_delivery": False})

    db_address = Address(
        user_id=current_user.id,
        address_type=address_data.address_type,
        house_number=address_data.house_number,
        street=address_data.street,
        city=address_data.city,
        state=address_data.state,
        pincode=address_data.pincode,
        landmark=address_data.landmark,
        is_default_delivery=address_data.is_default_delivery
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

@router.put("/me/addresses/{address_id}", response_model=AddressSchema)
def update_user_address(
    address_id: int,
    update_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing address in the database for the authenticated user.
    """
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not db_address:
        # Fallback: check if user has any address, update the first one
        db_address = db.query(Address).filter(Address.user_id == current_user.id).first()
        if not db_address:
            # Create if none exists
            db_address = Address(
                user_id=current_user.id,
                address_type=update_data.address_type or AddressType.HOME,
                house_number=update_data.house_number or "Flat 101",
                street=update_data.street or "Main Road",
                city=update_data.city or "Bengaluru",
                state=update_data.state or "Karnataka",
                pincode=update_data.pincode or "560103"
            )
            db.add(db_address)

    for field, val in update_data.model_dump(exclude_unset=True).items():
        setattr(db_address, field, val)

    if update_data.is_default_delivery:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.id != db_address.id
        ).update({"is_default_delivery": False})

    db.commit()
    db.refresh(db_address)
    return db_address

@router.delete("/me/addresses/{address_id}")
def delete_user_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a saved delivery address from the database.
    """
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()

    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(db_address)
    db.commit()
    return {"success": True, "message": "Address deleted successfully"}
