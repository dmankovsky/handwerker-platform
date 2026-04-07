import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { Button, Input } from '@/components/common';
import { validationRules } from '@/utils/validation';
import type { Booking } from '@/types';

interface CreateBookingFormData {
  craftsman_id: number;
  job_title: string;
  job_description: string;
  service_address: string;
  requested_date: string;
  estimated_hours?: number;
}

export function CreateBooking() {
  const navigate = useNavigate();
  const location = useLocation();
  const craftsmanId = location.state?.craftsmanId;
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateBookingFormData>({
    defaultValues: {
      craftsman_id: craftsmanId,
    },
  });

  const onSubmit = async (data: CreateBookingFormData) => {
    setIsLoading(true);
    try {
      const booking = await api.createBooking(data);
      toast.success('Booking request sent successfully!');
      navigate(`/bookings/${booking.id}`);
    } catch (error: any) {
      console.error('Create booking error:', error);
      const message = error.response?.data?.detail || 'Failed to create booking';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h1 className="text-3xl font-bold mb-2">Create Booking Request</h1>
        <p className="text-gray-600 mb-8">
          Fill out the details below to request a booking with a craftsman
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Input
            label="Craftsman ID"
            type="number"
            error={errors.craftsman_id?.message}
            helperText="Enter the craftsman ID you want to book"
            {...register('craftsman_id', {
              required: 'Craftsman ID is required',
              valueAsNumber: true,
            })}
          />

          <Input
            label="Job Title"
            type="text"
            placeholder="e.g., Fix leaking kitchen faucet"
            error={errors.job_title?.message}
            {...register('job_title', validationRules.minLength('Job title', 5))}
          />

          <div>
            <label htmlFor="job_description" className="block text-sm font-medium text-gray-700 mb-2">
              Job Description
            </label>
            <textarea
              id="job_description"
              rows={4}
              className={`input ${errors.job_description ? 'border-red-500' : ''}`}
              placeholder="Describe the work you need done in detail..."
              {...register('job_description', validationRules.minLength('Job description', 20))}
            />
            {errors.job_description && (
              <p className="text-red-500 text-sm mt-1">{errors.job_description.message}</p>
            )}
          </div>

          <Input
            label="Service Address"
            type="text"
            placeholder="Full address where work will be performed"
            error={errors.service_address?.message}
            {...register('service_address', validationRules.minLength('Service address', 10))}
          />

          <Input
            label="Requested Date"
            type="date"
            error={errors.requested_date?.message}
            helperText="Preferred date for the work to be done"
            {...register('requested_date', {
              required: 'Requested date is required',
            })}
          />

          <Input
            label="Estimated Hours (Optional)"
            type="number"
            min="0.5"
            step="0.5"
            placeholder="e.g., 2.5"
            error={errors.estimated_hours?.message}
            helperText="Your estimate of how long the job will take"
            {...register('estimated_hours', {
              valueAsNumber: true,
            })}
          />

          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">What happens next?</h3>
            <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
              <li>The craftsman will review your booking request</li>
              <li>They may accept or reject the request</li>
              <li>If accepted, you'll need to confirm and pay to secure the booking</li>
              <li>You'll receive email notifications about status changes</li>
            </ul>
          </div>

          <div className="flex gap-3">
            <Button type="submit" isLoading={isLoading} fullWidth>
              Send Booking Request
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate(-1)}
              fullWidth
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
