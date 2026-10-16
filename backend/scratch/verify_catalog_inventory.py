import sys
import os

# Add the parent directory of backend/app to path to resolve imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.models.medicine import Medicine
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.user import User, Gender
from app.models.pharmacy import Pharmacy
from app.models.prescription import Prescription, PrescriptionItem
from app.services import medicine_matching_service, inventory_service, prescription_service
from app.schemas.pharmacy_inventory import PharmacyInventoryUpdate
from datetime import date, timedelta, time as dtime

def verify_catalog_inventory():
    print("=" * 60)
    print("MediLoop Medicine Catalog & Inventory Verification")
    print("=" * 60)

    # 1. Initialize DB and create all tables
    print("Step 1: Re-creating database tables (dropping old schema to sync column changes)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 2. Seed catalog medicines
        print("Step 2: Seeding active catalog medicines...")
        meds_to_seed = [
            {"brand_name": "Crocin 650", "generic_name": "Paracetamol", "manufacturer": "GSK plc", "strength": "650 mg", "dosage_form": "Tablet", "prescription_required": False, "description": "Pain reliever"},
            {"brand_name": "Dolo 650", "generic_name": "Paracetamol", "manufacturer": "Micro Labs Ltd", "strength": "650 mg", "dosage_form": "Tablet", "prescription_required": False, "description": "Fever reducer"},
            {"brand_name": "Amoxil 500", "generic_name": "Amoxicillin", "manufacturer": "Alkem Labs", "strength": "500 mg", "dosage_form": "Capsule", "prescription_required": True, "description": "Antibiotic"},
            {"brand_name": "Lipitor 10", "generic_name": "Atorvastatin", "manufacturer": "Pfizer Inc", "strength": "10 mg", "dosage_form": "Tablet", "prescription_required": True, "description": "Cholesterol control"}
        ]
        
        db_meds = {}
        for m in meds_to_seed:
            db_med = db.query(Medicine).filter(Medicine.brand_name == m["brand_name"]).first()
            if not db_med:
                db_med = Medicine(**m)
                db.add(db_med)
                db.commit()
                db.refresh(db_med)
                print(f" -> Seeded medicine: {db_med.brand_name} (ID: {db_med.id})")
            else:
                print(f" -> Medicine exists: {db_med.brand_name} (ID: {db_med.id})")
            db_meds[db_med.brand_name] = db_med

        # 3. Seed Mock Customer and Pharmacy if not exists (self-contained seeding)
        print("Step 3: Seeding mock customer and pharmacy...")
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
            print(f" -> Created Customer: {customer.full_name} (ID: {customer.id})")
        else:
            print(f" -> Customer exists: {customer.full_name} (ID: {customer.id})")

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
            print(f" -> Created Pharmacy: {pharmacy.pharmacy_name} (ID: {pharmacy.id})")
        else:
            print(f" -> Pharmacy exists: {pharmacy.pharmacy_name} (ID: {pharmacy.id})")
            
        pharmacy_id = pharmacy.id

        inventory_to_seed = [
            (db_meds["Crocin 650"].id, 100, 35.0, 35.0),
            (db_meds["Dolo 650"].id, 50, 30.0, 30.0),
            (db_meds["Amoxil 500"].id, 20, 120.0, 120.0),
            (db_meds["Lipitor 10"].id, 0, 85.0, 90.0) # Out of stock
        ]
        
        for med_id, qty, price, mrp in inventory_to_seed:
            inventory_service.create_or_update_inventory(
                db=db,
                pharmacy_id=pharmacy_id,
                medicine_id=med_id,
                inventory_data=PharmacyInventoryUpdate(
                    stock_quantity=qty,
                    selling_price=price,
                    mrp=mrp,
                    batch_number="BCH-TEST99",
                    expiry_date=date.today() + timedelta(days=360),
                    is_available=(qty > 0)
                )
            )
            print(f" -> Stocked medicine ID {med_id} at pharmacy {pharmacy_id} with qty {qty}")

        # 4. Test fuzzy matching logic
        print("Step 4: Testing Medicine Matching Service...")
        queries = [
            "Tab Crocin 650mg",   # Exact brand + noise
            "Dolo 650",           # Exact brand
            "Amoxicillin 500",    # Generic name match
            "Lipitor 10 mg",      # Brand + noise
            "UnknownDrug 100"     # Missing catalog item
        ]
        
        for q in queries:
            match_res = medicine_matching_service.match_extracted_medicine(db, q)
            matched_med = match_res["medicine"]
            confidence = match_res["confidence"]
            alts = match_res["alternatives"]
            
            print(f"  Query: '{q}'")
            if matched_med:
                print(f"    -> Matched: {matched_med.brand_name} (Confidence: {confidence})")
                print(f"    -> Alternatives/Substitutes ({len(alts)}): {', '.join([a.brand_name for a in alts])}")
            else:
                print(f"    -> No match found (Max Confidence: {confidence})")
                print(f"    -> Alternatives/Substitutes ({len(alts)}): {', '.join([a.brand_name for a in alts])}")

        # 5. Test Stock and Safety Constraints
        print("Step 5: Testing Stock and Safety Constraints...")
        crocin_id = db_meds["Crocin 650"].id
        
        # Check stock for 10 pills (available)
        available, current_stock = inventory_service.check_stock(db, pharmacy_id, crocin_id, 10)
        print(f" -> Check stock for 10 Crocin: Available={available} (Current Stock={current_stock})")
        assert available == True, "10 Crocin should be available"
        
        # Check stock for 150 pills (insufficient)
        available, current_stock = inventory_service.check_stock(db, pharmacy_id, crocin_id, 150)
        print(f" -> Check stock for 150 Crocin: Available={available} (Current Stock={current_stock})")
        assert available == False, "150 Crocin should not be available"
        
        # Reserve stock (deduct 10)
        print(" -> Reserving 10 Crocin pills...")
        updated_item = inventory_service.reserve_stock(db, pharmacy_id, crocin_id, 10)
        print(f" -> New Stock Quantity: {updated_item.stock_quantity}")
        assert updated_item.stock_quantity == 90, "Stock should decrease to 90"
        
        # Try to over-reserve and catch error
        print(" -> Attempting to reserve 200 Crocin pills (expected to fail)...")
        try:
            inventory_service.reserve_stock(db, pharmacy_id, crocin_id, 200)
            print(" -> [FAIL] Stock reservation went negative!")
            assert False, "Stock reservation should have failed!"
        except ValueError as e:
            print(f" -> [PASS] Stock reservation blocked as expected: {str(e)}")

        # 6. Test background processing OCR matching link
        print("Step 6: Verifying Prescription Parsing & Catalog Matching Link...")
        # Create a dummy image path
        dummy_file_path = "uploads/prescriptions/dummy_matching_test.jpg"
        with open(dummy_file_path, "w") as f:
            f.write("Prescription OCR link test")
            
        # Get a customer user in database
        customer = db.query(User).first()
        assert customer is not None, "Run verify_prescription.py first to seed customer!"

        prescription = prescription_service.create_prescription_record(
            db=db,
            customer_id=customer.id,
            file_path=dummy_file_path,
            original_filename="presc_matching.jpg",
            pharmacy_id=pharmacy_id
        )
        print(f" -> Created Prescription (ID: {prescription.id})")
        
        # Override mock OCR service text for this run
        # We'll mock the get_ocr_engine text extraction to return "Rx\nTab Crocin 650\n1-0-1\n5 Days"
        # We can do this by executing background task directly with a mock sequence
        # However, to be robust we know the background task calls ocr_service.extract_text, 
        # which returns a random choice. Let's run the processing.
        prescription_service.process_prescription_background(prescription.id)
        
        db.refresh(prescription)
        print(" -> Background Parsing Complete.")
        print(f" -> Extracted items link matches:")
        
        items = db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription.id).all()
        for idx, item in enumerate(items, 1):
            print(f"    Item #{idx}: '{item.medicine_name}'")
            print(f"      - Matched Medicine ID: {item.medicine_id}")
            if item.medicine_id:
                matched_db_med = db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
                print(f"      - Resolved brand: {matched_db_med.brand_name}")
                print(f"      - Combined match confidence score: {item.confidence_score}")
            else:
                print("      - No catalog link established (Unresolved)")
                
        print("\n" + "=" * 60)
        print("CATALOG & INVENTORY VERIFICATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    verify_catalog_inventory()
