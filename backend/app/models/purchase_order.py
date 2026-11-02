from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class SupplierPurchaseOrder(Base):
    __tablename__ = "supplier_purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, index=True, nullable=False)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_name = Column(String, default="Apex Healthcare & Pharma Distributors Pvt Ltd", nullable=False)
    supplier_email = Column(String, default="procurement@apexpharma.in", nullable=False)
    supplier_phone = Column(String, default="+91 98450 88990", nullable=False)
    
    # Status: DRAFT, READY_FOR_SUPPLIER, SENT_TO_SUPPLIER, DELIVERED, CANCELLED
    status = Column(String, default="READY_FOR_SUPPLIER", nullable=False, index=True)
    
    # Itemized lines: list of dicts with medicine_id, name, current_stock, reorder_qty, wholesale_price, total
    items_json = Column(JSON, nullable=False)
    
    subtotal = Column(Float, nullable=False, default=0.0)
    tax_amount = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False, default=0.0)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    pharmacy = relationship("Pharmacy", backref="purchase_orders")
