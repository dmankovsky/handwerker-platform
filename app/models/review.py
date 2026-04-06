from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Review(Base):
    """Reviews and ratings for craftsmen"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    # Participants
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Homeowner
    craftsman_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Rating (1-5 stars)
    rating = Column(Float, nullable=False)  # 1.0 to 5.0

    # Detailed ratings (optional)
    quality_rating = Column(Float, nullable=True)  # Quality of work
    communication_rating = Column(Float, nullable=True)  # Communication
    punctuality_rating = Column(Float, nullable=True)  # Timeliness
    value_rating = Column(Float, nullable=True)  # Value for money

    # Review text
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=False)

    # Response from craftsman
    response = Column(Text, nullable=True)
    response_date = Column(DateTime, nullable=True)

    # Moderation
    is_verified = Column(Boolean, default=True)  # Verified booking completion
    is_flagged = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="review")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    craftsman = relationship("User", foreign_keys=[craftsman_id], back_populates="reviews_received")

    def __repr__(self):
        return f"<Review #{self.id} - {self.rating}⭐>"

    @property
    def overall_rating(self):
        """Calculate overall rating from detailed ratings"""
        ratings = [
            self.quality_rating,
            self.communication_rating,
            self.punctuality_rating,
            self.value_rating
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return self.rating
