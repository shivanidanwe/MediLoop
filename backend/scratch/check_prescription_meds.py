import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from app.models.medicine import Medicine
from app.models.pharmacy_inventory import PharmacyInventory

db = SessionLocal()
target_names = ['ceftas', 'calpol', 'drot', 'acera', 'alka', 'paracetamol', 'cefixime']
for name in target_names:
    matches = db.query(Medicine).filter(
        (Medicine.brand_name.ilike(f'%{name}%')) | (Medicine.generic_name.ilike(f'%{name}%'))
    ).all()
    print(f'Query for "{name}": {len(matches)} found')
    for m in matches:
        invs = db.query(PharmacyInventory).filter(PharmacyInventory.medicine_id == m.id).all()
        stocks = [f'Pharm {i.pharmacy_id}: stock {i.stock_quantity}, price Rs.{i.selling_price}' for i in invs]
        print(f'   - ID {m.id}: {m.brand_name} ({m.generic_name}) [{m.strength}] -> {stocks}')
db.close()
