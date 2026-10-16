from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.services import auth_service
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency injection helper to retrieve the currently logged-in user.
    """
    return auth_service.get_current_user(db, token)

def get_current_pharmacist(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Pharmacist:
    """
    Dependency injection helper to retrieve the currently logged-in pharmacist.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    pharmacist_id_str = payload.get("sub")
    if not pharmacist_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        pharmacist_id = int(pharmacist_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid pharmacist ID format in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    pharmacist = db.query(Pharmacist).filter(Pharmacist.id == pharmacist_id).first()
    if not pharmacist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pharmacist not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return pharmacist

