from app.db import models
from app.core.websocket_manager import manager

async def notify_user(db, user_id, titre, message, type, lien=None):
    notif = models.Notification(
        user_id=user_id,
        titre=titre,
        message=message,
        type=type,
        lien=lien
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    # 🔥 PUSH temps réel
    await manager.send_personal_message(
        user_id,
        {
            "id": notif.id,
            "titre": notif.titre,
            "message": notif.message,
            "type": notif.type,
            "lien": notif.lien,
            "read": False,
            "created_at": notif.created_at.isoformat()
        }
    )
