from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.models.craftsman import CraftsmanProfile
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.api.dependencies import get_current_active_user
from app.services.email_service import EmailService
from app.services.websocket_manager import notify_booking_created, notify_booking_accepted, notify_booking_status_change

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new booking (homeowners only)"""
    # Verify craftsman exists
    result = await db.execute(
        select(User).where(User.id == booking_data.craftsman_id, User.role == UserRole.CRAFTSMAN)
    )
    craftsman = result.scalar_one_or_none()

    if not craftsman:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman not found"
        )

    # Get craftsman profile for hourly rate
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == craftsman.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman profile not found"
        )

    if not profile.accepts_bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Craftsman is not accepting bookings"
        )

    # Calculate estimated cost
    estimated_cost = None
    if booking_data.estimated_hours:
        estimated_cost = booking_data.estimated_hours * profile.hourly_rate

    # Create booking
    booking = Booking(
        homeowner_id=current_user.id,
        craftsman_id=craftsman.id,
        title=booking_data.title,
        description=booking_data.description,
        trade_type=booking_data.trade_type,
        service_address=booking_data.service_address,
        postal_code=booking_data.postal_code,
        city=booking_data.city,
        requested_date=booking_data.requested_date,
        estimated_hours=booking_data.estimated_hours,
        hourly_rate=profile.hourly_rate,
        estimated_cost=estimated_cost,
        status=BookingStatus.PENDING,
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    # Send email notification to craftsman
    try:
        await EmailService.send_booking_created_email(
            craftsman_email=craftsman.email,
            craftsman_name=craftsman.full_name,
            homeowner_name=current_user.full_name,
            booking_title=booking.title,
            booking_id=booking.id,
            requested_date=booking.requested_date.strftime("%d.%m.%Y %H:%M") if booking.requested_date else "TBD"
        )
    except Exception as e:
        print(f"Error sending booking created email: {e}")

    # Send WebSocket notification to craftsman
    try:
        await notify_booking_created(
            homeowner_id=current_user.id,
            craftsman_id=craftsman.id,
            booking_data={
                "id": booking.id,
                "title": booking.title,
                "homeowner_name": current_user.full_name,
                "requested_date": booking.requested_date.isoformat() if booking.requested_date else None,
                "estimated_cost": booking.estimated_cost
            }
        )
    except Exception as e:
        print(f"Error sending WebSocket notification: {e}")

    return BookingResponse.from_orm(booking)


@router.get("/", response_model=List[BookingResponse])
async def get_my_bookings(
    status_filter: BookingStatus | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's bookings (as homeowner or craftsman)"""
    query = select(Booking).where(
        or_(
            Booking.homeowner_id == current_user.id,
            Booking.craftsman_id == current_user.id
        )
    )

    if status_filter:
        query = query.where(Booking.status == status_filter)

    query = query.order_by(Booking.created_at.desc())

    result = await db.execute(query)
    bookings = result.scalars().all()

    return [BookingResponse.from_orm(b) for b in bookings]


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific booking"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Check access rights
    if booking.homeowner_id != current_user.id and booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this booking"
        )

    return BookingResponse.from_orm(booking)


@router.put("/{booking_id}/accept", response_model=BookingResponse)
async def accept_booking(
    booking_id: int,
    scheduled_date: datetime,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a booking (craftsmen only)"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Verify craftsman
    if booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the assigned craftsman for this booking"
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending bookings can be accepted"
        )

    booking.status = BookingStatus.ACCEPTED
    booking.scheduled_date = scheduled_date
    booking.accepted_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    # Send email notification to homeowner
    try:
        result = await db.execute(
            select(User).where(User.id == booking.homeowner_id)
        )
        homeowner = result.scalar_one_or_none()

        if homeowner:
            await EmailService.send_booking_accepted_email(
                homeowner_email=homeowner.email,
                homeowner_name=homeowner.full_name,
                craftsman_name=current_user.full_name,
                booking_title=booking.title,
                booking_id=booking.id,
                scheduled_date=booking.scheduled_date.strftime("%d.%m.%Y %H:%M")
            )
    except Exception as e:
        print(f"Error sending booking accepted email: {e}")

    # Send WebSocket notification to homeowner
    try:
        await notify_booking_accepted(
            homeowner_id=booking.homeowner_id,
            craftsman_id=current_user.id,
            booking_data={
                "id": booking.id,
                "title": booking.title,
                "craftsman_name": current_user.full_name,
                "scheduled_date": booking.scheduled_date.isoformat(),
                "status": booking.status.value
            }
        )
    except Exception as e:
        print(f"Error sending WebSocket notification: {e}")

    return BookingResponse.from_orm(booking)


@router.put("/{booking_id}/reject", response_model=BookingResponse)
async def reject_booking(
    booking_id: int,
    reason: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a booking (craftsmen only)"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the assigned craftsman for this booking"
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending bookings can be rejected"
        )

    booking.status = BookingStatus.REJECTED
    booking.cancellation_reason = reason

    await db.commit()
    await db.refresh(booking)

    return BookingResponse.from_orm(booking)


@router.put("/{booking_id}/start", response_model=BookingResponse)
async def start_booking(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark booking as in progress (craftsmen only)"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the assigned craftsman"
        )

    if booking.status != BookingStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only accepted bookings can be started"
        )

    booking.status = BookingStatus.IN_PROGRESS

    await db.commit()
    await db.refresh(booking)

    return BookingResponse.from_orm(booking)


@router.put("/{booking_id}/complete", response_model=BookingResponse)
async def complete_booking(
    booking_id: int,
    actual_hours: float,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark booking as completed (craftsmen only)"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the assigned craftsman"
        )

    if booking.status != BookingStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only in-progress bookings can be completed"
        )

    booking.status = BookingStatus.COMPLETED
    booking.actual_hours = actual_hours
    booking.final_cost = actual_hours * booking.hourly_rate
    booking.completed_at = datetime.utcnow()

    # Update craftsman stats
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.total_jobs += 1

    await db.commit()
    await db.refresh(booking)

    # Send email notification to homeowner
    try:
        result = await db.execute(
            select(User).where(User.id == booking.homeowner_id)
        )
        homeowner = result.scalar_one_or_none()

        if homeowner:
            await EmailService.send_booking_completed_email(
                homeowner_email=homeowner.email,
                homeowner_name=homeowner.full_name,
                craftsman_name=current_user.full_name,
                booking_title=booking.title,
                booking_id=booking.id,
                final_cost=booking.final_cost
            )
    except Exception as e:
        print(f"Error sending booking completed email: {e}")

    # Send WebSocket notification to both users
    try:
        await notify_booking_status_change(
            user_ids={booking.homeowner_id, booking.craftsman_id},
            booking_data={
                "id": booking.id,
                "title": booking.title,
                "final_cost": booking.final_cost,
                "craftsman_name": current_user.full_name
            },
            status="completed"
        )
    except Exception as e:
        print(f"Error sending WebSocket notification: {e}")

    return BookingResponse.from_orm(booking)


@router.put("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    reason: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a booking (homeowner or craftsman)"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Check access
    if booking.homeowner_id != current_user.id and booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this booking"
        )

    # Only certain statuses can be cancelled
    if booking.status in [BookingStatus.COMPLETED, BookingStatus.PAID, BookingStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel booking with status {booking.status.value}"
        )

    booking.status = BookingStatus.CANCELLED
    booking.cancellation_reason = reason
    booking.cancelled_at = datetime.utcnow()

    await db.commit()
    await db.refresh(booking)

    return BookingResponse.from_orm(booking)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update booking details"""
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Check access
    if booking.homeowner_id != current_user.id and booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this booking"
        )

    # Update fields
    update_data = booking_data.dict(exclude_unset=True)

    # Only craftsman can update craftsman_notes
    if "craftsman_notes" in update_data and booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only craftsman can update craftsman notes"
        )

    # Only homeowner can update homeowner_notes
    if "homeowner_notes" in update_data and booking.homeowner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only homeowner can update homeowner notes"
        )

    for field, value in update_data.items():
        setattr(booking, field, value)

    await db.commit()
    await db.refresh(booking)

    return BookingResponse.from_orm(booking)
