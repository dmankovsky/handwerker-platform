import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingPage, Button } from '@/components/common';
import { ReviewCard } from '@/components/review';
import type { CraftsmanProfile, Review } from '@/types';

export function CraftsmanProfile() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [craftsman, setCraftsman] = useState<CraftsmanProfile | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadCraftsman();
      loadReviews();
    }
  }, [id]);

  const loadCraftsman = async () => {
    try {
      const data = await api.getCraftsmanProfile(parseInt(id!));
      setCraftsman(data);
    } catch (error) {
      console.error('Failed to load craftsman:', error);
      toast.error('Failed to load craftsman profile');
      navigate('/search');
    } finally {
      setIsLoading(false);
    }
  };

  const loadReviews = async () => {
    try {
      const data = await api.getCraftsmanReviews(parseInt(id!));
      setReviews(data);
    } catch (error) {
      console.error('Failed to load reviews:', error);
    }
  };

  const handleBookNow = () => {
    if (!isAuthenticated) {
      toast.info('Please log in to book a craftsman');
      navigate('/login');
      return;
    }

    if (user?.role !== 'homeowner') {
      toast.error('Only homeowners can book craftsmen');
      return;
    }

    navigate('/bookings/new', { state: { craftsmanId: craftsman?.id } });
  };

  if (isLoading || !craftsman) {
    return <LoadingPage />;
  }

  const displayName = craftsman.company_name || `Craftsman #${craftsman.id}`;

  return (
    <div className="max-w-5xl mx-auto">
      {/* Back Button */}
      <Link to="/search" className="text-primary-600 hover:text-primary-700 mb-4 inline-block">
        ← Back to search
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Profile */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header */}
          <div className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <h1 className="text-3xl font-bold">{displayName}</h1>
                  {craftsman.is_verified && (
                    <span className="badge-success">
                      <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path
                          fillRule="evenodd"
                          d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                      Verified Craftsman
                    </span>
                  )}
                </div>

                {/* Rating */}
                {craftsman.average_rating && (
                  <div className="flex items-center gap-2">
                    <div className="flex items-center">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <svg
                          key={i}
                          className={`w-5 h-5 ${
                            i < Math.floor(craftsman.average_rating!)
                              ? 'text-yellow-400'
                              : 'text-gray-300'
                          }`}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                    <span className="font-semibold">{craftsman.average_rating.toFixed(1)}</span>
                    <span className="text-gray-500">({craftsman.total_reviews} reviews)</span>
                  </div>
                )}
              </div>
            </div>

            {/* Bio */}
            {craftsman.bio && (
              <div className="mb-6">
                <h3 className="font-semibold mb-2">About</h3>
                <p className="text-gray-700">{craftsman.bio}</p>
              </div>
            )}

            {/* Trades */}
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Services</h3>
              <div className="flex flex-wrap gap-2">
                {craftsman.trades.map((trade) => (
                  <span key={trade} className="badge-info capitalize">
                    {trade.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>

            {/* Service Areas */}
            {craftsman.service_areas.length > 0 && (
              <div>
                <h3 className="font-semibold mb-2">Service Areas</h3>
                <div className="flex flex-wrap gap-2">
                  {craftsman.service_areas.map((area) => (
                    <span key={area} className="badge bg-gray-100 text-gray-700">
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Reviews */}
          <div className="card">
            <h2 className="text-2xl font-bold mb-4">
              Reviews ({reviews.length})
            </h2>

            {reviews.length > 0 ? (
              <div className="space-y-6">
                {reviews.map((review) => (
                  <ReviewCard
                    key={review.id}
                    review={review}
                    onResponseAdded={(updatedReview) => {
                      setReviews(
                        reviews.map((r) => (r.id === updatedReview.id ? updatedReview : r))
                      );
                    }}
                  />
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No reviews yet</p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card sticky top-4">
            {/* Stats */}
            <div className="mb-6">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {craftsman.total_jobs}
                  </div>
                  <div className="text-sm text-gray-600">Jobs Completed</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {craftsman.years_experience || '—'}
                  </div>
                  <div className="text-sm text-gray-600">Years Experience</div>
                </div>
              </div>

              {craftsman.hourly_rate && (
                <div className="text-center p-4 bg-primary-50 rounded-lg border border-primary-200">
                  <div className="text-3xl font-bold text-primary-600">
                    €{craftsman.hourly_rate}
                  </div>
                  <div className="text-sm text-gray-600">per hour</div>
                </div>
              )}
            </div>

            {/* CTA */}
            {craftsman.accepts_bookings ? (
              <Button
                onClick={handleBookNow}
                variant="primary"
                size="lg"
                fullWidth
              >
                Book Now
              </Button>
            ) : (
              <div className="text-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  This craftsman is not currently accepting new bookings
                </p>
              </div>
            )}

            {isAuthenticated && user?.role === 'homeowner' && (
              <Link
                to={`/messages?craftsman=${craftsman.id}`}
                className="mt-3 btn-secondary w-full text-center"
              >
                Send Message
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
