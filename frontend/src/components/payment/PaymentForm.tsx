import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { toast } from 'react-toastify';
import { Button } from '@/components/common';
import { api } from '@/services/api';
import type { Booking } from '@/types';

interface PaymentFormProps {
  booking: Booking;
  clientSecret: string;
}

export function PaymentForm({ booking, clientSecret }: PaymentFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const amount = booking.final_cost || booking.estimated_cost;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      // Confirm the payment
      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/payment/success?booking_id=${booking.id}`,
        },
        redirect: 'if_required',
      });

      if (error) {
        setErrorMessage(error.message || 'Payment failed');
        toast.error(error.message || 'Payment failed');
      } else if (paymentIntent && paymentIntent.status === 'succeeded') {
        // Confirm payment on backend
        await api.confirmPayment(booking.id, paymentIntent.id);

        toast.success('Payment successful!');
        navigate(`/payment/success?booking_id=${booking.id}`);
      }
    } catch (error: any) {
      console.error('Payment error:', error);
      setErrorMessage(error.message || 'An unexpected error occurred');
      toast.error('Payment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Payment Summary */}
      <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-3">Payment Summary</h3>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Booking:</span>
            <span className="font-medium">{booking.job_title}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Craftsman:</span>
            <span className="font-medium">{booking.craftsman.full_name}</span>
          </div>
          {booking.estimated_hours && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Estimated Hours:</span>
              <span className="font-medium">{booking.estimated_hours}h</span>
            </div>
          )}
          <div className="border-t border-gray-300 pt-2 mt-2">
            <div className="flex justify-between">
              <span className="font-semibold text-gray-900">Total Amount:</span>
              <span className="text-xl font-bold text-primary-600">€{amount}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stripe Payment Element */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4">Payment Details</h3>
        <PaymentElement />
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">{errorMessage}</p>
        </div>
      )}

      {/* Security Notice */}
      <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <svg
          className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
            clipRule="evenodd"
          />
        </svg>
        <div className="text-sm text-blue-900">
          <p className="font-medium">Secure Payment</p>
          <p className="text-blue-700">
            Your payment is processed securely by Stripe. We never store your card details.
          </p>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={() => navigate(`/bookings/${booking.id}`)}
          disabled={isProcessing}
          fullWidth
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={!stripe || isProcessing}
          isLoading={isProcessing}
          fullWidth
        >
          {isProcessing ? 'Processing...' : `Pay €${amount}`}
        </Button>
      </div>

      {/* Payment Info */}
      <p className="text-xs text-center text-gray-500">
        By completing this payment, you agree to our Terms of Service and acknowledge that
        payment will be held in escrow until the work is completed.
      </p>
    </form>
  );
}
