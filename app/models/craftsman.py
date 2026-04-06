import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class TradeType(str, enum.Enum):
    """Types of trades/crafts"""
    ELECTRICIAN = "electrician"
    PLUMBER = "plumber"
    CARPENTER = "carpenter"
    PAINTER = "painter"
    ROOFER = "roofer"
    MASON = "mason"
    TILER = "tiler"
    FLOORING = "flooring"
    HVAC = "hvac"
    LOCKSMITH = "locksmith"
    GLAZIER = "glazier"
    LANDSCAPER = "landscaper"
    RENOVATION = "renovation"
    OTHER = "other"


class CraftsmanProfile(Base):
    """Craftsman profile with business information"""
    __tablename__ = "craftsman_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Business information
    company_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    hourly_rate = Column(Float, nullable=False)  # in EUR
    years_experience = Column(Integer, nullable=True)

    # Verification
    is_verified = Column(Boolean, default=False)
    handwerkskammer_number = Column(String(100), nullable=True)  # Chamber of crafts registration
    tax_id = Column(String(100), nullable=True)

    # Stripe Connect
    stripe_account_id = Column(String(255), nullable=True)
    stripe_onboarding_complete = Column(Boolean, default=False)

    # Statistics
    total_jobs = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

    # Availability
    accepts_bookings = Column(Boolean, default=True)
    max_radius_km = Column(Integer, default=50)  # Maximum travel distance

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="craftsman_profile")
    trades = relationship("Trade", back_populates="craftsman", cascade="all, delete-orphan")
    service_areas = relationship("ServiceArea", back_populates="craftsman", cascade="all, delete-orphan")
    portfolio = relationship("Portfolio", back_populates="craftsman", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CraftsmanProfile {self.company_name or self.user.full_name}>"


class Trade(Base):
    """Trades offered by a craftsman"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    craftsman_id = Column(Integer, ForeignKey("craftsman_profiles.id"), nullable=False)
    trade_type = Column(Enum(TradeType), nullable=False)
    is_primary = Column(Boolean, default=False)

    # Relationships
    craftsman = relationship("CraftsmanProfile", back_populates="trades")

    def __repr__(self):
        return f"<Trade {self.trade_type.value}>"


class ServiceArea(Base):
    """Geographic areas where craftsman provides services"""
    __tablename__ = "service_areas"

    id = Column(Integer, primary_key=True, index=True)
    craftsman_id = Column(Integer, ForeignKey("craftsman_profiles.id"), nullable=False)

    postal_code = Column(String(10), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)

    # Relationships
    craftsman = relationship("CraftsmanProfile", back_populates="service_areas")

    def __repr__(self):
        return f"<ServiceArea {self.postal_code} {self.city}>"


class Portfolio(Base):
    """Portfolio items (photos of completed work)"""
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    craftsman_id = Column(Integer, ForeignKey("craftsman_profiles.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=False)
    trade_type = Column(Enum(TradeType), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    craftsman = relationship("CraftsmanProfile", back_populates="portfolio")

    def __repr__(self):
        return f"<Portfolio {self.title}>"
