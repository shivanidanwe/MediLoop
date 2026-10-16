from pydantic import BaseModel, ConfigDict
from typing import Optional

class MedicalInfoBase(BaseModel):
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None

class MedicalInfoCreate(MedicalInfoBase):
    pass

class MedicalInfoUpdate(BaseModel):
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None

class MedicalInfo(MedicalInfoBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
