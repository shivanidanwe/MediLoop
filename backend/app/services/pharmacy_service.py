from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.pharmacy import Pharmacy
from app.schemas.pharmacy import PharmacyCreate, PharmacyUpdate

def get_all_pharmacies(db: Session) -> List[Pharmacy]:
    """
    Retrieve all active pharmacies.
    """
    return db.query(Pharmacy).filter(Pharmacy.is_active == True).all()

def get_pharmacy_by_id(db: Session, pharmacy_id: int) -> Optional[Pharmacy]:
    """
    Retrieve a pharmacy by its ID.
    """
    return db.query(Pharmacy).filter(Pharmacy.id == pharmacy_id).first()

def get_nearby_pharmacies(db: Session, latitude: Optional[float] = None, longitude: Optional[float] = None) -> List[Pharmacy]:
    """
    Retrieve nearby active pharmacies. Geolocation implementation in the future;
    currently returns all active pharmacies.
    """
    return get_all_pharmacies(db)

def create_pharmacy(db: Session, pharmacy_data: PharmacyCreate) -> Pharmacy:
    """
    Create a new pharmacy record.
    """
    db_pharmacy = Pharmacy(**pharmacy_data.model_dump())
    db.add(db_pharmacy)
    db.commit()
    db.refresh(db_pharmacy)
    return db_pharmacy

def update_pharmacy(db: Session, pharmacy_id: int, pharmacy_data: PharmacyUpdate) -> Optional[Pharmacy]:
    """
    Update an existing pharmacy record.
    """
    db_pharmacy = get_pharmacy_by_id(db, pharmacy_id)
    if not db_pharmacy:
        return None
    for key, val in pharmacy_data.model_dump(exclude_unset=True).items():
        setattr(db_pharmacy, key, val)
    db.commit()
    db.refresh(db_pharmacy)
    return db_pharmacy
