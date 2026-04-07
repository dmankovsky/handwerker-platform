import { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { api } from '@/services/api';
import { LoadingPage } from '@/components/common';
import type { Booking } from '@/types';

export function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const bookingId = searchParams.get('booking_id');

  useEffect(() => {
    if (bookingId) {
      loadBooking();
    } else {
      navigate('/bookings');
    }
  }, [bookingId]);

  const loadBooking = async () => {
    try {
      const data = await api.getBooking(parseInt(bookingId!));
      setBooking(data);
    } catch (error) {
      console.error('Failed to load booking:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingPage />;
  }

  if (!booking) {
    return (
      <div className="max-w-2xl mx-auto text-center py-16">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Booking Not Found</h1>
        <Link to="/bookings" className="text-primary-600 hover:underline">
          Go to Bookings
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center py-12">
        {/* Success Icon */}
        <div className="mb-6 flex justify-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
            <svg
              className="w-12 h-12 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>

        {/* Success Message */}
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
        <p className="text-lg text-gray-600 mb-8">
          Your payment has been processed successfully
        </p>

        {/* Payment Details */}
        <div className="card text-left mb-8">
          <h2 className="text-xl font-bold mb-4">Payment Details</h2>

          <div className="space-y-3">
            <div className="flex justify-between py-2 border-b border-gray-200">
              <span className="text-gray-600">Booking ID:</span>
              <span className="font-medium">#{booking.id}</span>
            </div>

            <div className="flex justify-between py-2 border-b border-gray-200">
              <span className="text-gray-600">Service:</span>
              <span className="font-medium">{booking.job_title}</span>
            </div>

            <div className="flex justify-between py-2 border-b border-gray-200">
              <span className="text-gray-600">Craftsman:</span>
              <span className="font-medium">{booking.craftsman.full_name}</span>
            </div>

            <div className="flex justify-between py-2 border-b border-gray-200">
              <span className="text-gray-600">Payment Status:</span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Paid
              </span>
            </div>

            <div className="flex justify-between py-2 pt-4">
              <span className="text-lg font-semibold text-gray-900">Amount Paid:</span>
              <span className="text-2xl font-bold text-green-600">
                €{booking.final_cost || booking.estimated_cost}
              </span>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="card bg-blue-50 border border-blue-200 text-left mb-8">
          <h3 className="font-semibold text-blue-900 mb-3">What happens next?</h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Payment is held in escrow until work is completed</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>The craftsman will be notified and can start work</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>You'll receive email updates about your booking status</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>After completion, you can leave a review</span>
            </li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center">
          <Link
            to={`/bookings/${booking.id}`}
            className="btn-primary px-6 py-3"
          >
            View Booking Details
          </Link>
          <Link
            to="/bookings"
            className="btn-secondary px-6 py-3"
          >
            Go to My Bookings
          </Link>
        </div>

        {/* Receipt Note */}
        <p className="text-sm text-gray-500 mt-8">
          A payment receipt has been sent to your email address
        </p>
      </div>
    </div>
  );
}
