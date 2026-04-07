import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { LoadingPage } from '@/components/common';
import { ReviewForm } from '@/components/review';
import type { Booking, Review } from '@/types';

export function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadBooking();
    }
  }, [id]);

  const loadBooking = async () => {
    setIsLoading(true);
    try {
      const data = await api.getBooking(parseInt(id!));

      // Check if booking is completed
      if (data.status !== 'completed') {
        toast.error('You can only review completed bookings');
        navigate(`/bookings/${id}`);
        return;
      }

      // Check if already reviewed
      const reviews = await api.getCraftsmanReviews(data.craftsman.id);
      const existingReview = reviews.find((r: Review) => r.booking_id === data.id);

      if (existingReview) {
        toast.info('You have already reviewed this booking');
        navigate(`/bookings/${id}`);
        return;
      }

      setBooking(data);
    } catch (error) {
      console.error('Failed to load booking:', error);
      toast.error('Failed to load booking');
      navigate('/bookings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReviewSubmitted = (review: Review) => {
    toast.success('Thank you for your review!');
    navigate(`/bookings/${id}`);
  };

  if (isLoading || !booking) {
    return <LoadingPage />;
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Back Button */}
      <Link
        to={`/bookings/${id}`}
        className="text-primary-600 hover:text-primary-700 mb-4 inline-block"
      >
        ← Back to booking
      </Link>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Leave a Review</h1>
        <p className="text-gray-600">
          Share your experience working with {booking.craftsman.full_name}
        </p>
      </div>

      {/* Booking Summary */}
      <div className="card mb-6">
        <h2 className="text-xl font-bold mb-4">{booking.job_title}</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Craftsman:</span>
            <p className="font-medium">{booking.craftsman.full_name}</p>
          </div>
          <div>
            <span className="text-gray-600">Total Cost:</span>
            <p className="font-medium">€{booking.final_cost || booking.estimated_cost}</p>
          </div>
        </div>
      </div>

      {/* Review Form */}
      <div className="card">
        <ReviewForm bookingId={booking.id} onReviewSubmitted={handleReviewSubmitted} />
      </div>
    </div>
  );
}
