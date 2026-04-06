from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.craftsman import TradeType


class TradeCreate(BaseModel):
    """Schema for creating a trade"""
    trade_type: TradeType
    is_primary: bool = False


class TradeResponse(BaseModel):
    """Schema for trade response"""
    id: int
    trade_type: TradeType
    is_primary: bool

    class Config:
        from_attributes = True


class ServiceAreaCreate(BaseModel):
    """Schema for creating a service area"""
    postal_code: str = Field(..., max_length=10)
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=100)


class ServiceAreaResponse(BaseModel):
    """Schema for service area response"""
    id: int
    postal_code: str
    city: str
    state: Optional[str]

    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    """Schema for creating a portfolio item"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    image_url: str = Field(..., max_length=512)
    trade_type: Optional[TradeType] = None


class PortfolioResponse(BaseModel):
    """Schema for portfolio response"""
    id: int
    title: str
    description: Optional[str]
    image_url: str
    trade_type: Optional[TradeType]
    created_at: datetime

    class Config:
        from_attributes = True


class CraftsmanProfileCreate(BaseModel):
    """Schema for creating a craftsman profile"""
    company_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    hourly_rate: float = Field(..., gt=0, le=500)
    years_experience: Optional[int] = Field(None, ge=0, le=80)
    max_radius_km: int = Field(50, ge=1, le=200)

    # Verification
    handwerkskammer_number: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=100)

    # Initial trades
    trades: List[TradeCreate] = []

    # Initial service areas
    service_areas: List[ServiceAreaCreate] = []


class CraftsmanProfileUpdate(BaseModel):
    """Schema for updating craftsman profile"""
    company_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, gt=0, le=500)
    years_experience: Optional[int] = Field(None, ge=0, le=80)
    max_radius_km: Optional[int] = Field(None, ge=1, le=200)
    accepts_bookings: Optional[bool] = None

    handwerkskammer_number: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=100)


class CraftsmanProfileResponse(BaseModel):
    """Schema for craftsman profile response"""
    id: int
    user_id: int
    company_name: Optional[str]
    bio: Optional[str]
    hourly_rate: float
    years_experience: Optional[int]
    is_verified: bool
    stripe_onboarding_complete: bool
    total_jobs: int
    average_rating: float
    total_reviews: int
    accepts_bookings: bool
    max_radius_km: int
    created_at: datetime
    updated_at: datetime

    # Nested data
    trades: List[TradeResponse] = []
    service_areas: List[ServiceAreaResponse] = []
    portfolio: List[PortfolioResponse] = []

    class Config:
        from_attributes = True


class CraftsmanSearchFilters(BaseModel):
    """Schema for craftsman search filters"""
    trade_type: Optional[TradeType] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    max_hourly_rate: Optional[float] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    radius_km: int = Field(50, ge=1, le=200)
    is_verified: Optional[bool] = None
    accepts_bookings: bool = True
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
