from pydantic import BaseModel
from typing import Optional
from app.schemas.user import UserCreate, UserProfile
from app.schemas.address import AddressCreate
from app.schemas.medical_info import MedicalInfoCreate
from app.schemas.emergency_contact import EmergencyContactCreate

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    user_info: UserCreate
    home_address: AddressCreate
    work_address: Optional[AddressCreate] = None
    medical_info: MedicalInfoCreate
    emergency_contact: EmergencyContactCreate

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str
