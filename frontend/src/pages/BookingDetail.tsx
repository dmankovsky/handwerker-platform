import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import { format } from 'date-fns';
import { api } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingPage, Button } from '@/components/common';
import { BookingStatusBadge } from '@/components/booking/BookingStatusBadge';
import type { Booking } from '@/types';

export function BookingDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);

  const {
    register: registerAccept,
    handleSubmit: handleSubmitAccept,
    formState: { errors: acceptErrors },
  } = useForm<{ scheduled_date: string; estimated_hours?: number }>();

  const {
    register: registerComplete,
    handleSubmit: handleSubmitComplete,
    formState: { errors: completeErrors },
  } = useForm<{ actual_hours?: number; notes?: string }>();

  useEffect(() => {
    if (id) {
      loadBooking();
    }
  }, [id]);

  const loadBooking = async () => {
    setIsLoading(true);
    try {
      const data = await api.getBooking(parseInt(id!));
      setBooking(data);
    } catch (error) {
      console.error('Failed to load booking:', error);
      toast.error('Failed to load booking');
      navigate('/bookings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccept = async (data: { scheduled_date: string; estimated_hours?: number }) => {
    setIsActionLoading(true);
    try {
      const updated = await api.acceptBooking(
        parseInt(id!),
        data.scheduled_date,
        data.estimated_hours
      );
      setBooking(updated);
      toast.success('Booking accepted successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to accept booking');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!confirm('Are you sure you want to reject this booking?')) return;

    setIsActionLoading(true);
    try {
      const updated = await api.rejectBooking(parseInt(id!));
      setBooking(updated);
      toast.success('Booking rejected');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to reject booking');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleStartWork = async () => {
    setIsActionLoading(true);
    try {
      const updated = await api.startWork(parseInt(id!));
      setBooking(updated);
      toast.success('Work started');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to start work');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleComplete = async (data: { actual_hours?: number; notes?: string }) => {
    setIsActionLoading(true);
    try {
      const updated = await api.completeBooking(parseInt(id!), data.actual_hours, data.notes);
      setBooking(updated);
      toast.success('Booking marked as completed');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to complete booking');
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel this booking?')) return;

    setIsActionLoading(true);
    try {
      const updated = await api.cancelBooking(parseInt(id!));
      setBooking(updated);
      toast.success('Booking cancelled');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to cancel booking');
    } finally {
      setIsActionLoading(false);
    }
  };

  if (isLoading || !booking) {
    return <LoadingPage />;
  }

  const isCraftsman = user?.role === 'craftsman';
  const isHomeowner = user?.role === 'homeowner';
  const canAccept = isCraftsman && booking.status === 'pending';
  const canReject = isCraftsman && booking.status === 'pending';
  const canStart = isCraftsman && booking.status === 'confirmed';
  const canComplete = isCraftsman && booking.status === 'in_progress';
  const canCancel = booking.status === 'pending' || booking.status === 'accepted';

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      <Link to="/bookings" className="text-primary-600 hover:text-primary-700 mb-4 inline-block">
        ← Back to bookings
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header */}
          <div className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold mb-2">{booking.job_title}</h1>
                <BookingStatusBadge status={booking.status} />
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-primary-600">
                  €{booking.final_cost || booking.estimated_cost}
                </div>
                {booking.hourly_rate && (
                  <div className="text-sm text-gray-500">€{booking.hourly_rate}/hr</div>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Description</h3>
                <p className="text-gray-700">{booking.job_description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-1">Service Address</h3>
                  <p className="text-gray-700">{booking.service_address}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-1">
                    {booking.scheduled_date ? 'Scheduled Date' : 'Requested Date'}
                  </h3>
                  <p className="text-gray-700">
                    {format(
                      new Date(booking.scheduled_date || booking.requested_date),
                      'MMMM dd, yyyy'
                    )}
                  </p>
                </div>
              </div>

              {(booking.estimated_hours || booking.actual_hours) && (
                <div className="grid grid-cols-2 gap-4">
                  {booking.estimated_hours && (
                    <div>
                      <h3 className="font-semibold mb-1">Estimated Hours</h3>
                      <p className="text-gray-700">{booking.estimated_hours} hours</p>
                    </div>
                  )}
                  {booking.actual_hours && (
                    <div>
                      <h3 className="font-semibold mb-1">Actual Hours</h3>
                      <p className="text-gray-700">{booking.actual_hours} hours</p>
                    </div>
                  )}
                </div>
              )}

              {booking.notes && (
                <div>
                  <h3 className="font-semibold mb-1">Notes</h3>
                  <p className="text-gray-700">{booking.notes}</p>
                </div>
              )}
            </div>
          </div>

          {/* Accept Form */}
          {canAccept && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Accept Booking</h2>
              <form onSubmit={handleSubmitAccept(handleAccept)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Scheduled Date *
                  </label>
                  <input
                    type="date"
                    className={`input ${acceptErrors.scheduled_date ? 'border-red-500' : ''}`}
                    {...registerAccept('scheduled_date', { required: 'Date is required' })}
                  />
                  {acceptErrors.scheduled_date && (
                    <p className="text-red-500 text-sm mt-1">
                      {acceptErrors.scheduled_date.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Estimated Hours (Optional)
                  </label>
                  <input
                    type="number"
                    min="0.5"
                    step="0.5"
                    className="input"
                    {...registerAccept('estimated_hours', { valueAsNumber: true })}
                  />
                </div>

                <div className="flex gap-3">
                  <Button type="submit" isLoading={isActionLoading} fullWidth>
                    Accept Booking
                  </Button>
                  <Button
                    type="button"
                    variant="danger"
                    onClick={handleReject}
                    disabled={isActionLoading}
                    fullWidth
                  >
                    Reject
                  </Button>
                </div>
              </form>
            </div>
          )}

          {/* Complete Form */}
          {canComplete && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Mark as Completed</h2>
              <form onSubmit={handleSubmitComplete(handleComplete)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Actual Hours (Optional)
                  </label>
                  <input
                    type="number"
                    min="0.5"
                    step="0.5"
                    className="input"
                    {...registerComplete('actual_hours', { valueAsNumber: true })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes (Optional)
                  </label>
                  <textarea
                    rows={3}
                    className="input"
                    placeholder="Any additional notes about the completed work..."
                    {...registerComplete('notes')}
                  />
                </div>

                <Button type="submit" isLoading={isActionLoading} fullWidth>
                  Mark as Completed
                </Button>
              </form>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card space-y-4">
            <div>
              <h3 className="font-semibold mb-2">Booking Information</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Booking ID:</span>
                  <span className="font-medium">#{booking.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Created:</span>
                  <span className="font-medium">
                    {format(new Date(booking.created_at), 'MMM dd, yyyy')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Updated:</span>
                  <span className="font-medium">
                    {format(new Date(booking.updated_at), 'MMM dd, yyyy')}
                  </span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-3 pt-4 border-t">
              {canStart && (
                <Button onClick={handleStartWork} isLoading={isActionLoading} fullWidth>
                  Start Work
                </Button>
              )}

              {canCancel && (
                <Button
                  variant="danger"
                  onClick={handleCancel}
                  disabled={isActionLoading}
                  fullWidth
                >
                  Cancel Booking
                </Button>
              )}

              {booking.status === 'completed' && isHomeowner && (
                <Link to={`/bookings/${booking.id}/review`}>
                  <Button variant="primary" fullWidth>
                    Leave Review
                  </Button>
                </Link>
              )}

              <Link to={`/messages?booking=${booking.id}`}>
                <Button variant="secondary" fullWidth>
                  Send Message
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
