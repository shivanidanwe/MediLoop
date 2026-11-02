from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime


class SupplierPurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    pharmacy_id: int
    supplier_name: str
    supplier_email: str
    supplier_phone: str
    status: str
    items_json: List[Dict[str, Any]]
    subtotal: float
    tax_amount: float
    total_amount: float
    notes: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
