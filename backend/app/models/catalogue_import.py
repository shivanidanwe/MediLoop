from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class CatalogueImport(Base):
    __tablename__ = "catalogue_imports"

    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(Integer, ForeignKey("pharmacies.id", ondelete="CASCADE"), nullable=True)
    pharmacist_id = Column(Integer, ForeignKey("pharmacists.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer, default=0, nullable=False)
    valid_rows = Column(Integer, default=0, nullable=False)
    invalid_rows = Column(Integer, default=0, nullable=False)
    added_count = Column(Integer, default=0, nullable=False)
    updated_count = Column(Integer, default=0, nullable=False)
    skipped_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="COMPLETED", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    errors = relationship("CatalogueImportError", back_populates="import_record", cascade="all, delete-orphan")


class CatalogueImportError(Base):
    __tablename__ = "catalogue_import_errors"

    id = Column(Integer, primary_key=True, index=True)
    import_id = Column(Integer, ForeignKey("catalogue_imports.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    medicine_name = Column(String(255), nullable=True)
    error_reason = Column(Text, nullable=False)
    raw_data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    import_record = relationship("CatalogueImport", back_populates="errors")

