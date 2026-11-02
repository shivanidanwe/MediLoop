from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    pharmacist_id = Column(Integer, ForeignKey("pharmacists.id", ondelete="CASCADE"), nullable=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, default="SYSTEM_ALERT", nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    action_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="notifications")
    pharmacist = relationship("Pharmacist", backref="notifications")
    pharmacy = relationship("Pharmacy", backref="notifications")
