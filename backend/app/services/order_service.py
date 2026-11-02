import uuid
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cart import Cart, CartItem, CartStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.services import inventory_service
import logging

logger = logging.getLogger(__name__)

def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.id == order_id).first()

def get_all_orders(db: Session) -> List[Order]:
    return db.query(Order).order_by(Order.placed_at.desc()).all()

def get_orders_by_customer(db: Session, customer_id: int) -> List[Order]:
    return db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.placed_at.desc()).all()

def get_orders_by_pharmacy(db: Session, pharmacy_id: int) -> List[Order]:
    return db.query(Order).filter(Order.pharmacy_id == pharmacy_id).order_by(Order.placed_at.desc()).all()

def create_order_from_cart(
    db: Session, 
    customer_id: int, 
    address_id: int, 
    payment_method: str
) -> Order:
    """
    Creates an Order from the customer's active Cart.
    Performs stock verification, stock reservation, and cart checkout within a database transaction.
    If stock levels are insufficient, raises ValueError, aborting order creation.
    """
    # 1. Fetch active cart
    cart = db.query(Cart).filter(
        Cart.customer_id == customer_id,
        Cart.status == CartStatus.ACTIVE
    ).first()
    
    if not cart or not cart.items:
        raise ValueError("Cannot checkout. Active cart is empty or does not exist.")
        
    if not cart.pharmacy_id:
        raise ValueError("No pharmacy associated with this cart.")

    try:
        # 2. Verify and Reserve inventory stock for all items
        for item in cart.items:
            # Check availability
            is_available, current_stock = inventory_service.check_stock(
                db, cart.pharmacy_id, item.medicine_id, item.quantity
            )
            if not is_available:
                raise ValueError(
                    f"Insufficient stock for medicine ID {item.medicine_id}. "
                    f"Required: {item.quantity}, Available: {current_stock}"
                )
                
            # Reserve stock (decrements inventory quantity)
            inventory_service.reserve_stock(db, cart.pharmacy_id, item.medicine_id, item.quantity, commit=False)
            
        # 3. Create unique order number
        order_number = f"ML-{uuid.uuid4().hex[:8].upper()}"
        
        # 4. Create Order record
        db_order = Order(
            order_number=order_number,
            customer_id=customer_id,
            pharmacy_id=cart.pharmacy_id,
            cart_id=cart.id,
            address_id=address_id,
            payment_method=payment_method,
            payment_status="PENDING",
            order_status=OrderStatus.RECEIVED,
            total_amount=cart.total_amount
        )
        db.add(db_order)
        db.flush() # Sync order id
        
        # 5. Create OrderItem records
        for item in cart.items:
            db_order_item = OrderItem(
                order_id=db_order.id,
                medicine_id=item.medicine_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )
            db.add(db_order_item)
            
        # 6. Mark cart as checked out
        cart.status = CartStatus.CHECKED_OUT
        db.add(cart)
        
        db.commit()
        db.refresh(db_order)
        logger.info(f"Order created successfully: {db_order.order_number} (ID: {db_order.id})")

        # Trigger Order Completion Multi-Agent Workflow asynchronously
        _trigger_order_completed_workflow(db_order.id, customer_id)

        return db_order
        
    except Exception as e:
        db.rollback() # Rollback transaction if reservation/creation fails
        logger.error(f"Failed to place order: {str(e)}")
        raise e

def update_order_status(db: Session, order_id: int, new_status: OrderStatus) -> Optional[Order]:
    """
    Transition order status. Handles releasing reserved stock back to inventory if order is cancelled.
    """
    order = get_order_by_id(db, order_id)
    if not order:
        return None
        
    # If transitioning to CANCELLED or REJECTED, release reserved stock back to pharmacy
    status_str = new_status.value if hasattr(new_status, "value") else str(new_status)
    if status_str in ["CANCELLED", "REJECTED"] and str(order.order_status) not in ["CANCELLED", "REJECTED"]:
        for item in order.items:
            inventory_service.release_reserved_stock(
                db, 
                pharmacy_id=order.pharmacy_id, 
                medicine_id=item.medicine_id, 
                quantity=item.quantity,
                commit=False
            )
            
    order.order_status = status_str
    db.commit()
    db.refresh(order)

    if status_str == "DELIVERED":
        _trigger_order_completed_workflow(order.id, order.customer_id)

    return order

def _trigger_order_completed_workflow(order_id: int, customer_id: int) -> None:
    """Helper to execute Refill Reminder & Notification MultiAgent Workflow."""
    import asyncio
    from app.agents.context import AgentContext
    from app.agents.factory import get_workflow_engine

    try:
        context = AgentContext()
        context.metadata["order_id"] = order_id
        context.metadata["customer_id"] = customer_id
        
        engine = get_workflow_engine()
        asyncio.run(engine.execute_order_completed_workflow(context))
        logger.info(f"Order completion AI workflow executed for Order ID {order_id}")
    except Exception as ex:
        logger.warn(f"Order completion AI workflow trigger note: {str(ex)}")

