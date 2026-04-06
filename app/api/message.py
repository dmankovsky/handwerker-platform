from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.booking import Booking
from app.models.message import Message, MessageThread
from app.schemas.message import MessageCreate, MessageResponse, MessageThreadResponse
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/api/messages", tags=["Messages"])


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message in a booking conversation"""
    # Get booking
    result = await db.execute(
        select(Booking).where(Booking.id == message_data.booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Verify user is part of the booking
    if booking.homeowner_id != current_user.id and booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this booking conversation"
        )

    # Determine recipient
    recipient_id = booking.craftsman_id if current_user.id == booking.homeowner_id else booking.homeowner_id

    # Get or create message thread
    result = await db.execute(
        select(MessageThread).where(MessageThread.booking_id == booking.id)
    )
    thread = result.scalar_one_or_none()

    if not thread:
        thread = MessageThread(booking_id=booking.id)
        db.add(thread)
        await db.flush()

    # Create message
    message = Message(
        thread_id=thread.id,
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=message_data.content
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return MessageResponse.from_orm(message)


@router.get("/threads", response_model=List[MessageThreadResponse])
async def get_message_threads(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all message threads for current user"""
    # Get bookings where user is involved
    result = await db.execute(
        select(Booking).where(
            or_(
                Booking.homeowner_id == current_user.id,
                Booking.craftsman_id == current_user.id
            )
        )
    )
    bookings = result.scalars().all()
    booking_ids = [b.id for b in bookings]

    # Get threads for these bookings
    result = await db.execute(
        select(MessageThread)
        .where(MessageThread.booking_id.in_(booking_ids))
        .options(selectinload(MessageThread.messages))
        .order_by(MessageThread.updated_at.desc())
    )
    threads = result.scalars().all()

    # Build response with unread counts
    response = []
    for thread in threads:
        # Get unread count
        unread_result = await db.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.thread_id == thread.id,
                    Message.recipient_id == current_user.id,
                    Message.is_read == False
                )
            )
        )
        unread_count = unread_result.scalar_one()

        # Get booking info
        booking = next((b for b in bookings if b.id == thread.booking_id), None)

        thread_response = MessageThreadResponse(
            id=thread.id,
            booking_id=thread.booking_id,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
            booking_title=booking.title if booking else None,
            booking_status=booking.status.value if booking else None,
            messages=[MessageResponse.from_orm(m) for m in thread.messages],
            unread_count=unread_count
        )
        response.append(thread_response)

    return response


@router.get("/booking/{booking_id}", response_model=MessageThreadResponse)
async def get_booking_messages(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a specific booking"""
    # Get booking
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Verify access
    if booking.homeowner_id != current_user.id and booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this conversation"
        )

    # Get thread
    result = await db.execute(
        select(MessageThread)
        .where(MessageThread.booking_id == booking_id)
        .options(selectinload(MessageThread.messages))
    )
    thread = result.scalar_one_or_none()

    if not thread:
        # Return empty thread if no messages yet
        return MessageThreadResponse(
            id=0,
            booking_id=booking_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            booking_title=booking.title,
            booking_status=booking.status.value,
            messages=[],
            unread_count=0
        )

    # Mark messages as read
    result = await db.execute(
        select(Message).where(
            and_(
                Message.thread_id == thread.id,
                Message.recipient_id == current_user.id,
                Message.is_read == False
            )
        )
    )
    unread_messages = result.scalars().all()

    for msg in unread_messages:
        msg.is_read = True
        msg.read_at = datetime.utcnow()

    await db.commit()

    # Get unread count
    unread_result = await db.execute(
        select(func.count(Message.id))
        .where(
            and_(
                Message.thread_id == thread.id,
                Message.recipient_id == current_user.id,
                Message.is_read == False
            )
        )
    )
    unread_count = unread_result.scalar_one()

    return MessageThreadResponse(
        id=thread.id,
        booking_id=thread.booking_id,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        booking_title=booking.title,
        booking_status=booking.status.value,
        messages=[MessageResponse.from_orm(m) for m in thread.messages],
        unread_count=unread_count
    )


@router.put("/{message_id}/read", response_model=MessageResponse)
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a message as read"""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )

    if message.recipient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only mark your own messages as read"
        )

    if not message.is_read:
        message.is_read = True
        message.read_at = datetime.utcnow()
        await db.commit()
        await db.refresh(message)

    return MessageResponse.from_orm(message)


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get total unread message count for current user"""
    result = await db.execute(
        select(func.count(Message.id))
        .where(
            and_(
                Message.recipient_id == current_user.id,
                Message.is_read == False
            )
        )
    )
    unread_count = result.scalar_one()

    return {"unread_count": unread_count}
