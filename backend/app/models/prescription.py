import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class VerificationStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

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

    # Relationships
    customer = relationship("User", backref="prescriptions")
    pharmacy = relationship("Pharmacy", backref="prescriptions")
    items = relationship(
        "PrescriptionItem", 
        back_populates="prescription", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )

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

    # Relationships
    prescription = relationship("Prescription", back_populates="items")
    medicine = relationship("Medicine")
