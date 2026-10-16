from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.prescription import VerificationStatus
from app.schemas.prescription_item import PrescriptionItemResponse

class PrescriptionBase(BaseModel):
    pharmacy_id: Optional[int] = None
    verification_status: VerificationStatus = VerificationStatus.UPLOADED
    pharmacist_comments: Optional[str] = None

class PrescriptionCreate(BaseModel):
    pharmacy_id: Optional[int] = None

class PrescriptionUpdate(BaseModel):
    verification_status: Optional[VerificationStatus] = None
    pharmacist_comments: Optional[str] = None

class PrescriptionResponse(PrescriptionBase):
    id: int
    customer_id: int
    uploaded_image_path: str
    original_filename: str
    extracted_text: Optional[str] = None
    overall_confidence: Optional[float] = None
    uploaded_at: datetime
    updated_at: datetime
    items: List[PrescriptionItemResponse] = []

    model_config = ConfigDict(from_attributes=True)

class PrescriptionReviewRequest(BaseModel):
    pharmacist_comments: Optional[str] = None
