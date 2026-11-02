from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.cart import CartStatus, CartItemSource
from app.schemas.medicine import MedicineResponse

class CartItemCreate(BaseModel):
    medicine_id: int
    quantity: int = 1
    source: CartItemSource = CartItemSource.MANUAL_SEARCH

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    medicine_id: int
    quantity: int
    unit_price: float
    total_price: float
    source: CartItemSource
    medicine: Optional[MedicineResponse] = None

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: int
    customer_id: int
    pharmacy_id: Optional[int] = None
    status: CartStatus
    subtotal: float
    discount: float
    delivery_fee: float
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[CartItemResponse] = []
    unavailable_medicines: List[str] = []
    prescription_text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
