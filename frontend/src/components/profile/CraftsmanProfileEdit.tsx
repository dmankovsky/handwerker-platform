import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import { api } from '@/services/api';
import { Button, Input, LoadingPage } from '@/components/common';
import { validationRules } from '@/utils/validation';
import type { User, CraftsmanProfile, TradeType } from '@/types';

interface CraftsmanProfileEditProps {
  user: User;
}

interface ProfileFormData {
  company_name?: string;
  bio?: string;
  years_experience?: number;
  hourly_rate?: number;
  accepts_bookings: boolean;
  trades: string[];
  service_areas: string[];
}

const TRADE_OPTIONS: { value: TradeType; label: string }[] = [
  { value: 'electrician', label: 'Electrician' },
  { value: 'plumber', label: 'Plumber' },
  { value: 'carpenter', label: 'Carpenter' },
  { value: 'painter', label: 'Painter' },
  { value: 'roofer', label: 'Roofer' },
  { value: 'mason', label: 'Mason' },
  { value: 'tiler', label: 'Tiler' },
  { value: 'flooring', label: 'Flooring Specialist' },
  { value: 'hvac', label: 'HVAC Technician' },
  { value: 'locksmith', label: 'Locksmith' },
  { value: 'glazier', label: 'Glazier' },
  { value: 'landscaper', label: 'Landscaper' },
  { value: 'renovation', label: 'Renovation Specialist' },
  { value: 'other', label: 'Other' },
];

const SERVICE_AREA_OPTIONS = [
  'Berlin',
  'Munich',
  'Hamburg',
  'Frankfurt',
  'Cologne',
  'Stuttgart',
  'Düsseldorf',
  'Dortmund',
  'Essen',
  'Leipzig',
];

export function CraftsmanProfileEdit({ user }: CraftsmanProfileEditProps) {
  const [profile, setProfile] = useState<CraftsmanProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [selectedTrades, setSelectedTrades] = useState<string[]>([]);
  const [selectedAreas, setSelectedAreas] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProfileFormData>();

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setIsLoading(true);
    try {
      const data = await api.getMyCraftsmanProfile();
      setProfile(data);
      setSelectedTrades(data.trades || []);
      setSelectedAreas(data.service_areas || []);

      reset({
        company_name: data.company_name || '',
        bio: data.bio || '',
        years_experience: data.years_experience || undefined,
        hourly_rate: data.hourly_rate || undefined,
        accepts_bookings: data.accepts_bookings ?? true,
      });
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = async (data: ProfileFormData) => {
    if (selectedTrades.length === 0) {
      toast.error('Please select at least one trade');
      return;
    }

    if (selectedAreas.length === 0) {
      toast.error('Please select at least one service area');
      return;
    }

    setIsSaving(true);
    try {
      const updated = await api.updateCraftsmanProfile({
        ...data,
        trades: selectedTrades,
        service_areas: selectedAreas,
      });
      setProfile(updated);
      toast.success('Profile updated successfully');
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const toggleTrade = (trade: string) => {
    setSelectedTrades((prev) =>
      prev.includes(trade) ? prev.filter((t) => t !== trade) : [...prev, trade]
    );
  };

  const toggleArea = (area: string) => {
    setSelectedAreas((prev) =>
      prev.includes(area) ? prev.filter((a) => a !== area) : [...prev, area]
    );
  };

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Basic Information */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Basic Information</h2>

        <div className="space-y-4">
          <Input
            label="Company Name (Optional)"
            type="text"
            placeholder="e.g., Müller Handwerk GmbH"
            error={errors.company_name?.message}
            {...register('company_name')}
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bio / About You
            </label>
            <textarea
              rows={4}
              className={`input ${errors.bio ? 'border-red-500' : ''}`}
              placeholder="Tell customers about your experience and expertise..."
              {...register('bio', validationRules.maxLength('Bio', 500))}
            />
            {errors.bio && (
              <p className="text-red-500 text-sm mt-1">{errors.bio.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Years of Experience"
              type="number"
              min="0"
              placeholder="e.g., 10"
              error={errors.years_experience?.message}
              {...register('years_experience', { valueAsNumber: true })}
            />

            <Input
              label="Hourly Rate (€)"
              type="number"
              min="0"
              step="5"
              placeholder="e.g., 75"
              error={errors.hourly_rate?.message}
              {...register('hourly_rate', { valueAsNumber: true })}
            />
          </div>

          <div>
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="mr-2 w-4 h-4 text-primary-600 rounded"
                {...register('accepts_bookings')}
              />
              <span className="text-sm font-medium text-gray-700">
                Accept new booking requests
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Trades */}
      <div className="card">
        <h2 className="text-xl font-bold mb-2">Trades & Services</h2>
        <p className="text-gray-600 mb-4">Select all trades you offer</p>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {TRADE_OPTIONS.map((trade) => (
            <button
              key={trade.value}
              type="button"
              onClick={() => toggleTrade(trade.value)}
              className={`p-3 border-2 rounded-lg text-left transition-all ${
                selectedTrades.includes(trade.value)
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <span className="font-medium">{trade.label}</span>
            </button>
          ))}
        </div>

        {selectedTrades.length === 0 && (
          <p className="text-red-500 text-sm mt-2">Please select at least one trade</p>
        )}
      </div>

      {/* Service Areas */}
      <div className="card">
        <h2 className="text-xl font-bold mb-2">Service Areas</h2>
        <p className="text-gray-600 mb-4">Select all cities you serve</p>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {SERVICE_AREA_OPTIONS.map((area) => (
            <button
              key={area}
              type="button"
              onClick={() => toggleArea(area)}
              className={`p-3 border-2 rounded-lg text-left transition-all ${
                selectedAreas.includes(area)
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <span className="font-medium">{area}</span>
            </button>
          ))}
        </div>

        {selectedAreas.length === 0 && (
          <p className="text-red-500 text-sm mt-2">
            Please select at least one service area
          </p>
        )}
      </div>

      {/* Profile Stats */}
      {profile && (
        <div className="card bg-gray-50">
          <h2 className="text-xl font-bold mb-4">Profile Statistics</h2>

          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {profile.total_jobs}
              </div>
              <div className="text-sm text-gray-600">Jobs Completed</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {profile.average_rating?.toFixed(1) || 'N/A'}
              </div>
              <div className="text-sm text-gray-600">Average Rating</div>
            </div>

            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {profile.total_reviews}
              </div>
              <div className="text-sm text-gray-600">Reviews</div>
            </div>
          </div>

          {profile.is_verified && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-medium text-green-900">
                  Your profile is verified
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Submit */}
      <div className="flex gap-3">
        <Button type="submit" isLoading={isSaving} fullWidth>
          Save Profile
        </Button>
      </div>
    </form>
  );
}
