from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    """Schema for creating a booking"""
    craftsman_id: int
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    trade_type: str = Field(..., max_length=50)

    # Location
    service_address: str = Field(..., max_length=512)
    postal_code: str = Field(..., max_length=10)
    city: str = Field(..., max_length=100)

    # Scheduling
    requested_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, gt=0, le=100)


class BookingUpdate(BaseModel):
    """Schema for updating a booking"""
    status: Optional[BookingStatus] = None
    scheduled_date: Optional[datetime] = None
    actual_hours: Optional[float] = Field(None, gt=0, le=100)
    final_cost: Optional[float] = Field(None, gt=0)
    craftsman_notes: Optional[str] = None
    homeowner_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None


class BookingResponse(BaseModel):
    """Schema for booking response"""
    id: int
    homeowner_id: int
    craftsman_id: int

    title: str
    description: str
    trade_type: str

    service_address: str
    postal_code: str
    city: str

    requested_date: Optional[datetime]
    scheduled_date: Optional[datetime]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]

    hourly_rate: float
    estimated_cost: Optional[float]
    final_cost: Optional[float]
    platform_commission_rate: float

    status: BookingStatus
    cancellation_reason: Optional[str]

    created_at: datetime
    updated_at: datetime
    accepted_at: Optional[datetime]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema for booking list response with additional info"""
    id: int
    title: str
    trade_type: str
    status: BookingStatus
    requested_date: Optional[datetime]
    scheduled_date: Optional[datetime]
    created_at: datetime

    # Simplified related data
    homeowner_name: str
    craftsman_name: str
    craftsman_company: Optional[str]

    class Config:
        from_attributes = True
