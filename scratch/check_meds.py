import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
from app.core.database import SessionLocal
from app.models.medicine import Medicine

db = SessionLocal()
meds = db.query(Medicine).all()
print(f"Total medicines: {len(meds)}")
for m in meds:
    print(f"ID {m.id:2d} | Brand: {m.brand_name:25s} | Generic: {m.generic_name or '':25s} | Form: {m.dosage_form}")
db.close()

