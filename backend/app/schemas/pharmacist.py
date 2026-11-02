from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PharmacistBase(BaseModel):
    pharmacy_id: int
    full_name: str
    registration_number: str
    email: str
    mobile_number: str
    designation: str = "Pharmacist"
    is_active: bool = True

class PharmacistCreate(PharmacistBase):
    password: str

class PharmacistUpdate(BaseModel):
    pharmacy_id: Optional[int] = None
    full_name: Optional[str] = None
    registration_number: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    designation: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class Pharmacist(PharmacistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    pharmacy_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PharmacistResponse(Pharmacist):
    pass
