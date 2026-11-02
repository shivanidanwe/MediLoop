from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    pharmacist_id = Column(Integer, ForeignKey("pharmacists.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    new_prescription = Column(Boolean, default=True, nullable=False)
    new_orders = Column(Boolean, default=True, nullable=False)
    low_stock = Column(Boolean, default=True, nullable=False)
    out_of_stock = Column(Boolean, default=True, nullable=False)
    new_stock = Column(Boolean, default=True, nullable=False)
    expiry_alerts = Column(Boolean, default=True, nullable=False)
    order_updates = Column(Boolean, default=True, nullable=False)
    sound_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    pharmacist = relationship("Pharmacist")

