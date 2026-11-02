import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
from app.core.database import SessionLocal
from app.models.medicine import Medicine
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.prescription import Prescription

db = SessionLocal()
print("=== CATALOG MEDICINES MATCHING ===")
for m in db.query(Medicine).all():
    name = (m.brand_name + " " + (m.generic_name or "")).lower()
    if any(k in name for k in ['budesonide', 'budecort', 'formoterol', 'montelukast', 'montair', 'levocetirizine', 'zyrtec', 'salbutamol', 'asthalin']):
        print(f"ID: {m.id} | Brand: {m.brand_name} | Generic: {m.generic_name}")

print("\n=== CARTS & CART ITEMS ===")
carts = db.query(Cart).all()
for c in carts:
    print(f"Cart ID: {c.id}, Customer: {c.customer_id}, Status: {c.status}")
    for item in c.items:
        med = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        print(f"   Item: {med.brand_name if med else 'Unknown'} (id={item.medicine_id}), qty: {item.quantity}, unit_price: {item.unit_price}")

print("\n=== RECENT PRESCRIPTIONS ===")
rxs = db.query(Prescription).order_by(Prescription.id.desc()).limit(3).all()
for rx in rxs:
    print(f"Rx ID: {rx.id}, Status: {rx.status}, Patient: {rx.patient_name}")
    print(f"Items: {[item.medicine_name for item in rx.items]}")
    print(f"Extracted Text: {rx.extracted_text[:120] if rx.extracted_text else 'None'}...")

print("\n=== RECENT ORDERS ===")
orders = db.query(Order).order_by(Order.id.desc()).limit(3).all()
for o in orders:
    print(f"Order ID: {o.id}, Order Number: {o.order_number}, Status: {o.order_status}, Prescription ID: {o.prescription_id}")
    for item in o.items:
        med = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
        print(f"   Item: {med.brand_name if med else 'Unknown'} (id={item.medicine_id}), qty: {item.quantity}, unit_price: {item.unit_price}")

db.close()
