from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections and notifications"""

    def __init__(self):
        # Map of user_id to set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        print(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)

            # Remove user entry if no connections remain
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

            print(f"User {user_id} disconnected. Remaining: {len(self.active_connections.get(user_id, []))}")

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user (all their connections)"""
        if user_id in self.active_connections:
            message_json = json.dumps(message)

            # Send to all connections for this user
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    print(f"Error sending to connection: {e}")
                    disconnected.add(connection)

            # Clean up failed connections
            for connection in disconnected:
                self.disconnect(connection, user_id)

    async def broadcast(self, message: dict, user_ids: Optional[Set[int]] = None):
        """Broadcast a message to multiple users"""
        if user_ids is None:
            user_ids = set(self.active_connections.keys())

        for user_id in user_ids:
            await self.send_personal_message(message, user_id)

    def get_connected_users(self) -> Set[int]:
        """Get set of all connected user IDs"""
        return set(self.active_connections.keys())

    def is_user_connected(self, user_id: int) -> bool:
        """Check if a user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global connection manager instance
manager = ConnectionManager()


# Notification helper functions

async def notify_booking_created(homeowner_id: int, craftsman_id: int, booking_data: dict):
    """Notify craftsman about new booking"""
    notification = {
        "type": "booking_created",
        "timestamp": datetime.utcnow().isoformat(),
        "data": booking_data
    }
    await manager.send_personal_message(notification, craftsman_id)


async def notify_booking_accepted(homeowner_id: int, craftsman_id: int, booking_data: dict):
    """Notify homeowner that booking was accepted"""
    notification = {
        "type": "booking_accepted",
        "timestamp": datetime.utcnow().isoformat(),
        "data": booking_data
    }
    await manager.send_personal_message(notification, homeowner_id)


async def notify_booking_status_change(user_ids: Set[int], booking_data: dict, status: str):
    """Notify users about booking status change"""
    notification = {
        "type": "booking_status_changed",
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "data": booking_data
    }
    await manager.broadcast(notification, user_ids)


async def notify_new_message(sender_id: int, recipient_id: int, message_data: dict):
    """Notify recipient about new message"""
    notification = {
        "type": "new_message",
        "timestamp": datetime.utcnow().isoformat(),
        "data": message_data
    }
    await manager.send_personal_message(notification, recipient_id)


async def notify_payment_confirmed(homeowner_id: int, booking_id: int, amount: float):
    """Notify homeowner about payment confirmation"""
    notification = {
        "type": "payment_confirmed",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "booking_id": booking_id,
            "amount": amount
        }
    }
    await manager.send_personal_message(notification, homeowner_id)


async def notify_review_received(craftsman_id: int, review_data: dict):
    """Notify craftsman about new review"""
    notification = {
        "type": "review_received",
        "timestamp": datetime.utcnow().isoformat(),
        "data": review_data
    }
    await manager.send_personal_message(notification, craftsman_id)


async def notify_verification_approved(craftsman_id: int, profile_id: int):
    """Notify craftsman about verification approval"""
    notification = {
        "type": "verification_approved",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "profile_id": profile_id,
            "message": "Your profile has been verified!"
        }
    }
    await manager.send_personal_message(notification, craftsman_id)
