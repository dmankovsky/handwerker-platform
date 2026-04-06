from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    """Schema for creating a review"""
    booking_id: int
    rating: float = Field(..., ge=1.0, le=5.0)

    # Detailed ratings (optional)
    quality_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    communication_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    punctuality_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    value_rating: Optional[float] = Field(None, ge=1.0, le=5.0)

    title: Optional[str] = Field(None, max_length=255)
    comment: str = Field(..., min_length=10)


class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    quality_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    communication_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    punctuality_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    value_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = Field(None, min_length=10)


class ReviewResponse(BaseModel):
    """Schema for review response"""
    id: int
    booking_id: int
    reviewer_id: int
    craftsman_id: int

    rating: float
    quality_rating: Optional[float]
    communication_rating: Optional[float]
    punctuality_rating: Optional[float]
    value_rating: Optional[float]

    title: Optional[str]
    comment: str

    response: Optional[str]
    response_date: Optional[datetime]

    is_verified: bool
    is_visible: bool

    created_at: datetime
    updated_at: datetime

    # Reviewer info (for public display)
    reviewer_name: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewResponseCreate(BaseModel):
    """Schema for craftsman response to review"""
    response: str = Field(..., min_length=10, max_length=1000)
