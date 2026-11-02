from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import UserRegister, LoginRequest, LoginResponse, Token, ForgotPasswordRequest, VerifyOtpRequest, ResetPasswordRequest
from app.schemas.user import UserProfile, UserProfileUpdate
from app.schemas.pharmacist import PharmacistResponse
from app.services import auth_service, pharmacist_service
from pydantic import BaseModel

class PharmacistLoginResponse(BaseModel):
    access_token: str
    token_type: str
    pharmacist: PharmacistResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def register(register_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user profile including addresses, medical info, and emergency contacts.
    Runs inside a single atomic transaction.
    """
    db_user = auth_service.register_user(db, register_data)
    return db_user

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint to authenticate credentials and receive a JWT access token.
    """
    db_user = auth_service.authenticate_user(db, login_data.email, login_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token with user.id as subject and role
    access_token = create_access_token(subject=str(db_user.id), role="patient")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve the profile details of the currently authenticated user.
    """
    return current_user

@router.put("/me", response_model=UserProfile)
def update_me(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the profile details of the currently authenticated user.
    """
    updated_user = auth_service.update_user_profile(db, current_user, update_data)
    return updated_user

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Generates and dispatches a 6-digit real-time OTP code to user's registered email.
    """
    auth_service.generate_forgot_password_otp(db, data.email)
    return {
        "success": True,
        "message": f"Verification OTP code sent to {data.email}"
    }

@router.post("/verify-otp")
def verify_otp(data: VerifyOtpRequest):
    """
    Verifies if provided OTP code matches and is unexpired.
    """
    is_valid = auth_service.verify_forgot_password_otp(data.email, data.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP code."
        )
    return {"success": True, "message": "OTP verification successful."}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Resets user password upon successful OTP verification.
    """
    auth_service.reset_password_with_otp(db, data.email, data.otp, data.new_password)
    return {"success": True, "message": "Password reset successfully. You can now login with your new credentials."}

@router.post("/pharmacist/login", response_model=PharmacistLoginResponse)
def pharmacist_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint for pharmacists to authenticate and receive a JWT access token.
    """
    db_pharmacist = pharmacist_service.authenticate_pharmacist(db, login_data.email, login_data.password)
    if not db_pharmacist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token with pharmacist.id as subject and role
    access_token = create_access_token(subject=str(db_pharmacist.id), role="pharmacist")
    pharmacist_resp = PharmacistResponse.model_validate(db_pharmacist)
    if db_pharmacist.pharmacy:
        pharmacist_resp.pharmacy_name = db_pharmacist.pharmacy.pharmacy_name

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "pharmacist": pharmacist_resp
    }
