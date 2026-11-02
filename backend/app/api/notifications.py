from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import oauth2_scheme
from app.core.security import decode_access_token
from app.models.user import User
from app.models.pharmacist import Pharmacist
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_current_actor(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Union[User, Pharmacist]:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = payload.get("sub")
    role = payload.get("role")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub_id = int(sub)
    if role == "pharmacist":
        p = db.query(Pharmacist).filter(Pharmacist.id == sub_id).first()
        if p:
            return p
    elif role in ("patient", "user", "customer"):
        u = db.query(User).filter(User.id == sub_id).first()
        if u:
            return u

    p = db.query(Pharmacist).filter(Pharmacist.id == sub_id).first()
    if p:
        return p
    u = db.query(User).filter(User.id == sub_id).first()
    if u:
        return u

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Actor associated with token not found",
        headers={"WWW-Authenticate": "Bearer"},
    )

class NotificationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    pharmacist_id: Optional[int] = None
    pharmacy_id: Optional[int] = None
    title: str
    message: str
    notification_type: str
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificationPreferenceSchema(BaseModel):
    new_prescription: bool = True
    new_orders: bool = True
    low_stock: bool = True
    out_of_stock: bool = True
    new_stock: bool = True
    expiry_alerts: bool = True
    order_updates: bool = True
    sound_enabled: bool = True

    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    limit: int = 50,
    category: Optional[str] = None,
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    """
    Retrieves operational notifications for the logged in user or pharmacist.
    """
    query = db.query(Notification)

    if isinstance(current_actor, Pharmacist):
        query = query.filter(
            (Notification.pharmacist_id == current_actor.id) |
            (Notification.pharmacy_id == current_actor.pharmacy_id) |
            (Notification.pharmacy_id == None)
        )
    else:
        query = query.filter(Notification.user_id == current_actor.id)

    if category and category.upper() != "ALL":
        query = query.filter(Notification.notification_type.ilike(f"%{category}%"))

    return query.order_by(Notification.created_at.desc()).limit(limit).all()

@router.get("/unread-count")
def get_unread_count(
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    """
    Returns unread notification badge count for the header bell.
    """
    query = db.query(Notification).filter(Notification.is_read == False)
    if isinstance(current_actor, Pharmacist):
        query = query.filter(
            (Notification.pharmacist_id == current_actor.id) |
            (Notification.pharmacy_id == current_actor.pharmacy_id) |
            (Notification.pharmacy_id == None)
        )
    else:
        query = query.filter(Notification.user_id == current_actor.id)

    count = query.count()
    return {"unread_count": count}

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif

@router.post("/mark-all-read")
def mark_all_notifications_as_read(
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    query = db.query(Notification).filter(Notification.is_read == False)
    if isinstance(current_actor, Pharmacist):
        query = query.filter(
            (Notification.pharmacist_id == current_actor.id) |
            (Notification.pharmacy_id == current_actor.pharmacy_id) |
            (Notification.pharmacy_id == None)
        )
    else:
        query = query.filter(Notification.user_id == current_actor.id)

    query.update({"is_read": True}, synchronize_session=False)
    db.commit()
    return {"message": "All notifications marked as read."}

@router.get("/preferences", response_model=NotificationPreferenceSchema)
def get_notification_preferences(
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    if not isinstance(current_actor, Pharmacist):
        return NotificationPreferenceSchema()

    pref = db.query(NotificationPreference).filter(
        NotificationPreference.pharmacist_id == current_actor.id
    ).first()

    if not pref:
        pref = NotificationPreference(pharmacist_id=current_actor.id)
        db.add(pref)
        db.commit()
        db.refresh(pref)

    return pref

@router.put("/preferences", response_model=NotificationPreferenceSchema)
def update_notification_preferences(
    payload: NotificationPreferenceSchema,
    current_actor: Union[User, Pharmacist] = Depends(get_current_actor),
    db: Session = Depends(get_db)
):
    if not isinstance(current_actor, Pharmacist):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only pharmacists have dashboard notification preferences.")

    pref = db.query(NotificationPreference).filter(
        NotificationPreference.pharmacist_id == current_actor.id
    ).first()

    if not pref:
        pref = NotificationPreference(pharmacist_id=current_actor.id)
        db.add(pref)

    for k, v in payload.model_dump().items():
        setattr(pref, k, v)

    db.commit()
    db.refresh(pref)
    return pref
