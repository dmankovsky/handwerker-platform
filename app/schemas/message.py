from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    booking_id: int
    content: str = Field(..., min_length=1, max_length=2000)


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    thread_id: int
    sender_id: int
    recipient_id: int
    content: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    # Sender info
    sender_name: Optional[str] = None

    class Config:
        from_attributes = True


class MessageThreadResponse(BaseModel):
    """Schema for message thread response"""
    id: int
    booking_id: int
    created_at: datetime
    updated_at: datetime

    # Related booking info
    booking_title: Optional[str] = None
    booking_status: Optional[str] = None

    # Messages in thread
    messages: List[MessageResponse] = []

    # Unread count for current user
    unread_count: int = 0

    class Config:
        from_attributes = True
