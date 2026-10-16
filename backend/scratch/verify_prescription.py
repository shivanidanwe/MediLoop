import sys
import os
import time

# Add the parent directory of backend/app to path to resolve imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User, Gender
from app.models.pharmacy import Pharmacy
from app.models.prescription import Prescription, PrescriptionItem, VerificationStatus
from app.services import prescription_service
from datetime import date, time as dtime

def verify_module():
    print("=" * 60)
    print("MediLoop Prescription Intelligence Module - Verification Script")
    print("=" * 60)

    # 1. Initialize DB and create all tables (just in case)
    print("Step 1: Auto-creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 2. Seed Mock Customer if not exists
        print("Step 2: Checking/Seeding Mock Customer...")
        customer = db.query(User).filter(User.email == "test_customer@mediloop.com").first()
        if not customer:
            customer = User(
                full_name="John Doe",
                email="test_customer@mediloop.com",
                mobile_number="+1234567890",
                hashed_password="mocked_password_hash",
                date_of_birth=date(1990, 1, 1),
                gender=Gender.MALE
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            print(f" -> Created new Mock Customer (ID: {customer.id})")
        else:
            print(f" -> Mock Customer exists (ID: {customer.id})")

        # 3. Seed Mock Pharmacy if not exists
        print("Step 3: Checking/Seeding Mock Pharmacy...")
        pharmacy = db.query(Pharmacy).filter(Pharmacy.email == "test_pharmacy@mediloop.com").first()
        if not pharmacy:
            pharmacy = Pharmacy(
                pharmacy_name="MediLoop Central Pharmacy",
                license_number="LIC-1234567",
                email="test_pharmacy@mediloop.com",
                phone_number="+1987654321",
                address="123 Health Ave",
                city="Wellness City",
                state="State of Care",
                pincode="123456",
                opening_time=dtime(8, 0),
                closing_time=dtime(22, 0)
            )
            db.add(pharmacy)
            db.commit()
            db.refresh(pharmacy)
            print(f" -> Created new Mock Pharmacy (ID: {pharmacy.id})")
        else:
            print(f" -> Mock Pharmacy exists (ID: {pharmacy.id})")

        # 4. Create a fake prescription file
        print("Step 4: Creating a dummy prescription file on disk...")
        os.makedirs("uploads/prescriptions", exist_ok=True)
        dummy_file_path = "uploads/prescriptions/dummy_presc.jpg"
        with open(dummy_file_path, "w") as f:
            f.write("Simulated binary image data")
        
        # 5. Create prescription DB record
        print("Step 5: Creating database prescription record...")
        prescription = prescription_service.create_prescription_record(
            db=db,
            customer_id=customer.id,
            file_path=dummy_file_path,
            original_filename="presc_dr_smith.jpg",
            pharmacy_id=pharmacy.id
        )
        print(f" -> Created Prescription Record (ID: {prescription.id}, Status: {prescription.verification_status.value})")

        # 6. Execute Background Processing synchronously for testing
        print("Step 6: Executing OCR and AI parsing background worker task (synchronously)...")
        prescription_service.process_prescription_background(prescription.id)
        
        # Refresh and fetch from DB
        db.refresh(prescription)
        print(f" -> Processing Complete.")
        print(f" -> Updated Status: {prescription.verification_status.value}")
        print(f" -> Extracted Text:\n{prescription.extracted_text}")
        print(f" -> Overall Confidence: {prescription.overall_confidence}")

        # 7. Check Extracted Items
        print("Step 7: Verifying parsed items...")
        items = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription.id).all()
        print(f" -> Total parsed items: {len(items)}")
        for idx, item in enumerate(items, 1):
            print(f"    Item #{idx}:")
            print(f"      - Medicine Name: {item.medicine_name}")
            print(f"      - Strength: {item.strength}")
            print(f"      - Dosage Pattern: {item.dosage_pattern}")
            print(f"      - Frequency: {item.frequency}")
            print(f"      - Duration Days: {item.duration_days}")
            print(f"      - Calculated Qty: {item.calculated_quantity}")
            print(f"      - Item Confidence: {item.confidence_score}")
            
        assert len(items) > 0, "No items parsed from prescription!"
        assert items[0].calculated_quantity > 0, "Item quantity was not calculated correctly!"

        # 8. Test Pharmacist Review approval/rejection endpoints logic
        print("Step 8: Testing Pharmacist Review actions...")
        approved_presc = prescription_service.approve_prescription(db, prescription.id, "Prescription checks out correctly.")
        print(f" -> Status after Approval: {approved_presc.verification_status.value}")
        print(f" -> Pharmacist Comments: {approved_presc.pharmacist_comments}")
        
        rejected_presc = prescription_service.reject_prescription(db, prescription.id, "Signature is missing.")
        print(f" -> Status after Rejection: {rejected_presc.verification_status.value}")
        print(f" -> Pharmacist Comments: {rejected_presc.pharmacist_comments}")

        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETED SUCCESSFULLY! All flows and integrations verified.")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Verification failed: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    verify_module()
