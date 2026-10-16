"""
Seed medicines specifically prescribed in the Dr. Sujit Suresh Durugkar prescription:
1. Tab. Ceftas-O 200 mg
2. Tab. Calpol 500 (already seeded, ensure inventory)
3. Tab. Drotin-DS 80mg
4. Cap. Acera-D (Rabeprazole 20mg + Domperidone 30mg)
5. Liq. Alkarate (Disodium Hydrogen Citrate 1.4g/5ml)
"""
import sys
import os
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.medicine import Medicine
from app.models.pharmacy import Pharmacy
from app.models.pharmacy_inventory import PharmacyInventory

NEW_PRESCRIPTION_MEDS = [
    {
        "brand_name": "Ceftas-O 200",
        "generic_name": "Cefixime + Ofloxacin",
        "manufacturer": "Intas Pharmaceuticals",
        "strength": "200 mg + 200 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Potent dual antibiotic for complicated urinary tract and respiratory infections."
    },
    {
        "brand_name": "Drotin-DS",
        "generic_name": "Drotaverine Hydrochloride",
        "manufacturer": "Walter Bushnell",
        "strength": "80 mg",
        "dosage_form": "Tablet",
        "prescription_required": True,
        "description": "Antispasmodic medication for smooth muscle spasms, kidney stone pain and severe abdominal cramps."
    },
    {
        "brand_name": "Acera-D",
        "generic_name": "Rabeprazole + Domperidone",
        "manufacturer": "Ipca Laboratories",
        "strength": "20 mg + 30 mg",
        "dosage_form": "Capsule",
        "prescription_required": True,
        "description": "Proton pump inhibitor and prokinetic combination to prevent acid reflux and antibiotic nausea."
    },
    {
        "brand_name": "Alkarate Liquid",
        "generic_name": "Disodium Hydrogen Citrate",
        "manufacturer": "Wallace Pharmaceuticals",
        "strength": "1.4 g / 5 ml",
        "dosage_form": "Syrup",
        "prescription_required": False,
        "description": "Systemic and urinary alkalizer for painful burning micturition, UTI symptoms, and gout."
    }
]

def seed_prescription_meds():
    db = SessionLocal()
    today = date.today()
    pharmacies = db.query(Pharmacy).all()
    print(f"Seeding prescription medicines across {len(pharmacies)} pharmacies...")

    prices = {
        "Ceftas-O 200": (145.0, 168.0),
        "Drotin-DS": (135.0, 155.0),
        "Acera-D": (110.0, 130.0),
        "Alkarate Liquid": (115.0, 130.0),
    }

    for item in NEW_PRESCRIPTION_MEDS:
        med = db.query(Medicine).filter(Medicine.brand_name == item["brand_name"]).first()
        if not med:
            med = Medicine(**item)
            db.add(med)
            db.commit()
            db.refresh(med)
            print(f"Added medicine: {med.brand_name} (ID: {med.id})")
        else:
            print(f"Found existing medicine: {med.brand_name} (ID: {med.id})")

        # Ensure stock in all pharmacies
        for pharm in pharmacies:
            inv = db.query(PharmacyInventory).filter(
                PharmacyInventory.pharmacy_id == pharm.id,
                PharmacyInventory.medicine_id == med.id
            ).first()

            selling_p, mrp_p = prices[item["brand_name"]]
            if not inv:
                inv = PharmacyInventory(
                    pharmacy_id=pharm.id,
                    medicine_id=med.id,
                    stock_quantity=100,
                    selling_price=selling_p,
                    mrp=mrp_p,
                    batch_number=f"BAT-{pharm.id:02d}-{med.id:03d}",
                    expiry_date=today + timedelta(days=365),
                    is_available=True
                )
                db.add(inv)
                print(f"  + Added stock to Pharmacy {pharm.id} ({pharm.pharmacy_name})")
            else:
                inv.stock_quantity = max(inv.stock_quantity, 50)
                inv.is_available = True
                print(f"  ~ Updated stock in Pharmacy {pharm.id} ({pharm.pharmacy_name}): {inv.stock_quantity}")

    # Also make sure Pharmacy 1 has Calpol 500
    calpol = db.query(Medicine).filter(Medicine.brand_name == "Calpol 500").first()
    if calpol:
        for pharm in pharmacies:
            calpol_inv = db.query(PharmacyInventory).filter(
                PharmacyInventory.pharmacy_id == pharm.id,
                PharmacyInventory.medicine_id == calpol.id
            ).first()
            if not calpol_inv:
                calpol_inv = PharmacyInventory(
                    pharmacy_id=pharm.id,
                    medicine_id=calpol.id,
                    stock_quantity=100,
                    selling_price=24.0,
                    mrp=26.5,
                    batch_number=f"BAT-{pharm.id:02d}-{calpol.id:03d}",
                    expiry_date=today + timedelta(days=365),
                    is_available=True
                )
                db.add(calpol_inv)
                print(f"  + Added Calpol 500 stock to Pharmacy {pharm.id}")

    db.commit()
    db.close()
    print("Prescription medicines successfully seeded and stocked!")

if __name__ == "__main__":
    seed_prescription_meds()
