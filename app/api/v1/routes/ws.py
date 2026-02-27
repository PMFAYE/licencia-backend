from fastapi import APIRouter, WebSocket, Depends
from app.core.websocket_manager import manager
from app.api.v1.routes.users import get_current_user_ws

router = APIRouter()

@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    current_user=Depends(get_current_user_ws),
):
    print(current_user)
    user_id = current_user["id"]
    await manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()  # keep alive
    except:
        manager.disconnect(user_id, websocket)
