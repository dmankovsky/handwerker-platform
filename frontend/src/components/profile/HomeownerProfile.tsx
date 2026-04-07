import { format } from 'date-fns';
import type { User } from '@/types';

interface HomeownerProfileProps {
  user: User;
}

export function HomeownerProfile({ user }: HomeownerProfileProps) {
  return (
    <div className="space-y-6">
      {/* Personal Information */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Personal Information</h2>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <p className="text-gray-900">{user.full_name}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <p className="text-gray-900">{user.email}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <p className="text-gray-900">{user.phone}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Member Since
              </label>
              <p className="text-gray-900">
                {format(new Date(user.created_at), 'MMMM yyyy')}
              </p>
            </div>
          </div>

          {user.street_address && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <p className="text-gray-900">
                {user.street_address}
                {user.city && `, ${user.city}`}
                {user.postal_code && ` ${user.postal_code}`}
                {user.state && `, ${user.state}`}
              </p>
            </div>
          )}
        </div>

        <div className="mt-6">
          <button className="btn-primary" disabled>
            Edit Profile (Coming Soon)
          </button>
        </div>
      </div>

      {/* Account Status */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Account Status</h2>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-700">Account Active</span>
            <span className={user.is_active ? 'badge-success' : 'badge-danger'}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-gray-700">Email Verified</span>
            <span className={user.email_verified ? 'badge-success' : 'badge-warning'}>
              {user.email_verified ? 'Verified' : 'Not Verified'}
            </span>
          </div>
        </div>

        {!user.email_verified && (
          <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <p className="text-sm text-yellow-900">
              Please verify your email address to access all features.
            </p>
            <button className="mt-2 text-sm text-yellow-900 font-semibold hover:underline">
              Resend Verification Email
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
