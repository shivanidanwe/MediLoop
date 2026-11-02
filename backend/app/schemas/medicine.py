from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MedicineBase(BaseModel):
    generic_name: str
    brand_name: str
    manufacturer: str
    strength: str
    dosage_form: str
    prescription_required: bool = False
    description: Optional[str] = None
    image_url: Optional[str] = None

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    manufacturer: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    prescription_required: Optional[bool] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class MedicineResponse(MedicineBase):
    id: int
    price: Optional[float] = 45.0
    selling_price: Optional[float] = 45.0
    mrp: Optional[float] = 55.0
    stock_quantity: Optional[int] = 100
    stock: Optional[int] = 100
    reorder_level: Optional[int] = 20
    batch_number: Optional[str] = "BAT-2026-01"
    expiry_date: Optional[str] = None
    availability: Optional[str] = "In Stock"
    status: Optional[str] = "In Stock"
    category: Optional[str] = "General"
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
