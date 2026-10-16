import sys
import os

# Add the parent directory of backend/app to path to resolve imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User, Gender
from app.models.pharmacy import Pharmacy
from app.models.address import Address, AddressType
from app.models.medicine import Medicine
from app.models.pharmacy_inventory import PharmacyInventory
from app.models.prescription import Prescription, PrescriptionItem, VerificationStatus
from app.models.cart import Cart, CartItem, CartStatus, CartItemSource
from app.models.order import Order, OrderItem, OrderStatus
from app.services import (
    prescription_service, 
    cart_service, 
    order_service, 
    inventory_service
)
from app.schemas.pharmacy_inventory import PharmacyInventoryUpdate
from datetime import date, timedelta, time as dtime

def verify_cart_order():
    print("=" * 70)
    print("MediLoop Cart & Order Management Verification Suite")
    print("=" * 70)

    # 1. Re-create all database tables to clear states
    print("Step 1: Dropping and re-creating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Monkeypatch MockOCRAngine for deterministic verification
    from app.services.ocr_service import MockOCRAngine
    MockOCRAngine.extract_text = lambda self, path: (
        "Rx\nTab Crocin 650\n1-0-1\n5 Days\n\nTab Amoxicillin 500\n1-1-1\n7 Days",
        0.95
    )
    
    try:
        # 2. Seed dependencies (User, Address, Pharmacy)
        print("Step 2: Seeding core dependency rows...")
        customer = User(
            full_name="Jane Doe",
            email="jane.doe@mediloop.com",
            mobile_number="+15555551234",
            hashed_password="mocked_password_hash",
            date_of_birth=date(1995, 5, 5),
            gender=Gender.FEMALE
        )
        db.add(customer)
        db.flush() # get customer.id
        
        address = Address(
            user_id=customer.id,
            address_type=AddressType.HOME,
            house_number="Apt 4B",
            street="Prescription Lane",
            city="Healthy Town",
            state="Wellness State",
            pincode="987654"
        )
        db.add(address)
        
        pharmacy = Pharmacy(
            pharmacy_name="MediLoop Neighborhood Pharmacy",
            license_number="LIC-8888777",
            email="neighborhood@mediloop.com",
            phone_number="+15559998888",
            address="456 Care Blvd",
            city="Healthy Town",
            state="Wellness State",
            pincode="987654",
            opening_time=dtime(9, 0),
            closing_time=dtime(21, 0)
        )
        db.add(pharmacy)
        db.commit()
        db.refresh(customer)
        db.refresh(address)
        db.refresh(pharmacy)
        print(f" -> Customer seeded (ID: {customer.id})")
        print(f" -> Address seeded (ID: {address.id})")
        print(f" -> Pharmacy seeded (ID: {pharmacy.id})")

        # 3. Seed catalog medicines
        print("Step 3: Seeding medicines catalog...")
        crocin = Medicine(
            brand_name="Crocin 650", generic_name="Paracetamol", 
            manufacturer="GSK", strength="650 mg", dosage_form="Tablet", 
            prescription_required=False, description="Analgesic"
        )
        amoxil = Medicine(
            brand_name="Amoxil 500", generic_name="Amoxicillin", 
            manufacturer="Alkem", strength="500 mg", dosage_form="Capsule", 
            prescription_required=True, description="Antibiotic"
        )
        dolo = Medicine(
            brand_name="Dolo 650", generic_name="Paracetamol", 
            manufacturer="Micro Labs", strength="650 mg", dosage_form="Tablet", 
            prescription_required=False, description="Antipyretic"
        )
        db.add(crocin)
        db.add(amoxil)
        db.add(dolo)
        db.commit()
        db.refresh(crocin)
        db.refresh(amoxil)
        db.refresh(dolo)
        print(f" -> Seeding Catalog complete (Crocin ID: {crocin.id}, Amoxil ID: {amoxil.id}, Dolo ID: {dolo.id})")

        # 4. Seed Inventory stock
        print("Step 4: Seeding stock levels...")
        # Crocin: 100 tablets, 35.0 each
        inventory_service.create_or_update_inventory(
            db, pharmacy.id, crocin.id, 
            PharmacyInventoryUpdate(stock_quantity=100, selling_price=35.0, mrp=35.0, batch_number="BCH-C1", expiry_date=date.today()+timedelta(days=365))
        )
        # Amoxil: 20 capsules, 120.0 each (Notice this is less than the prescription calculated requirement of 21)
        inventory_service.create_or_update_inventory(
            db, pharmacy.id, amoxil.id, 
            PharmacyInventoryUpdate(stock_quantity=20, selling_price=120.0, mrp=120.0, batch_number="BCH-A1", expiry_date=date.today()+timedelta(days=365))
        )
        # Dolo: 50 tablets, 30.0 each
        inventory_service.create_or_update_inventory(
            db, pharmacy.id, dolo.id, 
            PharmacyInventoryUpdate(stock_quantity=50, selling_price=30.0, mrp=30.0, batch_number="BCH-D1", expiry_date=date.today()+timedelta(days=365))
        )
        print(" -> Seeding Inventory complete.")

        # 5. Create and approve prescription (triggers auto-cart creation)
        print("Step 5: Uploading and approving mock prescription...")
        dummy_file = "uploads/prescriptions/dummy_cart_test.jpg"
        os.makedirs("uploads/prescriptions", exist_ok=True)
        with open(dummy_file, "w") as f:
            f.write("OCR cart test")
            
        prescription = prescription_service.create_prescription_record(
            db=db,
            customer_id=customer.id,
            file_path=dummy_file,
            original_filename="jane_prescription.jpg",
            pharmacy_id=pharmacy.id
        )
        
        # Manually run background task
        prescription_service.process_prescription_background(prescription.id)
        db.refresh(prescription)
        
        # Approve prescription
        print(" -> Pharmacist approving prescription...")
        prescription_service.approve_prescription(db, prescription.id, "Prescription approved.")
        
        # Refresh cart
        cart = db.query(Cart).filter(Cart.customer_id == customer.id, Cart.status == CartStatus.ACTIVE).first()
        print(f" -> Active Cart automatically created (ID: {cart.id}, Subtotal: {cart.subtotal}, Total: {cart.total_amount})")
        print(f" -> Cart Items details:")
        for idx, item in enumerate(cart.items, 1):
            print(f"    Item #{idx}: Medicine ID: {item.medicine_id}, Qty: {item.quantity}, Price: {item.unit_price}, Source: {item.source.value}")
            
        assert len(cart.items) == 2, "Cart should contain 2 prescription items"

        # 6. Test manual additions
        print("Step 6: Adding a manual search medicine to the cart (Dolo 650)...")
        cart_service.add_item_to_cart(db, customer.id, dolo.id, quantity=5, source=CartItemSource.MANUAL_SEARCH)
        db.refresh(cart)
        print(f" -> Cart Items count after addition: {len(cart.items)}")
        print(f" -> New subtotal: {cart.subtotal}")
        
        # Update quantity of manual addition
        print(" -> Updating quantity of Dolo 650 item to 10...")
        dolo_cart_item = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.medicine_id == dolo.id).first()
        cart_service.update_cart_item(db, customer.id, dolo_cart_item.id, quantity=10)
        db.refresh(cart)
        print(f" -> New subtotal after update: {cart.subtotal}")
        assert dolo_cart_item.quantity == 10, "Dolo quantity should update to 10"

        # 7. Test atomic transaction safety (checkout should abort due to insufficient stock of Amoxil)
        print("Step 7: Placing order - testing atomic transaction rollback (Amoxil stock is 20, but Cart requires 21)...")
        try:
            order_service.create_order_from_cart(
                db=db,
                customer_id=customer.id,
                address_id=address.id,
                payment_method="COD"
            )
            print(" -> [FAIL] Order creation should have failed due to stock boundaries!")
            assert False, "Overselling stock must not be permitted!"
        except ValueError as e:
            print(f" -> [PASS] Order placement aborted and transaction rolled back successfully: {str(e)}")
            
        # Verify that stock levels are UNCHANGED
        crocin_inv = inventory_service.get_inventory_item(db, pharmacy.id, crocin.id)
        print(f" -> Verify Crocin stock after failed order: {crocin_inv.stock_quantity} (Expected: 100)")
        assert crocin_inv.stock_quantity == 100, "Stock reservation must rollback on abort!"

        # 8. Re-stock and verify successful order placement
        print("Step 8: Re-stocking Amoxil (updating stock to 50) and retrying order creation...")
        inventory_service.create_or_update_inventory(
            db, pharmacy.id, amoxil.id, 
            PharmacyInventoryUpdate(stock_quantity=50)
        )
        
        order = order_service.create_order_from_cart(
            db=db,
            customer_id=customer.id,
            address_id=address.id,
            payment_method="COD"
        )
        print(f" -> [PASS] Order placed successfully!")
        print(f" -> Order Number: {order.order_number}")
        print(f" -> Order Status: {order.order_status.value}")
        print(f" -> Order Total Amount: {order.total_amount}")
        
        # Verify that cart is marked CHECKED_OUT
        db.refresh(cart)
        print(f" -> Cart Status: {cart.status.value}")
        assert cart.status == CartStatus.CHECKED_OUT, "Cart should be CHECKED_OUT"
        
        # Verify inventory stock deduction
        db.refresh(crocin_inv)
        amoxil_inv = inventory_service.get_inventory_item(db, pharmacy.id, amoxil.id)
        dolo_inv = inventory_service.get_inventory_item(db, pharmacy.id, dolo.id)
        
        print(f" -> Verify final inventory stocks:")
        print(f"    - Crocin: {crocin_inv.stock_quantity} (Expected: 90 [100 - 10])")
        print(f"    - Amoxil: {amoxil_inv.stock_quantity} (Expected: 29 [50 - 21])")
        print(f"    - Dolo: {dolo_inv.stock_quantity} (Expected: 40 [50 - 10])")
        
        assert crocin_inv.stock_quantity == 90
        assert amoxil_inv.stock_quantity == 29
        assert dolo_inv.stock_quantity == 40

        # 9. Test order status transitions
        print("Step 9: Testing Pharmacist order status updates...")
        order_service.update_order_status(db, order.id, OrderStatus.PREPARING)
        db.refresh(order)
        print(f" -> Order Status after update: {order.order_status.value}")
        assert order.order_status == OrderStatus.PREPARING
        
        # Test cancel order (re-stocks items)
        print(" -> Cancelling order (verifying stock restoration)...")
        order_service.update_order_status(db, order.id, OrderStatus.CANCELLED)
        db.refresh(crocin_inv)
        db.refresh(amoxil_inv)
        db.refresh(dolo_inv)
        print(f" -> Stocks after cancel:")
        print(f"    - Crocin: {crocin_inv.stock_quantity} (Expected: 100)")
        print(f"    - Amoxil: {amoxil_inv.stock_quantity} (Expected: 50)")
        print(f"    - Dolo: {dolo_inv.stock_quantity} (Expected: 50)")
        
        assert crocin_inv.stock_quantity == 100
        assert amoxil_inv.stock_quantity == 50
        assert dolo_inv.stock_quantity == 50

        print("\n" + "=" * 70)
        print("CART & ORDER MANAGEMENT MODULE VERIFIED SUCCESSFULLY!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] Verification failed: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    verify_cart_order()
