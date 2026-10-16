from pydantic import BaseModel, ConfigDict
from typing import Optional

class PrescriptionItemBase(BaseModel):
    medicine_name: str
    strength: Optional[str] = None
    dosage_pattern: Optional[str] = None
    frequency: Optional[int] = None
    duration_days: Optional[int] = None
    calculated_quantity: Optional[int] = None
    confidence_score: Optional[float] = None

class PrescriptionItemCreate(PrescriptionItemBase):
    pass

class PrescriptionItemUpdate(BaseModel):
    medicine_name: Optional[str] = None
    strength: Optional[str] = None
    dosage_pattern: Optional[str] = None
    frequency: Optional[int] = None
    duration_days: Optional[int] = None
    calculated_quantity: Optional[int] = None
    confidence_score: Optional[float] = None

class PrescriptionItemResponse(PrescriptionItemBase):
    id: int
    prescription_id: int

    model_config = ConfigDict(from_attributes=True)
