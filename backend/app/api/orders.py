from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Union, Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_pharmacist, oauth2_scheme
from app.core.security import decode_access_token
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse
from app.services import order_service, orchestration_service

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
    
    role = payload.get("role")
    sub_id = int(sub)

    if role == "pharmacist":
        pharmacist = db.query(Pharmacist).filter(Pharmacist.id == sub_id).first()
        if pharmacist:
            return pharmacist
    elif role in ("patient", "user", "customer"):
        user = db.query(User).filter(User.id == sub_id).first()
        if user:
            return user
        
    # Fallback for unlabelled tokens: check Pharmacist first if exists, else User
    pharmacist = db.query(Pharmacist).filter(Pharmacist.id == sub_id).first()
    if pharmacist and not role:
        return pharmacist
    user = db.query(User).filter(User.id == sub_id).first()
    if user:
        return user
        
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
    Single-click checkout: Place order for prescribed medicines.
    Orchestration layer performs stock verification for the selected pharmacy.
    - If stock unavailable: Notifies patient and raises 400.
    - If stock available: Reserves inventory and creates order in PENDING_VERIFICATION state.
    """
    pharmacy_id = order_data.pharmacy_id or 1
    return orchestration_service.orchestrate_order_placement(
        db=db,
        customer_id=current_user.id,
        pharmacy_id=pharmacy_id,
        address_id=order_data.address_id,
        payment_method=order_data.payment_method,
        prescription_id=order_data.prescription_id,
        items=[it.model_dump() for it in order_data.items] if order_data.items else None
    )

@router.get("", response_model=List[OrderResponse])
def read_all_orders(
    pharmacy_id: Optional[int] = None,
    current_pharmacist: Pharmacist = Depends(get_current_pharmacist),
    db: Session = Depends(get_db)
):
    """
    Retrieve incoming orders for the authenticated pharmacist's pharmacy store.
    Strictly prevents cross-pharmacy access.
    """
    target_pharmacy_id = current_pharmacist.pharmacy_id
    if pharmacy_id and pharmacy_id != target_pharmacy_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access orders of another pharmacy store."
        )
    return order_service.get_orders_by_pharmacy(db, target_pharmacy_id)

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
    Retrieve detailed order details. Accessible by the order owner or assigned pharmacists.
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

    # Pharmacist pharmacy assignment verification check
    if isinstance(current_actor, Pharmacist) and order.pharmacy_id != current_actor.pharmacy_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access orders belonging to another pharmacy store."
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
    Update order status enforcing legal state machine transitions and mandatory rejection reasons.
    Logs audit events and dispatches notifications.
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

    prev_status = str(order.order_status)
    new_status_str = status_data.order_status.value if hasattr(status_data.order_status, "value") else str(status_data.order_status)

    # 1. Terminal state check
    if prev_status in ["DELIVERED", "CANCELLED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition order from terminal state '{prev_status}'."
        )

    # 2. Mandatory rejection reason check
    if new_status_str == "REJECTED":
        if not status_data.rejection_reason or not status_data.rejection_reason.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A valid rejection reason is mandatory when rejecting an order."
            )
        order.rejection_reason = status_data.rejection_reason.strip()

    if new_status_str in ["ACCEPTED", "PRESCRIPTION_APPROVED", "Prescription Approved"]:
        from datetime import datetime
        order.verified_at = datetime.utcnow()

    # 3. Update status
    updated_order = order_service.update_order_status(db, id, status_data.order_status)

    # 4. Audit Log Event & Status History
    from app.models.order import OrderAuditEvent
    from app.models.order_status_history import OrderStatusHistory
    audit = OrderAuditEvent(
        order_id=order.id,
        actor_id=current_pharmacist.id,
        actor_role="PHARMACIST",
        previous_state=prev_status,
        new_state=new_status_str,
        action="PHARMACIST_STATUS_UPDATE",
        reason_or_note=status_data.rejection_reason or status_data.notes or f"Updated status to {new_status_str}"
    )
    db.add(audit)

    history = OrderStatusHistory(
        order_id=order.id,
        actor_id=current_pharmacist.id,
        actor_role="PHARMACIST",
        previous_status=prev_status,
        new_status=new_status_str,
        notes=status_data.rejection_reason or status_data.notes or f"Updated status to {new_status_str}"
    )
    db.add(history)

    # 5. Notify patient and pharmacy
    from app.models.notification import Notification
    notif_title = f"Order #{order.order_number} Update"
    if new_status_str == "REJECTED":
        notif_msg = f"Your order #{order.order_number} was rejected by the pharmacist. Reason: {status_data.rejection_reason}"
    elif new_status_str in ["ACCEPTED", "PRESCRIPTION_APPROVED", "Prescription Approved"]:
        notif_msg = f"Your order #{order.order_number} has been approved by the pharmacist and is being prepared."
    else:
        notif_msg = f"Your order #{order.order_number} status is now: {new_status_str}."

    notif = Notification(
        user_id=order.customer_id,
        pharmacy_id=current_pharmacist.pharmacy_id,
        pharmacist_id=current_pharmacist.id,
        title=notif_title,
        message=notif_msg,
        notification_type="ORDER_STATUS_UPDATE",
        action_url=f"/orders/{order.id}"
    )
    db.add(notif)
    db.commit()
    db.refresh(updated_order)

    return updated_order
