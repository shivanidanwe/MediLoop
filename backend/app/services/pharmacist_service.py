from sqlalchemy.orm import Session
from typing import Optional
from app.models.pharmacist import Pharmacist
from app.schemas.pharmacist import PharmacistCreate
from app.core.security import hash_password, verify_password

def create_pharmacist(db: Session, pharmacist_data: PharmacistCreate) -> Pharmacist:
    """
    Create a new pharmacist record belonging to a pharmacy.
    """
    hashed_pwd = hash_password(pharmacist_data.password)
    # Exclude password during mapping
    data_dict = pharmacist_data.model_dump(exclude={"password"})
    db_pharmacist = Pharmacist(**data_dict, hashed_password=hashed_pwd)
    db.add(db_pharmacist)
    db.commit()
    db.refresh(db_pharmacist)
    return db_pharmacist

def get_pharmacist_by_id(db: Session, pharmacist_id: int) -> Optional[Pharmacist]:
    """
    Retrieve a pharmacist by their ID.
    """
    return db.query(Pharmacist).filter(Pharmacist.id == pharmacist_id).first()

def authenticate_pharmacist(db: Session, email: str, password: str) -> Optional[Pharmacist]:
    """
    Authenticate a pharmacist by email and password.
    Returns the Pharmacist model if credentials match, else None.
    """
    pharmacist = db.query(Pharmacist).filter(Pharmacist.email == email).first()
    if not pharmacist:
        return None
    if not verify_password(password, pharmacist.hashed_password):
        return None
    return pharmacist
