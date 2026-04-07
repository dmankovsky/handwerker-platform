import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingPage } from '@/components/common';
import { HomeownerProfile } from '@/components/profile/HomeownerProfile';
import { CraftsmanProfileEdit } from '@/components/profile/CraftsmanProfileEdit';

export function Profile() {
  const { user, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'verification'>('profile');

  if (isLoading) {
    return <LoadingPage />;
  }

  if (!user) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Profile</h1>
        <p className="text-gray-600">
          {user.role === 'homeowner'
            ? 'Manage your personal information'
            : 'Manage your craftsman profile and verification'}
        </p>
      </div>

      {/* Tabs for Craftsmen */}
      {user.role === 'craftsman' && (
        <div className="mb-6 border-b border-gray-200">
          <div className="flex gap-6">
            <button
              onClick={() => setActiveTab('profile')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'profile'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Profile
            </button>
            <button
              onClick={() => setActiveTab('verification')}
              className={`pb-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'verification'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Verification
            </button>
          </div>
        </div>
      )}

      {/* Content */}
      {user.role === 'homeowner' ? (
        <HomeownerProfile user={user} />
      ) : (
        <>
          {activeTab === 'profile' && <CraftsmanProfileEdit user={user} />}
          {activeTab === 'verification' && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Verification Documents</h2>
              <p className="text-gray-600 mb-4">
                Upload your business documents to get verified and gain customer trust.
              </p>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-900">
                  Document upload functionality coming soon. Contact support to submit your
                  verification documents.
                </p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
