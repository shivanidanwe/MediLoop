from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime
from app.models.order import OrderStatus
from app.schemas.medicine import MedicineResponse

class OrderItemCreate(BaseModel):
    medicine_id: int
    quantity: int = 1
    unit_price: Optional[float] = None
    total_price: Optional[float] = None

class OrderCreate(BaseModel):
    address_id: int
    payment_method: str # e.g. COD, CARD, UPI
    pharmacy_id: Optional[int] = None
    prescription_id: Optional[int] = None
    idempotency_key: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = None

class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None

class OrderDraftItem(BaseModel):
    medicine_id: Optional[int] = None
    medicine_name: str
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    quantity: int = 1
    unit_price: float = 0.0
    total_price: float = 0.0
    prescription_required: bool = False
    requires_review: bool = False
    is_ambiguous: bool = False
    evidence_text: Optional[str] = None

class OrderDraftCreate(BaseModel):
    pharmacy_id: Optional[int] = None
    prescription_id: Optional[int] = None
    items: List[OrderDraftItem]
    allergy_warning: Optional[str] = None

class OrderDraftConfirmRequest(BaseModel):
    draft_id: str
    address_id: Optional[int] = None
    payment_method: Optional[str] = "COD"
    idempotency_key: Optional[str] = None

class OrderDraftResponse(BaseModel):
    id: str
    customer_id: int
    pharmacy_id: Optional[int] = None
    prescription_id: Optional[int] = None
    items: List[Dict[str, Any]] = []
    total_estimated_amount: float
    status: str
    allergy_warning: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    medicine_id: int
    quantity: int
    unit_price: float
    total_price: float
    medicine_name: Optional[str] = None
    manufacturer: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    image_url: Optional[str] = None
    medicine: Optional[MedicineResponse] = None

    model_config = ConfigDict(from_attributes=True)

class OrderAuditEventResponse(BaseModel):
    id: int
    order_id: int
    actor_id: Optional[int] = None
    actor_role: str
    previous_state: Optional[str] = None
    new_state: str
    action: str
    reason_or_note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    pharmacy_id: int
    cart_id: Optional[int] = None
    prescription_id: Optional[int] = None
    address_id: Optional[int] = None
    payment_method: str
    payment_status: str
    order_status: OrderStatus
    total_amount: float
    estimated_delivery_time: Optional[datetime] = None
    placed_at: datetime
    updated_at: datetime
    rejection_reason: Optional[str] = None
    idempotency_key: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    audit_events: List[OrderAuditEventResponse] = []
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    delivery_address: Optional[str] = None
    prescription_image_url: Optional[str] = None
    subtotal: Optional[float] = None
    discount: Optional[float] = 0.0
    delivery_charges: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)
