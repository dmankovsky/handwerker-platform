import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import type { Booking } from '@/types';
import { BookingStatusBadge } from './BookingStatusBadge';

interface BookingCardProps {
  booking: Booking;
  userRole: 'homeowner' | 'craftsman';
}

export function BookingCard({ booking, userRole }: BookingCardProps) {
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM dd, yyyy');
  };

  return (
    <Link
      to={`/bookings/${booking.id}`}
      className="card hover:shadow-lg transition-shadow block"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {booking.job_title}
          </h3>
          <BookingStatusBadge status={booking.status} />
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-primary-600">
            €{booking.final_cost || booking.estimated_cost}
          </div>
          {booking.hourly_rate && (
            <div className="text-sm text-gray-500">
              €{booking.hourly_rate}/hr
            </div>
          )}
        </div>
      </div>

      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
        {booking.job_description}
      </p>

      <div className="grid grid-cols-2 gap-4 py-3 border-t border-gray-200">
        <div>
          <div className="text-xs text-gray-500 mb-1">
            {userRole === 'homeowner' ? 'Craftsman' : 'Homeowner'}
          </div>
          <div className="font-medium">
            {userRole === 'homeowner' ? `#${booking.craftsman_id}` : `#${booking.homeowner_id}`}
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500 mb-1">
            {booking.scheduled_date ? 'Scheduled' : 'Requested'}
          </div>
          <div className="font-medium">
            {formatDate(booking.scheduled_date || booking.requested_date)}
          </div>
        </div>

        {booking.service_address && (
          <div className="col-span-2">
            <div className="text-xs text-gray-500 mb-1">Location</div>
            <div className="font-medium text-sm">{booking.service_address}</div>
          </div>
        )}
      </div>

      {booking.estimated_hours && (
        <div className="mt-3 text-sm text-gray-600">
          Estimated: {booking.estimated_hours} hours
          {booking.actual_hours && ` • Actual: ${booking.actual_hours} hours`}
        </div>
      )}
    </Link>
  );
}
