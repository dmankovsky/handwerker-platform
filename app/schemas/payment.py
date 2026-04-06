from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.payment import PaymentStatus


class StripeConnectOnboardingRequest(BaseModel):
    """Request to start Stripe Connect onboarding"""
    refresh_url: str = Field(..., description="URL to return to if onboarding fails")
    return_url: str = Field(..., description="URL to return to after onboarding completes")


class StripeConnectOnboardingResponse(BaseModel):
    """Response with Stripe Connect onboarding URL"""
    account_id: str
    onboarding_url: str
    expires_at: int


class StripeAccountStatusResponse(BaseModel):
    """Stripe account status"""
    account_id: Optional[str]
    onboarding_complete: bool
    charges_enabled: bool
    payouts_enabled: bool
    details_submitted: bool


class PaymentIntentRequest(BaseModel):
    """Request to create payment intent for booking"""
    booking_id: int
    save_payment_method: bool = False


class PaymentIntentResponse(BaseModel):
    """Payment intent response"""
    payment_id: int
    client_secret: str
    amount: float
    currency: str = "eur"
    status: str


class PaymentConfirmRequest(BaseModel):
    """Confirm payment for booking"""
    payment_intent_id: str


class PayoutRequest(BaseModel):
    """Request payout for completed booking"""
    booking_id: int


class PayoutResponse(BaseModel):
    """Payout response"""
    payout_id: int
    amount: float
    craftsman_amount: float
    platform_fee: float
    status: str
    transfer_id: Optional[str]
    estimated_arrival: Optional[datetime]


class PaymentResponse(BaseModel):
    """Payment response"""
    id: int
    booking_id: int
    amount: float
    platform_fee: float
    craftsman_payout: float
    status: PaymentStatus
    stripe_payment_intent_id: Optional[str]
    stripe_transfer_id: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]
    payout_at: Optional[datetime]

    class Config:
        from_attributes = True
