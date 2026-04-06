import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class BookingStatus(str, enum.Enum):
    """Booking lifecycle statuses"""
    PENDING = "pending"  # Created by homeowner, waiting for craftsman response
    ACCEPTED = "accepted"  # Craftsman accepted the booking
    REJECTED = "rejected"  # Craftsman rejected the booking
    CONFIRMED = "confirmed"  # Booking confirmed with date/time
    IN_PROGRESS = "in_progress"  # Work has started
    COMPLETED = "completed"  # Work finished, pending payment
    PAID = "paid"  # Payment completed
    CANCELLED = "cancelled"  # Cancelled by either party
    DISPUTED = "disputed"  # Dispute raised


class Booking(Base):
    """Booking/appointment between homeowner and craftsman"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    # Participants
    homeowner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    craftsman_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Job details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    trade_type = Column(String(50), nullable=False)

    # Location
    service_address = Column(String(512), nullable=False)
    postal_code = Column(String(10), nullable=False)
    city = Column(String(100), nullable=False)

    # Scheduling
    requested_date = Column(DateTime, nullable=True)  # Preferred date by homeowner
    scheduled_date = Column(DateTime, nullable=True)  # Confirmed date
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)

    # Pricing
    hourly_rate = Column(Float, nullable=False)  # Locked rate at booking time
    estimated_cost = Column(Float, nullable=True)
    final_cost = Column(Float, nullable=True)
    platform_commission_rate = Column(Float, default=0.12)  # 12% commission

    # Status and tracking
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    cancellation_reason = Column(Text, nullable=True)
    craftsman_notes = Column(Text, nullable=True)  # Private notes for craftsman
    homeowner_notes = Column(Text, nullable=True)  # Private notes for homeowner

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    homeowner = relationship("User", foreign_keys=[homeowner_id], back_populates="bookings_as_homeowner")
    craftsman = relationship("User", foreign_keys=[craftsman_id], back_populates="bookings_as_craftsman")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    review = relationship("Review", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    messages = relationship("MessageThread", back_populates="booking", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Booking #{self.id} - {self.status.value}>"

    @property
    def platform_commission(self):
        """Calculate platform commission amount"""
        if self.final_cost:
            return self.final_cost * self.platform_commission_rate
        return 0.0

    @property
    def craftsman_payout(self):
        """Calculate amount to pay craftsman after commission"""
        if self.final_cost:
            return self.final_cost - self.platform_commission
        return 0.0
