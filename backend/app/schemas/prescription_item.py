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
    form: Optional[str] = None
    dosage_instructions: Optional[str] = None
    raw_evidence_text: Optional[str] = None
    is_ambiguous: Optional[bool] = False
    requires_review: Optional[bool] = False

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
