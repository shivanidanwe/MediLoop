from pydantic import BaseModel, ConfigDict
from typing import Optional
from enum import Enum

class AddressType(str, Enum):
    HOME = "HOME"
    WORK = "WORK"

class AddressBase(BaseModel):
    address_type: AddressType
    house_number: str
    street: str
    city: str
    state: str
    pincode: str
    landmark: Optional[str] = None
    is_default_delivery: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    address_type: Optional[AddressType] = None
    house_number: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    landmark: Optional[str] = None
    is_default_delivery: Optional[bool] = None

class Address(AddressBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
