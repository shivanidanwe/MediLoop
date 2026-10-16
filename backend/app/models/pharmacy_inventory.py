from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class PharmacyInventory(Base):
    __tablename__ = "pharmacy_inventory"

    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(
        Integer, 
        ForeignKey("pharmacies.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    medicine_id = Column(
        Integer, 
        ForeignKey("medicines.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    stock_quantity = Column(Integer, default=0, nullable=False)
    selling_price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=False)
    batch_number = Column(String, nullable=False)
    expiry_date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    pharmacy = relationship("Pharmacy", backref="inventory_items")
    medicine = relationship("Medicine", backref="inventory_items")
