# app/schemas/notification_schema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationOut(BaseModel):
    id: int
    titre: str
    message: str
    type: str
    lien: Optional[str]
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    user_id: int
    titre: str
    message: str
    type: str
    lien: Optional[str] = None
