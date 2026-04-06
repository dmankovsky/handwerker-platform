import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles in the platform"""
    HOMEOWNER = "homeowner"
    CRAFTSMAN = "craftsman"
    ADMIN = "admin"


class User(Base):
    """User model for both homeowners and craftsmen"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.HOMEOWNER)

    # Address information
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(10), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="Germany")

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)

    # Stripe
    stripe_customer_id = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    craftsman_profile = relationship("CraftsmanProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    bookings_as_homeowner = relationship("Booking", foreign_keys="Booking.homeowner_id", back_populates="homeowner", cascade="all, delete-orphan")
    bookings_as_craftsman = relationship("Booking", foreign_keys="Booking.craftsman_id", back_populates="craftsman", cascade="all, delete-orphan")
    reviews_given = relationship("Review", foreign_keys="Review.reviewer_id", back_populates="reviewer", cascade="all, delete-orphan")
    reviews_received = relationship("Review", foreign_keys="Review.craftsman_id", back_populates="craftsman", cascade="all, delete-orphan")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", cascade="all, delete-orphan")
    messages_received = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
