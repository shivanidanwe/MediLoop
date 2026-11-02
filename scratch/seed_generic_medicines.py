import sys, os
from datetime import date, timedelta
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.models.medicine import Medicine
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.pharmacy import Pharmacy

db = SessionLocal()

new_medicines = [
    {
        "brand_name": "Budesonide 160mcg",
        "generic_name": "Budesonide",
        "manufacturer": "Cipla Ltd",
        "strength": "160 mcg",
        "dosage_form": "Inhaler",
        "prescription_required": True,
        "description": "Inhaled corticosteroid for asthma maintenance.",
        "selling_price": 290.0,
        "mrp": 320.0,
        "stock": 50,
    },
    {
        "brand_name": "Montelukast 5mg",
        "generic_name": "Montelukast",
        "manufacturer": "Sun Pharma",
        "strength": "5 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Leukotriene receptor antagonist for asthma and allergic rhinitis.",
        "selling_price": 95.0,
        "mrp": 110.0,
        "stock": 100,
    },
    {
        "brand_name": "Levocetirizine 5mg",
        "generic_name": "Levocetirizine",
        "manufacturer": "Cipla Ltd",
        "strength": "5 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Non-sedating antihistamine for allergic rhinitis.",
        "selling_price": 45.0,
        "mrp": 55.0,
        "stock": 100,
    },
    {
        "brand_name": "Salbutamol 100mcg",
        "generic_name": "Salbutamol",
        "manufacturer": "Cipla Ltd",
        "strength": "100 mcg",
        "dosage_form": "Inhaler",
        "prescription_required": True,
        "description": "Fast-acting bronchodilator for acute asthma bronchospasm relief.",
        "selling_price": 165.0,
        "mrp": 185.0,
        "stock": 50,
    },
]

pharmacies = db.query(Pharmacy).all()
pharmacy_ids = [p.id for p in pharmacies] if pharmacies else [1]

for item_info in new_medicines:
    existing = db.query(Medicine).filter(
        Medicine.brand_name.ilike(item_info["brand_name"])
    ).first()

    if not existing:
        med = Medicine(
            brand_name=item_info["brand_name"],
            generic_name=item_info["generic_name"],
            manufacturer=item_info["manufacturer"],
            strength=item_info["strength"],
            dosage_form=item_info["dosage_form"],
            prescription_required=item_info["prescription_required"],
            description=item_info["description"],
            is_active=True
        )
        db.add(med)
        db.flush()
        print(f"Created Medicine: ID {med.id} - {med.brand_name}")
    else:
        med = existing
        print(f"Medicine already exists: ID {med.id} - {med.brand_name}")

    # Add inventory
    for pid in pharmacy_ids:
        inv = db.query(PharmacyInventory).filter(
            PharmacyInventory.pharmacy_id == pid,
            PharmacyInventory.medicine_id == med.id
        ).first()

        if not inv:
            inv = PharmacyInventory(
                pharmacy_id=pid,
                medicine_id=med.id,
                stock_quantity=item_info["stock"],
                selling_price=item_info["selling_price"],
                mrp=item_info["mrp"],
                batch_number=f"BAT-{med.id}099",
                expiry_date=date.today() + timedelta(days=500),
                is_available=True
            )
            db.add(inv)
            print(f"   Added Inventory for Pharmacy {pid}: Stock={item_info['stock']}, Price=Rs.{item_info['selling_price']}")
        else:
            inv.stock_quantity = item_info["stock"]
            inv.selling_price = item_info["selling_price"]
            inv.is_available = True
            db.add(inv)

db.commit()
db.close()
print("Done seeding generic medicines and inventory!")

