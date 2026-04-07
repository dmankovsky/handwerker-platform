import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { LoadingPage } from '@/components/common';
import { CraftsmanCard } from '@/components/craftsman/CraftsmanCard';
import { SearchFilters } from '@/components/craftsman/SearchFilters';
import type { CraftsmanProfile, SearchFilters as SearchFiltersType } from '@/types';

export function Search() {
  const [craftsmen, setCraftsmen] = useState<CraftsmanProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<SearchFiltersType>({});

  useEffect(() => {
    searchCraftsmen();
  }, [filters]);

  const searchCraftsmen = async () => {
    setIsLoading(true);
    try {
      const results = await api.searchCraftsmen(filters);
      setCraftsmen(results);
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Failed to search craftsmen. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (newFilters: SearchFiltersType) => {
    setFilters(newFilters);
  };

  if (isLoading && craftsmen.length === 0) {
    return <LoadingPage />;
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Find Trusted Craftsmen
        </h1>
        <p className="text-gray-600">
          Browse verified craftsmen in your area and book services online
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <SearchFilters filters={filters} onFilterChange={handleFilterChange} />
        </div>

        {/* Results */}
        <div className="lg:col-span-3">
          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingPage />
            </div>
          ) : (
            <>
              {/* Results Count */}
              <div className="mb-6">
                <p className="text-gray-600">
                  Found <strong>{craftsmen.length}</strong> craftsmen
                  {Object.keys(filters).length > 0 && ' matching your filters'}
                </p>
              </div>

              {/* Results Grid */}
              {craftsmen.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {craftsmen.map((craftsman) => (
                    <CraftsmanCard key={craftsman.id} craftsman={craftsman} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
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
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">
                    No craftsmen found
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Try adjusting your filters or search criteria
                  </p>
                  {Object.keys(filters).length > 0 && (
                    <button
                      onClick={() => setFilters({})}
                      className="mt-4 btn-primary"
                    >
                      Clear Filters
                    </button>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
