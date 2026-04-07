import { Link } from 'react-router-dom';
import type { CraftsmanProfile } from '@/types';

interface CraftsmanCardProps {
  craftsman: CraftsmanProfile & { user?: { full_name: string } };
}

export function CraftsmanCard({ craftsman }: CraftsmanCardProps) {
  const displayName = craftsman.company_name || craftsman.user?.full_name || 'Craftsman';

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-xl font-semibold">{displayName}</h3>
            {craftsman.is_verified && (
              <span className="badge-success">
                <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                Verified
              </span>
            )}
          </div>

          {craftsman.bio && (
            <p className="text-gray-600 text-sm line-clamp-2 mb-3">{craftsman.bio}</p>
          )}
        </div>
      </div>

      {/* Trades */}
      <div className="mb-3">
        <div className="flex flex-wrap gap-2">
          {craftsman.trades.slice(0, 3).map((trade) => (
            <span key={trade} className="badge-info capitalize">
              {trade.replace('_', ' ')}
            </span>
          ))}
          {craftsman.trades.length > 3 && (
            <span className="badge bg-gray-100 text-gray-600">
              +{craftsman.trades.length - 3} more
            </span>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 py-3 border-t border-gray-200 mb-4">
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-yellow-500 font-semibold">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            {craftsman.average_rating?.toFixed(1) || 'N/A'}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {craftsman.total_reviews} reviews
          </div>
        </div>

        <div className="text-center">
          <div className="font-semibold text-gray-900">{craftsman.total_jobs}</div>
          <div className="text-xs text-gray-500 mt-1">Jobs</div>
        </div>

        <div className="text-center">
          <div className="font-semibold text-gray-900">
            {craftsman.years_experience || '—'}
          </div>
          <div className="text-xs text-gray-500 mt-1">Years</div>
        </div>
      </div>

      {/* Hourly Rate & CTA */}
      <div className="flex items-center justify-between">
        <div>
          {craftsman.hourly_rate && (
            <div className="text-2xl font-bold text-primary-600">
              €{craftsman.hourly_rate}
              <span className="text-sm text-gray-500 font-normal">/hour</span>
            </div>
          )}
        </div>
        <Link
          to={`/craftsman/${craftsman.id}`}
          className="btn-primary"
        >
          View Profile
        </Link>
      </div>

      {!craftsman.accepts_bookings && (
        <div className="mt-3 text-center">
          <span className="badge-warning">Not accepting bookings</span>
        </div>
      )}
    </div>
  );
}
