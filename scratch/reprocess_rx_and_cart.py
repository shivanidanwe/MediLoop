import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.prescription import Prescription, PrescriptionItem
from app.models.medicine import Medicine
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.services.orchestration_service import add_prescription_medicines_to_cart

db = SessionLocal()

# Find Rx 96
rx = db.query(Prescription).filter(Prescription.id == 96).first()
if not rx:
    rx = db.query(Prescription).order_by(Prescription.id.desc()).first()

print(f"Reprocessing Prescription ID: {rx.id} for Customer ID: {rx.customer_id}")

# Update Rx Items to link to proper generic medicines
for item in rx.items:
    raw = (item.medicine_name or "").lower()
    if "budesonide" in raw:
        med = db.query(Medicine).filter(Medicine.brand_name == "Budesonide 160mcg").first()
        item.medicine_id = med.id if med else None
        item.medicine_name = "Budesonide 160mcg"
    elif "formoterol" in raw:
        item.medicine_id = None
        item.medicine_name = "Formoterol 4.5mcg"
    elif "montelukast" in raw:
        med = db.query(Medicine).filter(Medicine.brand_name == "Montelukast 5mg").first()
        item.medicine_id = med.id if med else None
        item.medicine_name = "Montelukast 5mg"
    elif "levocetirizine" in raw:
        med = db.query(Medicine).filter(Medicine.brand_name == "Levocetirizine 5mg").first()
        item.medicine_id = med.id if med else None
        item.medicine_name = "Levocetirizine 5mg"
    elif "salbutamol" in raw:
        med = db.query(Medicine).filter(Medicine.brand_name == "Salbutamol 100mcg").first()
        item.medicine_id = med.id if med else None
        item.medicine_name = "Salbutamol 100mcg"
    db.add(item)

db.commit()
print("Updated Prescription Items.")

# Now populate cart using add_prescription_medicines_to_cart
cart = add_prescription_medicines_to_cart(db, rx.id)
print(f"Cart updated! Cart ID: {cart.id}")
print(f"Customer active cart items:")
for ci in cart.items:
    med = db.query(Medicine).filter(Medicine.id == ci.medicine_id).first()
    print(f"  - {med.brand_name} (id={med.id}) | Qty: {ci.quantity} | Unit: Rs.{ci.unit_price} | Total: Rs.{ci.total_price}")

print(f"Prescription pharmacist_comments:\n{rx.pharmacist_comments}")

# If Customer 20 has active cart, update it too
c20_cart = db.query(Cart).filter(Cart.customer_id == 20, Cart.status == "ACTIVE").first()
if c20_cart:
    db.query(CartItem).filter(CartItem.cart_id == c20_cart.id).delete()
    for ci in cart.items:
        new_ci = CartItem(
            cart_id=c20_cart.id,
            medicine_id=ci.medicine_id,
            quantity=ci.quantity,
            unit_price=ci.unit_price,
            total_price=ci.total_price,
            source=ci.source
        )
        db.add(new_ci)
    c20_cart.subtotal = cart.subtotal
    c20_cart.total_amount = cart.total_amount
    db.commit()
    print("Updated Customer 20 cart items to match!")

# Also update Order #43 items to match if it exists
order = db.query(Order).filter(Order.prescription_id == rx.id).first()
if not order:
    order = db.query(Order).order_by(Order.id.desc()).first()

if order:
    print(f"\nUpdating Order #{order.id} ({order.order_number})...")
    db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    total = 0.0
    for ci in cart.items:
        oi = OrderItem(
            order_id=order.id,
            medicine_id=ci.medicine_id,
            quantity=ci.quantity,
            unit_price=ci.unit_price,
            total_price=ci.total_price
        )
        db.add(oi)
        total += ci.total_price
    order.total_amount = round(total, 2)
    db.commit()
    print(f"Order #{order.id} updated with {len(cart.items)} items! Total: Rs.{order.total_amount}")
    for oi in order.items:
        med = db.query(Medicine).filter(Medicine.id == oi.medicine_id).first()
        print(f"  - {med.brand_name} | Qty: {oi.quantity} | Total: Rs.{oi.total_price}")

db.close()

