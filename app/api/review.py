from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.models.review import Review
from app.models.craftsman import CraftsmanProfile
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewResponseCreate
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a review for a completed booking (homeowners only)"""
    # Get booking
    result = await db.execute(
        select(Booking).where(Booking.id == review_data.booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Verify homeowner
    if booking.homeowner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review your own bookings"
        )

    # Verify booking is completed or paid
    if booking.status not in [BookingStatus.COMPLETED, BookingStatus.PAID]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review completed bookings"
        )

    # Check if review already exists
    result = await db.execute(
        select(Review).where(Review.booking_id == booking.id)
    )
    existing_review = result.scalar_one_or_none()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review already exists for this booking"
        )

    # Create review
    review = Review(
        booking_id=booking.id,
        reviewer_id=current_user.id,
        craftsman_id=booking.craftsman_id,
        rating=review_data.rating,
        quality_rating=review_data.quality_rating,
        communication_rating=review_data.communication_rating,
        punctuality_rating=review_data.punctuality_rating,
        value_rating=review_data.value_rating,
        title=review_data.title,
        comment=review_data.comment,
        is_verified=True,  # Verified because it's from a real booking
    )

    db.add(review)

    # Update craftsman profile stats
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == booking.craftsman_id)
    )
    profile = result.scalar_one_or_none()

    if profile:
        # Calculate new average rating
        result = await db.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.craftsman_id == booking.craftsman_id, Review.is_visible == True)
        )
        avg_rating, total_reviews = result.one()

        # Include the new review
        if avg_rating:
            new_avg = ((avg_rating * total_reviews) + review_data.rating) / (total_reviews + 1)
        else:
            new_avg = review_data.rating

        profile.average_rating = round(new_avg, 2)
        profile.total_reviews = (total_reviews or 0) + 1

    await db.commit()
    await db.refresh(review)

    return ReviewResponse.from_orm(review)


@router.get("/craftsman/{craftsman_id}", response_model=List[ReviewResponse])
async def get_craftsman_reviews(
    craftsman_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get all visible reviews for a craftsman"""
    result = await db.execute(
        select(Review)
        .where(Review.craftsman_id == craftsman_id, Review.is_visible == True)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reviews = result.scalars().all()

    return [ReviewResponse.from_orm(r) for r in reviews]


@router.get("/booking/{booking_id}", response_model=ReviewResponse)
async def get_booking_review(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get review for a specific booking"""
    result = await db.execute(
        select(Review).where(Review.booking_id == booking_id)
    )
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    # Get booking to check access
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    # Allow access to reviewer, craftsman, or if review is visible
    if not review.is_visible and (
        booking.homeowner_id != current_user.id and
        booking.craftsman_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this review"
        )

    return ReviewResponse.from_orm(review)


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a review (reviewer only)"""
    result = await db.execute(
        select(Review).where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews"
        )

    # Update fields
    update_data = review_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    # Recalculate craftsman stats if rating changed
    if "rating" in update_data:
        result = await db.execute(
            select(CraftsmanProfile).where(CraftsmanProfile.user_id == review.craftsman_id)
        )
        profile = result.scalar_one_or_none()

        if profile:
            result = await db.execute(
                select(func.avg(Review.rating))
                .where(Review.craftsman_id == review.craftsman_id, Review.is_visible == True)
            )
            avg_rating = result.scalar_one()
            profile.average_rating = round(avg_rating or 0, 2)

    await db.commit()
    await db.refresh(review)

    return ReviewResponse.from_orm(review)


@router.post("/{review_id}/respond", response_model=ReviewResponse)
async def respond_to_review(
    review_id: int,
    response_data: ReviewResponseCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Respond to a review (craftsman only)"""
    result = await db.execute(
        select(Review).where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    if review.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only respond to reviews about you"
        )

    if review.response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already responded to this review"
        )

    review.response = response_data.response
    review.response_date = datetime.utcnow()

    await db.commit()
    await db.refresh(review)

    return ReviewResponse.from_orm(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a review (reviewer only, marks as not visible)"""
    result = await db.execute(
        select(Review).where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )

    # Mark as not visible instead of deleting
    review.is_visible = False

    # Update craftsman stats
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == review.craftsman_id)
    )
    profile = result.scalar_one_or_none()

    if profile:
        result = await db.execute(
            select(func.avg(Review.rating), func.count(Review.id))
            .where(Review.craftsman_id == review.craftsman_id, Review.is_visible == True)
        )
        avg_rating, total_reviews = result.one()

        profile.average_rating = round(avg_rating or 0, 2)
        profile.total_reviews = total_reviews or 0

    await db.commit()
