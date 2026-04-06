from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.models.craftsman import CraftsmanProfile
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import (
    StripeConnectOnboardingRequest,
    StripeConnectOnboardingResponse,
    StripeAccountStatusResponse,
    PaymentIntentRequest,
    PaymentIntentResponse,
    PaymentConfirmRequest,
    PayoutRequest,
    PayoutResponse,
    PaymentResponse,
)
from app.api.dependencies import get_current_active_user
from app.services.stripe_service import StripeService
from app.core.config import settings

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/connect/onboarding", response_model=StripeConnectOnboardingResponse)
async def create_stripe_connect_onboarding(
    onboarding_data: StripeConnectOnboardingRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create Stripe Connect onboarding link for craftsman
    (Craftsmen only)
    """
    if current_user.role != UserRole.CRAFTSMAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only craftsmen can connect Stripe accounts"
        )

    # Get craftsman profile
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman profile not found"
        )

    # Create or retrieve Stripe account
    if not profile.stripe_account_id:
        account_data = await StripeService.create_connected_account(
            email=current_user.email,
            country="DE"
        )
        profile.stripe_account_id = account_data["account_id"]
        await db.commit()

    # Create onboarding link
    link_data = await StripeService.create_account_link(
        account_id=profile.stripe_account_id,
        refresh_url=onboarding_data.refresh_url,
        return_url=onboarding_data.return_url
    )

    return StripeConnectOnboardingResponse(
        account_id=profile.stripe_account_id,
        onboarding_url=link_data["url"],
        expires_at=link_data["expires_at"]
    )


@router.get("/connect/status", response_model=StripeAccountStatusResponse)
async def get_stripe_account_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Stripe Connect account status
    (Craftsmen only)
    """
    if current_user.role != UserRole.CRAFTSMAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only craftsmen can check Stripe status"
        )

    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman profile not found"
        )

    if not profile.stripe_account_id:
        return StripeAccountStatusResponse(
            account_id=None,
            onboarding_complete=False,
            charges_enabled=False,
            payouts_enabled=False,
            details_submitted=False
        )

    # Get account status from Stripe
    account_status = await StripeService.get_account_status(profile.stripe_account_id)

    # Update profile status
    onboarding_complete = (
        account_status["charges_enabled"] and
        account_status["payouts_enabled"] and
        account_status["details_submitted"]
    )

    if profile.stripe_onboarding_complete != onboarding_complete:
        profile.stripe_onboarding_complete = onboarding_complete
        await db.commit()

    return StripeAccountStatusResponse(
        account_id=account_status["account_id"],
        onboarding_complete=onboarding_complete,
        charges_enabled=account_status["charges_enabled"],
        payouts_enabled=account_status["payouts_enabled"],
        details_submitted=account_status["details_submitted"]
    )


@router.post("/intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create payment intent for a booking
    (Homeowners only)
    """
    if current_user.role != UserRole.HOMEOWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only homeowners can create payments"
        )

    # Get booking
    result = await db.execute(
        select(Booking).where(
            Booking.id == payment_data.booking_id,
            Booking.homeowner_id == current_user.id
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.status != BookingStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking must be accepted before payment"
        )

    # Check if payment already exists
    result = await db.execute(
        select(Payment).where(Payment.booking_id == booking.id)
    )
    existing_payment = result.scalar_one_or_none()

    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this booking"
        )

    # Get craftsman profile
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == booking.craftsman_id)
    )
    profile = result.scalar_one_or_none()

    if not profile or not profile.stripe_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Craftsman has not connected Stripe account"
        )

    # Calculate amounts
    amount = booking.estimated_cost or (booking.estimated_hours * booking.hourly_rate)
    platform_fee = amount * booking.platform_commission_rate
    craftsman_amount = amount - platform_fee

    # Create payment intent with Stripe
    payment_intent = await StripeService.create_payment_intent(
        amount=amount,
        currency="eur",
        connected_account_id=profile.stripe_account_id,
        application_fee=platform_fee,
        metadata={
            "booking_id": str(booking.id),
            "craftsman_id": str(booking.craftsman_id),
            "homeowner_id": str(booking.homeowner_id),
        }
    )

    # Create payment record
    payment = Payment(
        booking_id=booking.id,
        amount=amount,
        platform_fee=platform_fee,
        craftsman_payout=craftsman_amount,
        status=PaymentStatus.PENDING,
        stripe_payment_intent_id=payment_intent["id"],
    )
    db.add(payment)

    # Update booking status
    booking.status = BookingStatus.CONFIRMED
    await db.commit()
    await db.refresh(payment)

    return PaymentIntentResponse(
        payment_id=payment.id,
        client_secret=payment_intent["client_secret"],
        amount=amount,
        currency="eur",
        status=payment_intent["status"]
    )


@router.post("/confirm", response_model=PaymentResponse)
async def confirm_payment(
    confirm_data: PaymentConfirmRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm payment after successful charge"""
    # Find payment by intent ID
    result = await db.execute(
        select(Payment).where(
            Payment.stripe_payment_intent_id == confirm_data.payment_intent_id
        )
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Verify payment intent status with Stripe
    intent_status = await StripeService.confirm_payment_intent(
        confirm_data.payment_intent_id
    )

    if intent_status["status"] == "succeeded":
        payment.status = PaymentStatus.PAID
        payment.paid_at = datetime.utcnow()

        # Update booking status
        result = await db.execute(
            select(Booking).where(Booking.id == payment.booking_id)
        )
        booking = result.scalar_one_or_none()
        if booking:
            booking.status = BookingStatus.PAID

        await db.commit()
        await db.refresh(payment)

    return PaymentResponse.from_orm(payment)


@router.post("/payout", response_model=PayoutResponse)
async def process_payout(
    payout_data: PayoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process payout to craftsman after job completion
    (Craftsmen only)
    """
    if current_user.role != UserRole.CRAFTSMAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only craftsmen can request payouts"
        )

    # Get booking
    result = await db.execute(
        select(Booking).where(
            Booking.id == payout_data.booking_id,
            Booking.craftsman_id == current_user.id
        )
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking must be completed before payout"
        )

    # Get payment
    result = await db.execute(
        select(Payment).where(Payment.booking_id == booking.id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this booking"
        )

    if payment.status == PaymentStatus.TRANSFERRED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payout already processed"
        )

    if payment.status != PaymentStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment must be completed before payout"
        )

    # Get craftsman profile
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile or not profile.stripe_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe account not connected"
        )

    # Payout is automatic with Stripe Connect's transfer_data
    # Just update the status
    payment.status = PaymentStatus.TRANSFERRED
    payment.payout_at = datetime.utcnow()
    booking.status = BookingStatus.PAID

    await db.commit()
    await db.refresh(payment)

    return PayoutResponse(
        payout_id=payment.id,
        amount=payment.amount,
        craftsman_amount=payment.craftsman_payout,
        platform_fee=payment.platform_fee,
        status=payment.status.value,
        transfer_id=payment.stripe_transfer_id,
        estimated_arrival=None
    )


@router.get("/booking/{booking_id}", response_model=PaymentResponse)
async def get_booking_payment(
    booking_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment details for a booking"""
    # Get booking to verify access
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Verify user has access to this booking
    if booking.homeowner_id != current_user.id and booking.craftsman_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )

    # Get payment
    result = await db.execute(
        select(Payment).where(Payment.booking_id == booking_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return PaymentResponse.from_orm(payment)


@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payment history for current user"""
    if current_user.role == UserRole.HOMEOWNER:
        # Get payments for bookings where user is homeowner
        result = await db.execute(
            select(Payment)
            .join(Booking, Payment.booking_id == Booking.id)
            .where(Booking.homeowner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    elif current_user.role == UserRole.CRAFTSMAN:
        # Get payments for bookings where user is craftsman
        result = await db.execute(
            select(Payment)
            .join(Booking, Payment.booking_id == Booking.id)
            .where(Booking.craftsman_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )

    payments = result.scalars().all()
    return [PaymentResponse.from_orm(payment) for payment in payments]
