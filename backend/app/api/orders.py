from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Union
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_pharmacist, oauth2_scheme
from app.core.security import decode_access_token
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["Orders"])

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

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order_from_cart(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Checkout active cart and place a pharmacy order. Reserves stock atomically.
    """
    try:
        return order_service.create_order_from_cart(
            db=db,
            customer_id=current_user.id,
            address_id=order_data.address_id,
            payment_method=order_data.payment_method
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=List[OrderResponse])
def read_all_orders(
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Retrieve all orders inside the system (Pharmacist administration queue).
    """
    return order_service.get_all_orders(db)

@router.get("/customer", response_model=List[OrderResponse])
def read_customer_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve order history for the logged-in customer.
    """
    return order_service.get_orders_by_customer(db, current_user.id)

@router.get("/pharmacy/{pharmacy_id}", response_model=List[OrderResponse])
def read_pharmacy_orders(
    pharmacy_id: int,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Retrieve incoming orders for a specific pharmacy.
    """
    # Enforce pharmacist works at target pharmacy
    if current_pharmacist.pharmacy_id != pharmacy_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access orders of this pharmacy store."
        )
    return order_service.get_orders_by_pharmacy(db, pharmacy_id)

@router.get("/{id}", response_model=OrderResponse)
def read_order_by_id(
    id: int,
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    """
    Retrieve detailed order details. Accessible by the order owner or verified pharmacists.
    """
    order = order_service.get_order_by_id(db, id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    # Customer owner verification check
    if isinstance(current_actor, User) and order.customer_id != current_actor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order."
        )
        
    return order

@router.put("/{id}/status", response_model=OrderResponse)
def transition_order_status(
    id: int,
    status_data: OrderStatusUpdate,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Update order status (Pharmacist updates state machine).
    Automatically releases reserved inventory stock if order is CANCELLED.
    """
    order = order_service.get_order_by_id(db, id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    # Verify pharmacist works at the order's pharmacy store
    if current_pharmacist.pharmacy_id != order.pharmacy_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update orders of this pharmacy store."
        )
        
    updated_order = order_service.update_order_status(db, id, status_data.order_status)
    return updated_order
