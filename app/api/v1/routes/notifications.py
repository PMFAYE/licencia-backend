from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db import models
from app.schemas.notification_schema import NotificationOut, NotificationCreate
from app.api.v1.routes.users import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationOut])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(models.Notification)
        .order_by(models.Notification.created_at.desc())
        .limit(20)
        .all()
    )


@router.get("/unread-count")
def unread_notifications_count(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    count = (
        db.query(models.Notification)
        .filter(
            models.Notification.user_id == current_user["id"],
            models.Notification.read == False
        )
        .count()
    )
    return {"count": count}


@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    notif = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
        )
        .first()
    )

    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    notif.read = True
    db.commit()

    return {"message": "Notification marquée comme lue"}


@router.patch("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db.query(models.Notification).filter(
        models.Notification.user_id == current_user["id"],
        models.Notification.read == False
    ).update({models.Notification.read: True})

    db.commit()
    return {"message": "Toutes les notifications ont été lues"}
