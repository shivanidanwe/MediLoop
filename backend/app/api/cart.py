from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.prescription import Prescription
from app.schemas.cart import CartResponse, CartItemResponse, CartItemCreate, CartItemUpdate
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("", response_model=CartResponse)
def get_cart(
    pharmacy_id: Optional[int] = Query(None, description="Optional store ID to link/update active cart"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the current customer's active cart.
    Allows passing pharmacy_id to associate or switch pharmacies.
    """
    cart = cart_service.get_or_create_active_cart(db, current_user.id, pharmacy_id)

    unavailable_msgs = []
    rx_text = None
    latest_rx = db.query(Prescription).filter(
        Prescription.customer_id == current_user.id
    ).order_by(Prescription.id.desc()).first()

    if latest_rx:
        rx_text = latest_rx.extracted_text
        if latest_rx.pharmacist_comments and "[Stock Notice]" in latest_rx.pharmacist_comments:
            for line in latest_rx.pharmacist_comments.split("\n"):
                if "[Stock Notice]" in line:
                    notice_body = line.replace("[Stock Notice]", "").strip()
                    for sub in notice_body.split(" | "):
                        s = sub.strip()
                        if s and s not in unavailable_msgs:
                            unavailable_msgs.append(s)

    response = CartResponse.model_validate(cart)
    response.unavailable_medicines = unavailable_msgs
    response.prescription_text = rx_text
    return response

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a medicine to the active cart. Pulls unit pricing and validates stock.
    """
    try:
        return cart_service.add_item_to_cart(
            db=db,
            customer_id=current_user.id,
            medicine_id=item_data.medicine_id,
            quantity=item_data.quantity,
            source=item_data.source
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item_quantity(
    item_id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Modify quantity of a cart item. Setting quantity to 0 will remove the item.
    """
    try:
        return cart_service.update_cart_item(
            db=db,
            customer_id=current_user.id,
            item_id=item_id,
            quantity=item_update.quantity
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an item completely from the active cart.
    """
    try:
        cart_service.remove_cart_item(db, current_user.id, item_id)
        return
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all items inside the active cart.
    """
    cart = cart_service.get_or_create_active_cart(db, current_user.id)
    cart_service.clear_cart(db, cart.id)
    return
