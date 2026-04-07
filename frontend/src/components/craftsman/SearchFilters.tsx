import { useState, useEffect } from 'react';
import type { SearchFilters as SearchFiltersType, TradeType } from '@/types';
import { api } from '@/services/api';

interface SearchFiltersProps {
  filters: SearchFiltersType;
  onFilterChange: (filters: SearchFiltersType) => void;
}

const TRADE_LABELS: Record<TradeType, string> = {
  electrician: 'Electrician',
  plumber: 'Plumber',
  carpenter: 'Carpenter',
  painter: 'Painter',
  roofer: 'Roofer',
  mason: 'Mason',
  tiler: 'Tiler',
  flooring: 'Flooring Specialist',
  hvac: 'HVAC Technician',
  locksmith: 'Locksmith',
  glazier: 'Glazier',
  landscaper: 'Landscaper',
  renovation: 'Renovation Specialist',
  other: 'Other',
};

export function SearchFilters({ filters, onFilterChange }: SearchFiltersProps) {
  const [serviceAreas, setServiceAreas] = useState<string[]>([]);
  const [isExpanded, setIsExpanded] = useState(true);

  useEffect(() => {
    loadServiceAreas();
  }, []);

  const loadServiceAreas = async () => {
    try {
      const areas = await api.getServiceAreas();
      setServiceAreas(areas);
    } catch (error) {
      console.error('Failed to load service areas:', error);
    }
  };

  const handleTradeChange = (trade: TradeType | undefined) => {
    onFilterChange({ ...filters, trade });
  };

  const handleServiceAreaChange = (area: string) => {
    onFilterChange({ ...filters, service_area: area || undefined });
  };

  const handleMinRatingChange = (rating: number | undefined) => {
    onFilterChange({ ...filters, min_rating: rating });
  };

  const handleMaxRateChange = (rate: string) => {
    const maxRate = rate ? parseFloat(rate) : undefined;
    onFilterChange({ ...filters, max_hourly_rate: maxRate });
  };

  const handleVerifiedToggle = () => {
    onFilterChange({ ...filters, verified_only: !filters.verified_only });
  };

  const clearFilters = () => {
    onFilterChange({});
  };

  const hasActiveFilters = Object.keys(filters).some(
    (key) => filters[key as keyof SearchFiltersType] !== undefined
  );

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Filters</h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-primary-600 hover:text-primary-700 lg:hidden"
        >
          {isExpanded ? 'Hide' : 'Show'}
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-6">
          {/* Trade Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Trade
            </label>
            <select
              value={filters.trade || ''}
              onChange={(e) => handleTradeChange(e.target.value as TradeType || undefined)}
              className="input"
            >
              <option value="">All Trades</option>
              {Object.entries(TRADE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {/* Service Area */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Service Area
            </label>
            <select
              value={filters.service_area || ''}
              onChange={(e) => handleServiceAreaChange(e.target.value)}
              className="input"
            >
              <option value="">All Areas</option>
              {serviceAreas.map((area) => (
                <option key={area} value={area}>
                  {area}
                </option>
              ))}
            </select>
          </div>

          {/* Minimum Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Rating
            </label>
            <div className="space-y-2">
              {[4, 3, 2, 1].map((rating) => (
                <label key={rating} className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="rating"
                    checked={filters.min_rating === rating}
                    onChange={() => handleMinRatingChange(rating)}
                    className="mr-2"
                  />
                  <div className="flex items-center">
                    {Array.from({ length: 5 }).map((_, i) => (
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
                    <span className="ml-2 text-sm text-gray-600">& up</span>
                  </div>
                </label>
              ))}
              {filters.min_rating && (
                <button
                  onClick={() => handleMinRatingChange(undefined)}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Clear rating filter
                </button>
              )}
            </div>
          </div>

          {/* Max Hourly Rate */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Hourly Rate (€)
            </label>
            <input
              type="number"
              min="0"
              step="5"
              value={filters.max_hourly_rate || ''}
              onChange={(e) => handleMaxRateChange(e.target.value)}
              placeholder="Any"
              className="input"
            />
          </div>

          {/* Verified Only */}
          <div>
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={filters.verified_only || false}
                onChange={handleVerifiedToggle}
                className="mr-2 w-4 h-4 text-primary-600 rounded"
              />
              <span className="text-sm font-medium text-gray-700">
                Verified craftsmen only
              </span>
            </label>
          </div>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="w-full btn-secondary text-sm"
            >
              Clear All Filters
            </button>
          )}
        </div>
      )}
    </div>
  );
}
