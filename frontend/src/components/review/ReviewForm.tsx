import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { Button } from '@/components/common';
import type { Review } from '@/types';

interface ReviewFormProps {
  bookingId: number;
  onReviewSubmitted: (review: Review) => void;
}

interface ReviewFormData {
  comment: string;
}

export function ReviewForm({ bookingId, onReviewSubmitted }: ReviewFormProps) {
  const [qualityRating, setQualityRating] = useState(5);
  const [communicationRating, setCommunicationRating] = useState(5);
  const [punctualityRating, setPunctualityRating] = useState(5);
  const [valueRating, setValueRating] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ReviewFormData>();

  const onSubmit = async (data: ReviewFormData) => {
    setIsSubmitting(true);
    try {
      const review = await api.createReview(bookingId, {
        quality_rating: qualityRating,
        communication_rating: communicationRating,
        punctuality_rating: punctualityRating,
        value_rating: valueRating,
        comment: data.comment,
      });

      toast.success('Review submitted successfully!');
      reset();
      onReviewSubmitted(review);
    } catch (error: any) {
      console.error('Failed to submit review:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit review');
    } finally {
      setIsSubmitting(false);
    }
  };

  const RatingSlider = ({
    label,
    value,
    onChange,
  }: {
    label: string;
    value: number;
    onChange: (value: number) => void;
  }) => (
    <div>
      <div className="flex justify-between items-center mb-2">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <div className="flex items-center gap-1">
          {[...Array(5)].map((_, i) => (
            <svg
              key={i}
              className={`w-5 h-5 ${
                i < value ? 'text-yellow-400' : 'text-gray-300'
              }`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          ))}
          <span className="ml-2 text-sm font-semibold text-gray-900">{value}</span>
        </div>
      </div>
      <input
        type="range"
        min="1"
        max="5"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
      />
    </div>
  );

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-4">Rate Your Experience</h3>
        <div className="space-y-4">
          <RatingSlider
            label="Quality of Work"
            value={qualityRating}
            onChange={setQualityRating}
          />
          <RatingSlider
            label="Communication"
            value={communicationRating}
            onChange={setCommunicationRating}
          />
          <RatingSlider
            label="Punctuality"
            value={punctualityRating}
            onChange={setPunctualityRating}
          />
          <RatingSlider
            label="Value for Money"
            value={valueRating}
            onChange={setValueRating}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Review
        </label>
        <textarea
          rows={5}
          className={`input ${errors.comment ? 'border-red-500' : ''}`}
          placeholder="Share your experience working with this craftsman..."
          {...register('comment', {
            required: 'Please write a review',
            minLength: {
              value: 10,
              message: 'Review must be at least 10 characters',
            },
            maxLength: {
              value: 1000,
              message: 'Review cannot exceed 1000 characters',
            },
          })}
        />
        {errors.comment && (
          <p className="text-red-500 text-sm mt-1">{errors.comment.message}</p>
        )}
      </div>

      <div className="flex gap-3">
        <Button type="submit" isLoading={isSubmitting} fullWidth>
          Submit Review
        </Button>
      </div>
    </form>
  );
}
