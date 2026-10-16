from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import date, timedelta
from app.models.pharmacy_inventory import PharmacyInventory
from app.schemas.pharmacy_inventory import PharmacyInventoryCreate, PharmacyInventoryUpdate

def get_inventory_by_pharmacy(db: Session, pharmacy_id: int) -> List[PharmacyInventory]:
    """
    Retrieve all inventory items for a specific pharmacy.
    """
    return db.query(PharmacyInventory).filter(
        PharmacyInventory.pharmacy_id == pharmacy_id
    ).all()

def get_inventory_item(db: Session, pharmacy_id: int, medicine_id: int, for_update: bool = False) -> Optional[PharmacyInventory]:
    """
    Retrieve specific inventory item by pharmacy and medicine with optional row-level lock.
    """
    query = db.query(PharmacyInventory).filter(
        PharmacyInventory.pharmacy_id == pharmacy_id,
        PharmacyInventory.medicine_id == medicine_id
    )
    if for_update:
        query = query.with_for_update()
    return query.first()

def check_stock(db: Session, pharmacy_id: int, medicine_id: int, quantity: int) -> Tuple[bool, int]:
    """
    Check if a pharmacy has enough stock of a medicine.
    Returns:
        Tuple[bool, int]: (is_available, current_stock_quantity)
    """
    item = get_inventory_item(db, pharmacy_id, medicine_id)
    if not item or not item.is_available:
        return False, 0
    return item.stock_quantity >= quantity, item.stock_quantity

def update_stock(db: Session, pharmacy_id: int, medicine_id: int, quantity_change: int, commit: bool = True, for_update: bool = True) -> Optional[PharmacyInventory]:
    """
    Increments or decrements stock quantity. Uses row-level lock (with_for_update) to prevent race conditions.
    """
    item = get_inventory_item(db, pharmacy_id, medicine_id, for_update=for_update)
    if not item:
        return None
        
    new_stock = item.stock_quantity + quantity_change
    if new_stock < 0:
        raise ValueError(f"Insufficient stock. Available: {item.stock_quantity}, Requested change: {quantity_change}")
        
    item.stock_quantity = new_stock
    # Automatically mark unavailable if stock reaches zero
    if item.stock_quantity == 0:
        item.is_available = False
    elif item.stock_quantity > 0 and quantity_change > 0:
        item.is_available = True
        
    db.flush()
    if commit:
        db.commit()
        db.refresh(item)
    return item

def reserve_stock(db: Session, pharmacy_id: int, medicine_id: int, quantity: int, commit: bool = True) -> Optional[PharmacyInventory]:
    """
    Reserves stock for an order/cart by decrementing stock_quantity.
    Safety: prevents stock from going below 0.
    """
    return update_stock(db, pharmacy_id, medicine_id, -quantity, commit)

def release_reserved_stock(db: Session, pharmacy_id: int, medicine_id: int, quantity: int, commit: bool = True) -> Optional[PharmacyInventory]:
    """
    Releases previously reserved stock back to the inventory (incrementing stock_quantity).
    """
    return update_stock(db, pharmacy_id, medicine_id, quantity, commit)

def create_or_update_inventory(
    db: Session, 
    pharmacy_id: int, 
    medicine_id: int, 
    inventory_data: PharmacyInventoryUpdate
) -> PharmacyInventory:
    """
    Add a medicine to inventory or update existing metrics.
    """
    item = get_inventory_item(db, pharmacy_id, medicine_id)
    if item:
        # Update existing
        for key, val in inventory_data.model_dump(exclude_unset=True).items():
            setattr(item, key, val)
        db.commit()
        db.refresh(item)
        return item
    else:
        # Create new (using fallback values for required fields)
        db_item = PharmacyInventory(
            pharmacy_id=pharmacy_id,
            medicine_id=medicine_id,
            stock_quantity=inventory_data.stock_quantity or 0,
            selling_price=inventory_data.selling_price or 0.0,
            mrp=inventory_data.mrp or 0.0,
            batch_number=inventory_data.batch_number or "UNKNOWN",
            expiry_date=inventory_data.expiry_date or (date.today() + timedelta(days=365)),
            is_available=inventory_data.is_available if inventory_data.is_available is not None else True
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

def get_low_stock_alerts(db: Session, pharmacy_id: int, threshold: int = 10) -> List[PharmacyInventory]:
    """
    Retrieve inventory items that are low in stock.
    """
    return db.query(PharmacyInventory).filter(
        PharmacyInventory.pharmacy_id == pharmacy_id,
        PharmacyInventory.stock_quantity <= threshold
    ).all()

def get_expiring_alerts(db: Session, pharmacy_id: int, within_days: int = 90) -> List[PharmacyInventory]:
    """
    Retrieve inventory items expiring within next X days.
    """
    target_date = date.today() + timedelta(days=within_days)
    return db.query(PharmacyInventory).filter(
        PharmacyInventory.pharmacy_id == pharmacy_id,
        PharmacyInventory.expiry_date <= target_date,
        PharmacyInventory.expiry_date >= date.today()
    ).all()
