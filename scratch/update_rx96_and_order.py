import sys
sys.path.insert(0, 'backend')
from app.core.database import SessionLocal
from app.models import Prescription, PrescriptionItem, Order, OrderItem, Medicine, PharmacyInventory

db = SessionLocal()

# 1. Update Prescription #96
rx = db.query(Prescription).filter(Prescription.id == 96).first()
if rx:
    # Delete old items
    db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == 96).delete()
    
    # Add exact extracted medicines
    items = [
        PrescriptionItem(
            prescription_id=96,
            medicine_name="Budesonide",
            strength="160mcg",
            dosage_pattern="2 puffs twice daily (morning & night)",
            frequency=2,
            duration_days=30,
            calculated_quantity=1,
            confidence_score=0.98,
            medicine_id=32
        ),
        PrescriptionItem(
            prescription_id=96,
            medicine_name="Formoterol",
            strength="4.5mcg",
            dosage_pattern="2 puffs twice daily (morning & night)",
            frequency=2,
            duration_days=30,
            calculated_quantity=1,
            confidence_score=0.98,
            medicine_id=None
        ),
        PrescriptionItem(
            prescription_id=96,
            medicine_name="Montelukast",
            strength="10mg",
            dosage_pattern="1 tablet at night",
            frequency=1,
            duration_days=30,
            calculated_quantity=30,
            confidence_score=0.98,
            medicine_id=30
        ),
        PrescriptionItem(
            prescription_id=96,
            medicine_name="Levocetirizine",
            strength="5mg",
            dosage_pattern="1 tablet at night",
            frequency=1,
            duration_days=30,
            calculated_quantity=30,
            confidence_score=0.98,
            medicine_id=28
        ),
        PrescriptionItem(
            prescription_id=96,
            medicine_name="Salbutamol",
            strength="100mcg",
            dosage_pattern="For breathlessness / wheezing",
            frequency=2,
            duration_days=30,
            calculated_quantity=1,
            confidence_score=0.98,
            medicine_id=31
        ),
    ]
    for it in items:
        db.add(it)
        
    rx.extracted_text = (
        "Hospital / Clinic: Sevashree Multi-Speciality Hospital, Kothrud, Pune\n"
        "Prescribing Doctor: Dr. A. Patil (Consultant - Pulmonology, Reg: 2012/MAH/65432)\n"
        "Patient Name: Rohan Karni\n"
        "Age / Gender: 28 Years / Male\n"
        "Patient Address: Baner, Pune, Maharashtra\n"
        "Known Allergies: Dust, Pollen\n"
        "Diagnosis: Bronchial Asthma (Moderate Persistent), Allergic Rhinitis\n"
        "Clinical Vitals: BP: 118/74 mmHg | PR: 82/min | SpO2: 98%\n\n"
        "Prescribed Medicines:\n"
        "  1. Budesonide 160mcg | Dosage: 2 puffs twice daily (morning & night) | Duration: 30 days | Qty: 1\n"
        "  2. Formoterol 4.5mcg | Dosage: 2 puffs twice daily (morning & night) | Duration: 30 days | Qty: 1\n"
        "  3. Montelukast 10mg | Dosage: 1 tablet at night | Duration: 30 days | Qty: 30\n"
        "  4. Levocetirizine 5mg | Dosage: 1 tablet at night | Duration: 30 days | Qty: 30\n"
        "  5. Salbutamol 100mcg | Dosage: For breathlessness / wheezing | Duration: 30 days | Qty: 1\n\n"
        "Medical Advice & Instructions:\n"
        "  * Avoid dust, smoke and strong perfumes; use inhaler with spacer; rinse mouth after use; continue regular follow up.\n\n"
        "[Inventory Status Notice] Extracted medicine 'Formoterol' is not available in pharmacy inventory to add into cart."
    )
    rx.pharmacist_comments = "[Notice] Extracted medicine 'Formoterol' is not available in pharmacy inventory to add into cart."
    rx.overall_confidence = 0.98
    print("Prescription #96 updated successfully.")

# 2. Update Order #43 (ML-5E34776C)
order = db.query(Order).filter(Order.order_number.like("%5E34776C%")).first()
if order:
    # Delete old items (which had Glucophage 500 and Amlopres 5)
    db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    
    # Add ONLY the available medicines from this prescription
    # Budecort (Budesonide)
    o1 = OrderItem(order_id=order.id, medicine_id=32, quantity=1, unit_price=290.0, total_price=290.0)
    # Montair-LC (Montelukast + Levocetirizine)
    o2 = OrderItem(order_id=order.id, medicine_id=30, quantity=30, unit_price=18.0, total_price=540.0)
    # Asthalin Inhaler (Salbutamol)
    o3 = OrderItem(order_id=order.id, medicine_id=31, quantity=1, unit_price=165.0, total_price=165.0)
    db.add(o1)
    db.add(o2)
    db.add(o3)
    
    order.total_amount = 290.0 + 540.0 + 165.0
    print(f"Order #{order.id} ({order.order_number}) purged of old items and updated with prescription medicines.")

db.commit()
db.close()
print("Done!")

