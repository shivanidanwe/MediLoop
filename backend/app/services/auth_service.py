import random
import os
import logging
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.models.user import User, Gender
from app.models.address import Address, AddressType
from app.models.medical_info import MedicalInfo
from app.models.emergency_contact import EmergencyContact
from app.schemas.auth import UserRegister
from app.schemas.user import UserProfileUpdate
from app.core.security import hash_password, verify_password, decode_access_token, validate_password_strength

logger = logging.getLogger(__name__)

# In-memory OTP storage mapping email -> {"otp": str, "expires_at": datetime}
_otp_store = {}

def register_user(db: Session, register_data: UserRegister) -> User:
    """
    Registers a new user and creates their associated profiles:
    - Home Address
    - Work Address (copied from Home if not provided)
    - Medical Information
    - Emergency Contact
    All actions run within a single atomic transaction.
    """
    # 1. Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == register_data.user_info.email) | 
        (User.mobile_number == register_data.user_info.mobile_number)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or mobile number already registered."
        )

    try:
        # 2. Create User
        hashed_pwd = hash_password(register_data.user_info.password)
        db_user = User(
            full_name=register_data.user_info.full_name,
            email=register_data.user_info.email,
            mobile_number=register_data.user_info.mobile_number,
            hashed_password=hashed_pwd,
            date_of_birth=register_data.user_info.date_of_birth,
            gender=register_data.user_info.gender,
            profile_image=register_data.user_info.profile_image,
            is_active=True
        )
        db.add(db_user)
        db.flush()  # Gain access to db_user.id

        # 3. Create Home Address
        home_addr = Address(
            user_id=db_user.id,
            address_type=AddressType.HOME,
            house_number=register_data.home_address.house_number,
            street=register_data.home_address.street,
            city=register_data.home_address.city,
            state=register_data.home_address.state,
            pincode=register_data.home_address.pincode,
            landmark=register_data.home_address.landmark,
            is_default_delivery=register_data.home_address.is_default_delivery
        )
        db.add(home_addr)

        # 4. Create Work Address
        work_data = register_data.work_address or register_data.home_address
        work_addr = Address(
            user_id=db_user.id,
            address_type=AddressType.WORK,
            house_number=work_data.house_number,
            street=work_data.street,
            city=work_data.city,
            state=work_data.state,
            pincode=work_data.pincode,
            landmark=work_data.landmark,
            is_default_delivery=False if register_data.work_address else False
        )
        db.add(work_addr)

        # 5. Create Medical Info
        med_info = MedicalInfo(
            user_id=db_user.id,
            medical_conditions=register_data.medical_info.medical_conditions,
            allergies=register_data.medical_info.allergies
        )
        db.add(med_info)

        # 6. Create Emergency Contact
        em_contact = EmergencyContact(
            user_id=db_user.id,
            relationship=register_data.emergency_contact.relationship,
            contact_number=register_data.emergency_contact.contact_number
        )
        db.add(em_contact)

        # Commit transaction
        db.commit()
        db.refresh(db_user)
        return db_user

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}"
        )

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    Returns the User model if credentials match, else None.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_current_user(db: Session, token: str) -> User:
    """
    Decodes the JWT access token and returns the current user model.
    Raises HTTPException (401 Unauthorized) if credentials validation fails.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def update_user_profile(db: Session, db_user: User, update_data: UserProfileUpdate) -> User:
    """
    Updates user personal details, addresses, medical info, and emergency contact.
    All actions run within a single atomic transaction.
    """
    try:
        # 1. Update personal details
        if update_data.user_info:
            user_info = update_data.user_info
            
            # Check unique constraints if email or mobile is changing
            if user_info.email and user_info.email != db_user.email:
                existing_email = db.query(User).filter(User.email == user_info.email).first()
                if existing_email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered."
                    )
                db_user.email = user_info.email
                
            if user_info.mobile_number and user_info.mobile_number != db_user.mobile_number:
                existing_mobile = db.query(User).filter(User.mobile_number == user_info.mobile_number).first()
                if existing_mobile:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Mobile number already registered."
                    )
                db_user.mobile_number = user_info.mobile_number
            
            if user_info.full_name is not None:
                db_user.full_name = user_info.full_name
            if user_info.date_of_birth is not None:
                db_user.date_of_birth = user_info.date_of_birth
            if user_info.gender is not None:
                db_user.gender = user_info.gender
            if user_info.profile_image is not None:
                db_user.profile_image = user_info.profile_image
            if user_info.password is not None:
                db_user.hashed_password = hash_password(user_info.password)
                
        # 2. Update/create Home Address
        if update_data.home_address:
            home_addr = db.query(Address).filter(
                Address.user_id == db_user.id,
                Address.address_type == AddressType.HOME
            ).first()
            
            if home_addr:
                for key, val in update_data.home_address.model_dump(exclude_unset=True).items():
                    setattr(home_addr, key, val)
            else:
                home_addr = Address(
                    user_id=db_user.id,
                    address_type=AddressType.HOME,
                    **update_data.home_address.model_dump()
                )
                db.add(home_addr)
                
        # 3. Update/create Work Address
        if update_data.work_address:
            work_addr = db.query(Address).filter(
                Address.user_id == db_user.id,
                Address.address_type == AddressType.WORK
            ).first()
            
            if work_addr:
                for key, val in update_data.work_address.model_dump(exclude_unset=True).items():
                    setattr(work_addr, key, val)
            else:
                work_addr = Address(
                    user_id=db_user.id,
                    address_type=AddressType.WORK,
                    **update_data.work_address.model_dump()
                )
                db.add(work_addr)
                
        # 4. Update/create Medical Info
        if update_data.medical_info:
            med_info = db.query(MedicalInfo).filter(MedicalInfo.user_id == db_user.id).first()
            if med_info:
                for key, val in update_data.medical_info.model_dump(exclude_unset=True).items():
                    setattr(med_info, key, val)
            else:
                med_info = MedicalInfo(
                    user_id=db_user.id,
                    **update_data.medical_info.model_dump()
                )
                db.add(med_info)
                
        # 5. Update/create Emergency Contact
        if update_data.emergency_contact:
            em_contact = db.query(EmergencyContact).filter(EmergencyContact.user_id == db_user.id).first()
            if em_contact:
                for key, val in update_data.emergency_contact.model_dump(exclude_unset=True).items():
                    setattr(em_contact, key, val)
            else:
                em_contact = EmergencyContact(
                    user_id=db_user.id,
                    **update_data.emergency_contact.model_dump()
                )
                db.add(em_contact)
                
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Sends real-time email containing OTP for Password Reset.
    Falls back gracefully if SMTP variables are not configured in environment.
    """
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    from_email = os.getenv("SMTP_FROM_EMAIL", smtp_user or "no-reply@mediloop.com")

    body = (
        f"Hello,\n\n"
        f"Your MediLoop Password Reset Verification Code (OTP) is: {otp}\n\n"
        f"This code will expire in 10 minutes. If you did not request a password reset, please ignore this email.\n\n"
        f"Regards,\nMediLoop Healthcare Platform Security Team"
    )

    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEText(body)
            msg['Subject'] = 'MediLoop Password Reset OTP Verification'
            msg['From'] = from_email
            msg['To'] = to_email

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(from_email, [to_email], msg.as_string())
            logger.info(f"Successfully dispatched OTP email to {to_email}")
            return True
        except Exception as e:
            logger.warning(f"Failed to send email via SMTP ({e}). Fallback to system logger.")

    logger.info(f"REALTIME MAIL OTP GENERATED FOR [{to_email}]: {otp}")
    return True

def generate_forgot_password_otp(db: Session, email: str) -> str:
    """
    Validates user exists and generates a 6-digit OTP code for password reset.
    """
    clean_email = email.trim().lower() if hasattr(email, 'trim') else email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account registered with this email address."
        )

    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    _otp_store[clean_email] = {
        "otp": otp_code,
        "expires_at": expires_at
    }

    send_otp_email(clean_email, otp_code)
    return otp_code

def verify_forgot_password_otp(email: str, otp: str) -> bool:
    """
    Verifies if provided OTP is valid and unexpired for the given email.
    """
    clean_email = email.strip().lower()
    clean_otp = otp.strip()

    record = _otp_store.get(clean_email)
    if not record:
        return False

    if datetime.now(timezone.utc) > record["expires_at"]:
        _otp_store.pop(clean_email, None)
        return False

    return record["otp"] == clean_otp

def reset_password_with_otp(db: Session, email: str, otp: str, new_password: str) -> bool:
    """
    Resets user password after verifying OTP and password strength.
    """
    clean_email = email.strip().lower()
    if not verify_forgot_password_otp(clean_email, otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP verification code."
        )

    validate_password_strength(new_password)

    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    user.hashed_password = hash_password(new_password)
    db.commit()

    # Invalidate OTP after use
    _otp_store.pop(clean_email, None)
    return True

