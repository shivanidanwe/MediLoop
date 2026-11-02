from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.core.config import settings
from app.core.database import get_db
from app.services import auth_service
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency injection helper to retrieve the currently logged-in user from PostgreSQL.
    Strictly verifies JWT credentials and prevents unauthorized access.
    """
    if token:
        try:
            user = auth_service.get_current_user(db, token)
            if user and user.is_active:
                return user
        except Exception:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_pharmacist(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Pharmacist:
    """
    Dependency injection helper to retrieve the currently logged-in pharmacist from PostgreSQL.
    Strictly verifies JWT credentials and prevents unauthorized access.
    """
    if token:
        payload = decode_access_token(token)
        if payload and payload.get("sub"):
            try:
                pharmacist_id = int(payload.get("sub"))
                ph = db.query(Pharmacist).filter(Pharmacist.id == pharmacist_id, Pharmacist.is_active == True).first()
                if ph:
                    return ph
            except (ValueError, TypeError):
                pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Pharmacist not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
