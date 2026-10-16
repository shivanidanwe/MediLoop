from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus
from app.schemas.medicine import MedicineResponse

class OrderCreate(BaseModel):
    address_id: int
    payment_method: str # e.g. COD, CARD, UPI

class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    medicine_id: int
    quantity: int
    unit_price: float
    total_price: float
    medicine: Optional[MedicineResponse] = None

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    pharmacy_id: int
    cart_id: Optional[int] = None
    address_id: Optional[int] = None
    payment_method: str
    payment_status: str
    order_status: OrderStatus
    total_amount: float
    estimated_delivery_time: Optional[datetime] = None
    placed_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
