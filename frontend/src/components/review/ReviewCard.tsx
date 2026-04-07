import { useState } from 'react';
import { format } from 'date-fns';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/services/api';
import { toast } from 'react-toastify';
import { Button } from '@/components/common';
import type { Review } from '@/types';

interface ReviewCardProps {
  review: Review;
  onResponseAdded?: (review: Review) => void;
}

export function ReviewCard({ review, onResponseAdded }: ReviewCardProps) {
  const { user } = useAuth();
  const [showResponseForm, setShowResponseForm] = useState(false);
  const [response, setResponse] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const averageRating =
    (review.quality_rating +
      review.communication_rating +
      review.punctuality_rating +
      review.value_rating) /
    4;

  const canRespond =
    user?.role === 'craftsman' && !review.craftsman_response && onResponseAdded;

  const handleSubmitResponse = async () => {
    if (!response.trim()) {
      toast.error('Please enter a response');
      return;
    }

    setIsSubmitting(true);
    try {
      const updated = await api.respondToReview(review.id, response);
      toast.success('Response submitted successfully!');
      setShowResponseForm(false);
      setResponse('');
      if (onResponseAdded) {
        onResponseAdded(updated);
      }
    } catch (error: any) {
      console.error('Failed to submit response:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit response');
    } finally {
      setIsSubmitting(false);
    }
  };

  const StarRating = ({ rating, label }: { rating: number; label: string }) => (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600 w-32">{label}</span>
      <div className="flex items-center gap-1">
        {[...Array(5)].map((_, i) => (
          <svg
            key={i}
            className={`w-4 h-4 ${
              i < rating ? 'text-yellow-400' : 'text-gray-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
        <span className="ml-1 text-sm font-semibold text-gray-700">{rating}</span>
      </div>
    </div>
  );

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-lg font-bold text-primary-600">
              {review.homeowner.full_name.charAt(0)}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              {review.homeowner.full_name}
            </h3>
            <p className="text-sm text-gray-500">
              {format(new Date(review.created_at), 'MMMM d, yyyy')}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex">
            {[...Array(5)].map((_, i) => (
              <svg
                key={i}
                className={`w-5 h-5 ${
                  i < Math.round(averageRating) ? 'text-yellow-400' : 'text-gray-300'
                }`}
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            ))}
          </div>
          <span className="text-lg font-bold text-gray-900">
            {averageRating.toFixed(1)}
          </span>
        </div>
      </div>

      {/* Detailed Ratings */}
      <div className="space-y-2 mb-4 p-4 bg-gray-50 rounded-lg">
        <StarRating rating={review.quality_rating} label="Quality of Work" />
        <StarRating rating={review.communication_rating} label="Communication" />
        <StarRating rating={review.punctuality_rating} label="Punctuality" />
        <StarRating rating={review.value_rating} label="Value for Money" />
      </div>

      {/* Review Comment */}
      <div className="mb-4">
        <p className="text-gray-700 whitespace-pre-wrap">{review.comment}</p>
      </div>

      {/* Craftsman Response */}
      {review.craftsman_response && (
        <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
          <div className="flex items-center gap-2 mb-2">
            <svg
              className="w-5 h-5 text-blue-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z"
                clipRule="evenodd"
              />
            </svg>
            <span className="font-semibold text-blue-900">Response from Craftsman</span>
          </div>
          <p className="text-gray-700 whitespace-pre-wrap">
            {review.craftsman_response}
          </p>
          {review.response_date && (
            <p className="text-sm text-blue-600 mt-2">
              {format(new Date(review.response_date), 'MMMM d, yyyy')}
            </p>
          )}
        </div>
      )}

      {/* Response Form */}
      {canRespond && !showResponseForm && (
        <div className="mt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowResponseForm(true)}
          >
            Respond to Review
          </Button>
        </div>
      )}

      {showResponseForm && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Response
          </label>
          <textarea
            rows={4}
            className="input mb-3"
            placeholder="Thank the customer or address their feedback..."
            value={response}
            onChange={(e) => setResponse(e.target.value)}
          />
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={handleSubmitResponse}
              isLoading={isSubmitting}
            >
              Submit Response
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setShowResponseForm(false);
                setResponse('');
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
