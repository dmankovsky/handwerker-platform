import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment lifecycle statuses"""
    PENDING = "pending"  # Payment intent created
    AUTHORIZED = "authorized"  # Payment authorized (hold)
    PAID = "paid"  # Payment captured
    RELEASED = "released"  # Payment released to craftsman
    REFUNDED = "refunded"  # Payment refunded to homeowner
    FAILED = "failed"  # Payment failed
    DISPUTED = "disputed"  # Payment disputed


class Payment(Base):
    """Payment transactions for bookings"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)

    # Amounts (in EUR)
    amount = Column(Float, nullable=False)  # Total amount
    platform_fee = Column(Float, nullable=False)  # Platform commission
    craftsman_amount = Column(Float, nullable=False)  # Amount to craftsman

    # Stripe references
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_charge_id = Column(String(255), nullable=True)
    stripe_transfer_id = Column(String(255), nullable=True)  # Transfer to craftsman
    stripe_refund_id = Column(String(255), nullable=True)

    # Payment details
    payment_method = Column(String(50), default="card")  # card, sepa, etc.
    currency = Column(String(3), default="EUR")

    # Status and tracking
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    failure_reason = Column(String(512), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    authorized_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    released_at = Column(DateTime, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # Relationships
    booking = relationship("Booking", back_populates="payment")

    def __repr__(self):
        return f"<Payment #{self.id} - {self.status.value} - €{self.amount}>"
