import sys
import os

# Add parent directory to python path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.models.user import User

client = TestClient(app)

def cleanup_test_user(email: str):
    """Cleanup test user if they already exist in database."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.delete(user)
            db.commit()
            print(f"Cleaned up existing test user: {email}")
    except Exception as e:
        db.rollback()
        print(f"Failed to cleanup test user: {e}")
    finally:
        db.close()

def main():
    test_email = "testuser@mediloop.com"
    cleanup_test_user(test_email)

    print("\n--- Phase 1: Register User ---")
    register_payload = {
        "user_info": {
            "full_name": "Test User",
            "email": test_email,
            "mobile_number": "9876543210",
            "password": "securepassword123",
            "date_of_birth": "1995-08-15",
            "gender": "MALE",
            "profile_image": "http://example.com/profile.png"
        },
        "home_address": {
            "address_type": "HOME",
            "house_number": "A-12",
            "street": "Green Valley Road",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "landmark": "Near Central Park",
            "is_default_delivery": True
        },
        "medical_info": {
            "medical_conditions": "Hypertension, Asthma",
            "allergies": "Penicillin"
        },
        "emergency_contact": {
            "relationship": "Spouse",
            "contact_number": "9876543211"
        }
    }

    response = client.post("/api/auth/register", json=register_payload)
    if response.status_code == 201:
        print("Registration Successful!")
        print("Response JSON:")
        import pprint
        pprint.pprint(response.json())
    else:
        print(f"Registration Failed! Status code: {response.status_code}")
        print("Error details:", response.text)
        sys.exit(1)

    print("\n--- Phase 2: Login User ---")
    login_payload = {
        "email": test_email,
        "password": "securepassword123"
    }
    response = client.post("/api/auth/login", json=login_payload)
    if response.status_code == 200:
        print("Login Successful!")
        data = response.json()
        token = data.get("access_token")
        print(f"Token: {token[:30]}...")
    else:
        print(f"Login Failed! Status code: {response.status_code}")
        print("Error details:", response.text)
        sys.exit(1)

    print("\n--- Phase 3: Get Current User profile (/auth/me) ---")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = client.get("/api/auth/me", headers=headers)
    if response.status_code == 200:
        print("Get Current User profile Successful!")
        import pprint
        pprint.pprint(response.json())
    else:
        print(f"Get Current User profile Failed! Status code: {response.status_code}")
        print("Error details:", response.text)
        sys.exit(1)

    print("\nAll integration verification tests passed successfully!")

if __name__ == "__main__":
    main()
