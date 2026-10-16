from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
import sqlalchemy.orm as orm
from app.core.database import Base

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    relationship = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = orm.relationship("User", back_populates="emergency_contact")
