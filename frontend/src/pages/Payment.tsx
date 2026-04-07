import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { LoadingPage } from '@/components/common';
import { PaymentForm } from '@/components/payment/PaymentForm';
import type { Booking } from '@/types';

// Initialize Stripe
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');

export function Payment() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadBookingAndPayment();
    }
  }, [id]);

  const loadBookingAndPayment = async () => {
    setIsLoading(true);
    try {
      // Load booking details
      const bookingData = await api.getBooking(parseInt(id!));

      // Check if booking is in a payable state
      if (bookingData.status !== 'confirmed') {
        toast.error('This booking is not ready for payment');
        navigate(`/bookings/${id}`);
        return;
      }

      // Check if already paid
      if (bookingData.payment_status === 'completed') {
        toast.info('This booking has already been paid');
        navigate(`/bookings/${id}`);
        return;
      }

      setBooking(bookingData);

      // Create payment intent
      const { client_secret } = await api.createPaymentIntent(parseInt(id!));
      setClientSecret(client_secret);
    } catch (error: any) {
      console.error('Failed to load payment:', error);
      toast.error(error.response?.data?.detail || 'Failed to load payment');
      navigate('/bookings');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !booking || !clientSecret) {
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
        <h1 className="text-3xl font-bold mb-2">Complete Payment</h1>
        <p className="text-gray-600">
          Secure payment for booking #{booking.id}
        </p>
      </div>

      {/* Payment Form with Stripe Elements */}
      <Elements
        stripe={stripePromise}
        options={{
          clientSecret,
          appearance: {
            theme: 'stripe',
            variables: {
              colorPrimary: '#2563eb',
              colorBackground: '#ffffff',
              colorText: '#1f2937',
              colorDanger: '#ef4444',
              fontFamily: 'system-ui, sans-serif',
              borderRadius: '0.5rem',
            },
          },
        }}
      >
        <PaymentForm booking={booking} clientSecret={clientSecret} />
      </Elements>
    </div>
  );
}
