import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.order import Order, OrderItem
from app.models.medicine import Medicine

db = SessionLocal()
orders = db.query(Order).order_by(Order.id.desc()).limit(5).all()

print("=== RECENT ORDERS PRICING AUDIT ===")
for o in orders:
    print(f"\nOrder ID: {o.id} | Number: {o.order_number} | Recorded Total: Rs.{o.total_amount}")
    items_sum = 0.0
    for it in o.items:
        med_name = it.medicine.brand_name if it.medicine else f"Med #{it.medicine_id}"
        expected_line = round(it.quantity * it.unit_price, 2)
        print(f"   - {med_name:25s} | Qty: {it.quantity:2d} | Unit: Rs.{it.unit_price:6.2f} | Line: Rs.{it.total_price:7.2f} (Calc: Rs.{expected_line:7.2f})")
        items_sum += it.total_price
    print(f"   Items Sum: Rs.{items_sum:.2f} | Diff: Rs.{abs(o.total_amount - items_sum):.2f}")

db.close()

