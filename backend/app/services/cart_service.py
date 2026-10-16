from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.cart import Cart, CartItem, CartStatus, CartItemSource
from app.models.prescription import Prescription
from app.models.pharmacy_inventory import PharmacyInventory
from app.services import inventory_service
import logging

logger = logging.getLogger(__name__)

def get_or_create_active_cart(db: Session, customer_id: int, pharmacy_id: Optional[int] = None) -> Cart:
    """
    Retrieve the current ACTIVE cart for a customer, or create a new one.
    If the pharmacy_id is updated, the previous items are cleared to maintain inventory consistency.
    """
    cart = db.query(Cart).filter(
        Cart.customer_id == customer_id,
        Cart.status == CartStatus.ACTIVE
    ).first()

    if not cart:
        cart = Cart(customer_id=customer_id, pharmacy_id=pharmacy_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    # If pharmacy changed, clear previous items because stock & pricing are pharmacy-specific
    if pharmacy_id is not None and cart.pharmacy_id != pharmacy_id:
        cart.pharmacy_id = pharmacy_id
        # Clear items
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        recalculate_cart_totals(db, cart)
        db.commit()
        db.refresh(cart)

    return cart

def recalculate_cart_totals(db: Session, cart: Cart) -> None:
    """
    Recompute cart subtotal, delivery fees, and total amounts.
    """
    items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
    subtotal = sum(item.total_price for item in items)
    
    # Simple logic: Flat 50.0 delivery fee, free for orders above 500.0
    delivery_fee = 50.0 if (subtotal > 0 and subtotal < 500.0) else 0.0
    
    cart.subtotal = round(subtotal, 2)
    cart.delivery_fee = delivery_fee
    cart.discount = 0.0 # Placeholder for promo codes
    cart.total_amount = round(subtotal + delivery_fee - cart.discount, 2)
    db.add(cart)

def add_item_to_cart(
    db: Session, 
    customer_id: int, 
    medicine_id: int, 
    quantity: int = 1, 
    source: CartItemSource = CartItemSource.MANUAL_SEARCH
) -> CartItem:
    """
    Add a medicine to the customer's active cart.
    Validates stock availability and pulls prices from the pharmacy inventory.
    """
    cart = get_or_create_active_cart(db, customer_id)
    if not cart.pharmacy_id:
        raise ValueError("No pharmacy selected. Please select a pharmacy store before adding items.")

    # Retrieve unit price and verify item exists in pharmacy inventory
    inv_item = db.query(PharmacyInventory).filter(
        PharmacyInventory.pharmacy_id == cart.pharmacy_id,
        PharmacyInventory.medicine_id == medicine_id
    ).first()
    
    if not inv_item:
        raise ValueError("Selected medicine is not stocked by the chosen pharmacy.")
        
    # Check current cart item
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.medicine_id == medicine_id
    ).first()

    target_quantity = quantity
    if cart_item:
        target_quantity += cart_item.quantity

    # Validate stock availability
    is_available, available_stock = inventory_service.check_stock(
        db, cart.pharmacy_id, medicine_id, target_quantity
    )
    if not is_available:
        raise ValueError(
            f"Insufficient inventory stock. Requested: {target_quantity}, Available: {available_stock}"
        )

    if cart_item:
        cart_item.quantity = target_quantity
        cart_item.total_price = round(target_quantity * cart_item.unit_price, 2)
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            medicine_id=medicine_id,
            quantity=quantity,
            unit_price=inv_item.selling_price,
            total_price=round(quantity * inv_item.selling_price, 2),
            source=source
        )
        db.add(cart_item)

    db.flush() # Sync with database to run recalculation
    recalculate_cart_totals(db, cart)
    db.commit()
    db.refresh(cart_item)
    return cart_item

def update_cart_item(db: Session, customer_id: int, item_id: int, quantity: int) -> CartItem:
    """
    Modify quantity of an item in the active cart.
    """
    cart = get_or_create_active_cart(db, customer_id)
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise ValueError("Item not found in your cart.")
        
    if quantity <= 0:
        db.delete(cart_item)
    else:
        # Validate stock availability
        is_available, available_stock = inventory_service.check_stock(
            db, cart.pharmacy_id, cart_item.medicine_id, quantity
        )
        if not is_available:
            raise ValueError(
                f"Insufficient inventory stock. Requested: {quantity}, Available: {available_stock}"
            )
            
        cart_item.quantity = quantity
        cart_item.total_price = round(quantity * cart_item.unit_price, 2)
        db.add(cart_item)

    db.flush()
    recalculate_cart_totals(db, cart)
    db.commit()
    
    # Return updated item or empty if deleted
    return cart_item

def remove_cart_item(db: Session, customer_id: int, item_id: int) -> None:
    """
    Remove an item entirely from the active cart.
    """
    cart = get_or_create_active_cart(db, customer_id)
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise ValueError("Item not found in your cart.")
        
    db.delete(cart_item)
    db.flush()
    recalculate_cart_totals(db, cart)
    db.commit()

def clear_cart(db: Session, cart_id: int) -> None:
    """
    Deletes all items inside a cart and resets totals.
    """
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        recalculate_cart_totals(db, cart)
        db.commit()

def convert_approved_prescription_to_cart(db: Session, prescription_id: int) -> Cart:
    """
    Triggered when a prescription is APPROVED by a pharmacist.
    Clears any active cart and automatically populates the cart with matched prescription medicines.
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise ValueError("Prescription record not found.")
        
    if not prescription.pharmacy_id:
        prescription.pharmacy_id = 1
        db.commit()

    # 1. Create or clear the user's active cart linked to this pharmacy
    cart = get_or_create_active_cart(db, customer_id=prescription.customer_id, pharmacy_id=prescription.pharmacy_id)
    
    # 2. Convert each prescription item into a cart item if matched to catalog
    for item in prescription.items:
        if not item.medicine_id:
            logger.warning(f"Prescription Item '{item.medicine_name}' is not matched to a catalog ID, skipping cart load.")
            continue
            
        # Get stock price and availability from inventory
        inv_item = db.query(PharmacyInventory).filter(
            PharmacyInventory.pharmacy_id == prescription.pharmacy_id,
            PharmacyInventory.medicine_id == item.medicine_id
        ).first()
        
        if not inv_item:
            logger.warning(f"Matched medicine ID {item.medicine_id} is not stocked at pharmacy {prescription.pharmacy_id}, skipping.")
            continue
            
        quantity = item.calculated_quantity or 1
        
        # Check if already added to cart
        cart_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.medicine_id == item.medicine_id
        ).first()
        
        if cart_item:
            # Add together
            cart_item.quantity += quantity
            cart_item.total_price = round(cart_item.quantity * cart_item.unit_price, 2)
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                medicine_id=item.medicine_id,
                quantity=quantity,
                unit_price=inv_item.selling_price,
                total_price=round(quantity * inv_item.selling_price, 2),
                source=CartItemSource.PRESCRIPTION
            )
            db.add(cart_item)
            
    db.flush()
    recalculate_cart_totals(db, cart)
    db.commit()
    db.refresh(cart)
    logger.info(f"Loaded approved prescription {prescription_id} items into cart ID {cart.id}")
    return cart
