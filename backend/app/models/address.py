import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class AddressType(str, enum.Enum):
    HOME = "HOME"
    WORK = "WORK"

class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    address_type = Column(SQLEnum(AddressType), nullable=False)
    house_number = Column(String, nullable=False)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    pincode = Column(String, nullable=False)
    landmark = Column(String, nullable=True)
    is_default_delivery = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="addresses")
