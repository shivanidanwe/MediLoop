from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date
from enum import Enum
from app.schemas.address import Address, AddressUpdate
from app.schemas.medical_info import MedicalInfo, MedicalInfoUpdate
from app.schemas.emergency_contact import EmergencyContact, EmergencyContactUpdate

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class UserBase(BaseModel):
    full_name: str
    email: str
    mobile_number: str
    date_of_birth: date
    gender: Gender
    profile_image: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    profile_image: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class UserProfile(User):
    addresses: List[Address] = []
    medical_info: Optional[MedicalInfo] = None
    emergency_contact: Optional[EmergencyContact] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserProfileUpdate(BaseModel):
    user_info: Optional[UserUpdate] = None
    home_address: Optional[AddressUpdate] = None
    work_address: Optional[AddressUpdate] = None
    medical_info: Optional[MedicalInfoUpdate] = None
    emergency_contact: Optional[EmergencyContactUpdate] = None

