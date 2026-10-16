import sys
import os

# Add parent directory to python path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.pharmacy import Pharmacy
from app.models.pharmacist import Pharmacist

client = TestClient(app)

def cleanup_test_pharmacy(license_number: str):
    """Cleanup test data if it already exists in database."""
    db = SessionLocal()
    try:
        pharmacy = db.query(Pharmacy).filter(Pharmacy.license_number == license_number).first()
        if pharmacy:
            # Cascading delete will remove pharmacists automatically
            db.delete(pharmacy)
            db.commit()
            print(f"Cleaned up existing test pharmacy: {license_number}")
    except Exception as e:
        db.rollback()
        print(f"Failed to cleanup test pharmacy: {e}")
    finally:
        db.close()

def main():
    test_license = "RX-TEST-999"
    cleanup_test_pharmacy(test_license)

    print("\n--- Phase 1: Create Pharmacy ---")
    pharmacy_payload = {
        "pharmacy_name": "MediLoop Smart Pharmacy",
        "license_number": test_license,
        "email": "contact@medilooppharmacy.com",
        "phone_number": "18005550199",
        "address": "456 Healthcare Blvd",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400002",
        "latitude": 19.076,
        "longitude": 72.877,
        "opening_time": "08:00:00",
        "closing_time": "22:00:00",
        "supports_home_delivery": True,
        "is_active": True
    }

    response = client.post("/api/pharmacies", json=pharmacy_payload)
    if response.status_code == 201:
        print("Pharmacy Creation Successful!")
        pharmacy_data = response.json()
        pharmacy_id = pharmacy_data.get("id")
        print(f"Pharmacy ID: {pharmacy_id}")
    else:
        print(f"Pharmacy Creation Failed! Status code: {response.status_code}")
        print("Error details:", response.text)
        sys.exit(1)

    print("\n--- Phase 2: Create Pharmacist ---")
    pharmacist_payload = {
        "pharmacy_id": pharmacy_id,
        "full_name": "Dr. Jane Doe",
        "registration_number": "RPH-9999",
        "email": "janedoe@medilooppharmacy.com",
        "mobile_number": "9876549999",
        "password": "pharmacistpassword123",
        "is_active": True
    }

    response = client.post("/api/pharmacies/pharmacists", json=pharmacist_payload)
    if response.status_code == 201:
        print("Pharmacist Creation Successful!")
        pharmacist_data = response.json()
        pharmacist_id = pharmacist_data.get("id")
        print(f"Pharmacist ID: {pharmacist_id}")
    else:
        print(f"Pharmacist Creation Failed! Status code: {response.status_code}")
        print("Error details:", response.text)
        sys.exit(1)

    print("\n--- Phase 3: Get All Pharmacies ---")
    response = client.get("/api/pharmacies")
    if response.status_code == 200:
        print("Get All Pharmacies Successful!")
        import pprint
        pprint.pprint(response.json())
    else:
        print(f"Get All Pharmacies Failed! Status code: {response.status_code}")
        sys.exit(1)

    print("\n--- Phase 4: Get Nearby Pharmacies ---")
    response = client.get("/api/pharmacies/nearby?latitude=19.076&longitude=72.877")
    if response.status_code == 200:
        print("Get Nearby Pharmacies Successful!")
        import pprint
        pprint.pprint(response.json())
    else:
        print(f"Get Nearby Pharmacies Failed! Status code: {response.status_code}")
        sys.exit(1)

    print("\n--- Phase 5: Get Pharmacy By ID (with nested pharmacists) ---")
    response = client.get(f"/api/pharmacies/{pharmacy_id}")
    if response.status_code == 200:
        print("Get Pharmacy By ID Successful!")
        import pprint
        pprint.pprint(response.json())
    else:
        print(f"Get Pharmacy By ID Failed! Status code: {response.status_code}")
        sys.exit(1)

    print("\nAll integration verification tests for Pharmacy Module passed successfully!")

if __name__ == "__main__":
    main()
