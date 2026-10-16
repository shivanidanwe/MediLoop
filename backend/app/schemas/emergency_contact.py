from pydantic import BaseModel, ConfigDict
from typing import Optional

class EmergencyContactBase(BaseModel):
    relationship: str
    contact_number: str

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactUpdate(BaseModel):
    relationship: Optional[str] = None
    contact_number: Optional[str] = None

class EmergencyContact(EmergencyContactBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
