from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.schemas.medicine import MedicineResponse

class PharmacyInventoryBase(BaseModel):
    pharmacy_id: int
    medicine_id: int
    stock_quantity: int = 0
    selling_price: float
    mrp: float
    batch_number: str
    expiry_date: date
    is_available: bool = True

class PharmacyInventoryCreate(PharmacyInventoryBase):
    pass

class PharmacyInventoryUpdate(BaseModel):
    stock_quantity: Optional[int] = None
    selling_price: Optional[float] = None
    mrp: Optional[float] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    is_available: Optional[bool] = None

class PharmacyInventoryResponse(PharmacyInventoryBase):
    id: int
    updated_at: datetime
    medicine: Optional[MedicineResponse] = None

    model_config = ConfigDict(from_attributes=True)

class StockCheckRequest(BaseModel):
    pharmacy_id: int
    medicine_id: int
    quantity: int

class StockCheckResponse(BaseModel):
    pharmacy_id: int
    medicine_id: int
    requested_quantity: int
    available_quantity: int
    is_available: bool
