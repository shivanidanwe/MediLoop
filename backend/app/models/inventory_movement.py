from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_number = Column(String(100), nullable=True)
    previous_quantity = Column(Integer, default=0, nullable=False)
    quantity_changed = Column(Integer, default=0, nullable=False)
    updated_quantity = Column(Integer, default=0, nullable=False)
    movement_type = Column(String(50), nullable=False)  # PURCHASE, SALE, ADJUSTMENT, DAMAGED, EXPIRED, RESTOCK
    reason = Column(Text, nullable=True)
    pharmacist_id = Column(Integer, ForeignKey("pharmacists.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    pharmacy = relationship("Pharmacy")
    medicine = relationship("Medicine")
    pharmacist = relationship("Pharmacist")

