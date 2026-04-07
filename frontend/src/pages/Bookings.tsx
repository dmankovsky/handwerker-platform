import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingPage, Button } from '@/components/common';
import { BookingCard } from '@/components/booking/BookingCard';
import type { Booking } from '@/types';

export function Bookings() {
  const { user } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'pending' | 'active' | 'completed'>('all');

  useEffect(() => {
    loadBookings();
  }, []);

  const loadBookings = async () => {
    setIsLoading(true);
    try {
      const data = await api.getMyBookings();
      setBookings(data);
    } catch (error) {
      console.error('Failed to load bookings:', error);
      toast.error('Failed to load bookings');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredBookings = bookings.filter((booking) => {
    if (filter === 'all') return true;
    if (filter === 'pending') return booking.status === 'pending';
    if (filter === 'active')
      return ['accepted', 'confirmed', 'in_progress'].includes(booking.status);
    if (filter === 'completed') return ['completed', 'paid'].includes(booking.status);
    return true;
  });

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Bookings</h1>
          <p className="text-gray-600">
            {user?.role === 'homeowner'
              ? 'Manage your service bookings'
              : 'Manage your booking requests'}
          </p>
        </div>
        {user?.role === 'homeowner' && (
          <Link to="/bookings/new">
            <Button>Create Booking</Button>
          </Link>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-6">
          {[
            { key: 'all', label: 'All', count: bookings.length },
            {
              key: 'pending',
              label: 'Pending',
              count: bookings.filter((b) => b.status === 'pending').length,
            },
            {
              key: 'active',
              label: 'Active',
              count: bookings.filter((b) =>
                ['accepted', 'confirmed', 'in_progress'].includes(b.status)
              ).length,
            },
            {
              key: 'completed',
              label: 'Completed',
              count: bookings.filter((b) => ['completed', 'paid'].includes(b.status))
                .length,
            },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key as any)}
              className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                filter === tab.key
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>
      </div>

      {/* Bookings List */}
      {filteredBookings.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBookings.map((booking) => (
            <BookingCard
              key={booking.id}
              booking={booking}
              userRole={user?.role as 'homeowner' | 'craftsman'}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 card">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No bookings found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {filter === 'all'
              ? user?.role === 'homeowner'
                ? "You haven't created any bookings yet"
                : "You haven't received any booking requests yet"
              : `No ${filter} bookings`}
          </p>
          {user?.role === 'homeowner' && filter === 'all' && (
            <Link to="/bookings/new" className="mt-4 inline-block">
              <Button>Create Your First Booking</Button>
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
