from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.core.database import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    generic_name = Column(String, nullable=False, index=True)
    brand_name = Column(String, nullable=False, index=True)
    manufacturer = Column(String, nullable=False)
    strength = Column(String, nullable=False)
    dosage_form = Column(String, nullable=False, index=True) # Tablet, Capsule, Syrup, etc.
    prescription_required = Column(Boolean, default=False, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
