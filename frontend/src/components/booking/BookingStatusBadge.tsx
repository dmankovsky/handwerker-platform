import type { Booking } from '@/types';

interface BookingStatusBadgeProps {
  status: Booking['status'];
}

const STATUS_CONFIG = {
  pending: {
    label: 'Pending',
    className: 'badge-warning',
  },
  accepted: {
    label: 'Accepted',
    className: 'badge-info',
  },
  rejected: {
    label: 'Rejected',
    className: 'badge-danger',
  },
  confirmed: {
    label: 'Confirmed',
    className: 'badge-success',
  },
  in_progress: {
    label: 'In Progress',
    className: 'badge bg-blue-100 text-blue-800',
  },
  completed: {
    label: 'Completed',
    className: 'badge-success',
  },
  paid: {
    label: 'Paid',
    className: 'badge bg-green-100 text-green-800',
  },
  cancelled: {
    label: 'Cancelled',
    className: 'badge bg-gray-100 text-gray-800',
  },
  disputed: {
    label: 'Disputed',
    className: 'badge-danger',
  },
};

export function BookingStatusBadge({ status }: BookingStatusBadgeProps) {
  const config = STATUS_CONFIG[status];

  return <span className={config.className}>{config.label}</span>;
}
