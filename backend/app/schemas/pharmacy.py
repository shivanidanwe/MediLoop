from pydantic import BaseModel, ConfigDict
from datetime import time, datetime
from typing import Optional, List
from app.schemas.pharmacist import Pharmacist

class PharmacyBase(BaseModel):
    pharmacy_name: str
    license_number: str
    email: str
    phone_number: str
    address: str
    city: str
    state: str
    pincode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_time: time
    closing_time: time
    supports_home_delivery: bool = True
    estimated_delivery_minutes: int = 30
    is_active: bool = True

class PharmacyCreate(PharmacyBase):
    pass

class PharmacyUpdate(BaseModel):
    pharmacy_name: Optional[str] = None
    license_number: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    supports_home_delivery: Optional[bool] = None
    estimated_delivery_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class Pharmacy(PharmacyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PharmacyDetail(Pharmacy):
    pharmacists: List[Pharmacist] = []

    model_config = ConfigDict(from_attributes=True)

class PharmacyResponse(Pharmacy):
    pass
