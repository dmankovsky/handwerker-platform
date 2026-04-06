from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.services.websocket_manager import manager
import json

router = APIRouter(tags=["WebSocket"])


async def get_current_user_from_token(token: str, db: AsyncSession) -> User:
    """Get user from JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("user_id")

        if user_id is None:
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user

    except JWTError:
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time notifications

    Connect with: ws://localhost:8001/ws?token=YOUR_JWT_TOKEN

    Notification types:
    - booking_created: New booking request (craftsmen)
    - booking_accepted: Booking accepted (homeowners)
    - booking_status_changed: Booking status updated
    - new_message: New message received
    - payment_confirmed: Payment successful
    - review_received: New review (craftsmen)
    - verification_approved: Profile verified (craftsmen)
    """

    # Authenticate user
    user = await get_current_user_from_token(token, db)

    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Connect user
    await manager.connect(websocket, user.id)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": f"Connected as {user.full_name}",
            "user_id": user.id,
            "role": user.role.value
        })

        # Keep connection alive and handle incoming messages
        while True:
            # Receive message (ping/pong for keep-alive)
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle ping
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })

            except json.JSONDecodeError:
                # Ignore malformed messages
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
        print(f"User {user.id} disconnected from WebSocket")

    except Exception as e:
        print(f"WebSocket error for user {user.id}: {e}")
        manager.disconnect(websocket, user.id)
