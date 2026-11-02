import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class VerificationStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REQUIRES_CLARIFICATION = "REQUIRES_CLARIFICATION"

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="SET NULL"), nullable=True)
    uploaded_image_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    extracted_text = Column(String, nullable=True)
    overall_confidence = Column(Float, nullable=True)
    verification_status = Column(
        SQLEnum(VerificationStatus), 
        default=VerificationStatus.UPLOADED, 
        nullable=False
    )
    pharmacist_comments = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    verified_by_pharmacist_id = Column(Integer, ForeignKey("pharmacists.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    clarification_requested_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String, nullable=True)
    ocr_engine = Column(String, nullable=True)

    # Relationships
    customer = relationship("User", backref="prescriptions")
    pharmacy = relationship("Pharmacy", backref="prescriptions")
    verified_by_pharmacist = relationship("Pharmacist", foreign_keys=[verified_by_pharmacist_id])
    items = relationship(
        "PrescriptionItem", 
        back_populates="prescription", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )

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
    def customer_gender(self):
        if self.customer and self.customer.gender:
            return self.customer.gender.value if hasattr(self.customer.gender, "value") else str(self.customer.gender)
        return None

    @property
    def customer_age(self):
        if self.customer and self.customer.date_of_birth:
            from datetime import date
            today = date.today()
            dob = self.customer.date_of_birth
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None

    @property
    def delivery_address(self):
        if self.customer and self.customer.addresses:
            addr = self.customer.addresses[0]
            parts = [addr.house_number, addr.street, addr.city, addr.state, addr.pincode]
            return ", ".join([str(p).strip() for p in parts if p and str(p).strip()])
        return None

class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(
        Integer, 
        ForeignKey("prescriptions.id", ondelete="CASCADE"), 
        nullable=False
    )
    medicine_name = Column(String, nullable=False)
    strength = Column(String, nullable=True)
    dosage_pattern = Column(String, nullable=True)
    frequency = Column(Integer, nullable=True)
    duration_days = Column(Integer, nullable=True)
    calculated_quantity = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)

    medicine_id = Column(
        Integer, 
        ForeignKey("medicines.id", ondelete="SET NULL"), 
        nullable=True
    )

    form = Column(String, nullable=True)
    dosage_instructions = Column(String, nullable=True)
    raw_evidence_text = Column(String, nullable=True)
    is_ambiguous = Column(Boolean, default=False, nullable=True)
    requires_review = Column(Boolean, default=False, nullable=True)

    # Relationships
    prescription = relationship("Prescription", back_populates="items")
    medicine = relationship("Medicine")
