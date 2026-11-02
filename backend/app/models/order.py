import enum
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base

class OrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_PATIENT_CONFIRMATION = "PENDING_PATIENT_CONFIRMATION"
    SUBMITTED = "SUBMITTED"
    RECEIVED = "RECEIVED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    PENDING_PHARMACIST_REVIEW = "PENDING_PHARMACIST_REVIEW"
    PRESCRIPTION_APPROVED = "PRESCRIPTION_APPROVED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    PREPARING = "PREPARING"
    READY = "READY"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="RESTRICT"), nullable=False, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="SET NULL"), nullable=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    address_id = Column(Integer, ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)
    payment_method = Column(String, nullable=False) # e.g. COD, CARD, UPI
    payment_status = Column(String, default="PENDING", nullable=False) # e.g. PENDING, PAID, REFUNDED
    order_status = Column(String(64), default=OrderStatus.PENDING_VERIFICATION.value, nullable=False)
    total_amount = Column(Float, nullable=False)
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)
    placed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    rejection_reason = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=True, index=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer = relationship("User", backref="orders")
    pharmacy = relationship("Pharmacy", backref="orders")
    address = relationship("Address", backref="orders")
    prescription = relationship("Prescription", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    audit_events = relationship("OrderAuditEvent", back_populates="order", cascade="all, delete-orphan")

    @property
    def customer_name(self):
        if self.customer and self.customer.full_name:
            return self.customer.full_name.strip()
        return None

    @property
    def customer_phone(self):
        if self.customer:
            return self.customer.mobile_number
        return None

    @property
    def customer_email(self):
        if self.customer:
            return self.customer.email
        return None

    @property
    def delivery_address(self):
        addr = self.address
        if not addr and self.customer and self.customer.addresses:
            addr = self.customer.addresses[0]
        if addr:
            parts = [addr.house_number, addr.street, addr.city, addr.state, addr.pincode]
            return ", ".join([str(p).strip() for p in parts if p and str(p).strip()])
        return "pandharpur, Maharashtra"

    @property
    def prescription_image_url(self):
        if self.prescription_id:
            return f"http://localhost:8000/api/v1/prescriptions/{self.prescription_id}/image"
        return None

    @property
    def subtotal(self):
        if self.items:
            return sum(item.quantity * item.unit_price for item in self.items)
        return self.total_amount or 0.0

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    medicine = relationship("Medicine")

    @property
    def medicine_name(self):
        if self.medicine:
            return self.medicine.brand_name or self.medicine.generic_name
        return f"Medicine #{self.medicine_id}"

    @property
    def manufacturer(self):
        if self.medicine:
            return self.medicine.manufacturer
        return "MediLoop Pharma"

    @property
    def strength(self):
        if self.medicine:
            return self.medicine.strength
        return ""

    @property
    def dosage_form(self):
        if self.medicine:
            return self.medicine.dosage_form
        return "Tablet"

    @property
    def image_url(self):
        if self.medicine:
            return self.medicine.image_url
        return None

class OrderAuditEvent(Base):
    __tablename__ = "order_audit_events"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_id = Column(Integer, nullable=True)
    actor_role = Column(String(50), nullable=False)
    previous_state = Column(String(64), nullable=True)
    new_state = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    reason_or_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    order = relationship("Order", back_populates="audit_events")

class OrderDraft(Base):
    __tablename__ = "order_drafts"

    id = Column(String(64), primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="SET NULL"), nullable=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id", ondelete="SET NULL"), nullable=True)
    items_json = Column(JSONB, nullable=False)
    total_estimated_amount = Column(Float, default=0.0, nullable=False)
    status = Column(String(64), default="DRAFT", nullable=False)
    allergy_warning = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    customer = relationship("User")
    pharmacy = relationship("Pharmacy")
    prescription = relationship("Prescription")
