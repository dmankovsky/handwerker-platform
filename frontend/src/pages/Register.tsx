import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import { useAuth } from '@/contexts/AuthContext';
import { Button, Input } from '@/components/common';
import { validationRules, confirmPassword } from '@/utils/validation';
import type { RegisterData } from '@/types';

export function Register() {
  const navigate = useNavigate();
  const { register: registerUser } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState<'homeowner' | 'craftsman'>('homeowner');

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterData & { confirm_password: string }>({
    defaultValues: {
      role: 'homeowner',
    },
  });

  const password = watch('password');

  const onSubmit = async (data: RegisterData & { confirm_password: string }) => {
    setIsLoading(true);
    try {
      const { confirm_password, ...registerData } = data;
      await registerUser({ ...registerData, role: selectedRole });
      toast.success('Registration successful! Welcome to Handwerker Platform.');
      navigate('/');
    } catch (error: any) {
      console.error('Registration error:', error);
      const message =
        error.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <h1 className="text-3xl font-bold text-center mb-2">Create Your Account</h1>
        <p className="text-gray-600 text-center mb-8">
          Join Handwerker Platform as a homeowner or craftsman
        </p>

        {/* Role Selection */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            I want to register as:
          </label>
          <div className="grid grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setSelectedRole('homeowner')}
              className={`p-4 border-2 rounded-lg text-left transition-all ${
                selectedRole === 'homeowner'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="font-semibold text-lg mb-1">Homeowner</div>
              <div className="text-sm text-gray-600">
                Find and hire verified craftsmen for your projects
              </div>
            </button>

            <button
              type="button"
              onClick={() => setSelectedRole('craftsman')}
              className={`p-4 border-2 rounded-lg text-left transition-all ${
                selectedRole === 'craftsman'
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              <div className="font-semibold text-lg mb-1">Craftsman</div>
              <div className="text-sm text-gray-600">
                Grow your business by connecting with homeowners
              </div>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Input
            label="Full Name"
            type="text"
            placeholder="John Doe"
            error={errors.full_name?.message}
            {...register('full_name', validationRules.minLength('Full name', 2))}
          />

          <Input
            label="Email Address"
            type="email"
            placeholder="your.email@example.com"
            error={errors.email?.message}
            {...register('email', validationRules.email)}
          />

          <Input
            label="Phone Number"
            type="tel"
            placeholder="+49 123 456789"
            error={errors.phone?.message}
            {...register('phone', validationRules.phone)}
          />

          <Input
            label="Password"
            type="password"
            placeholder="Create a strong password"
            error={errors.password?.message}
            helperText="Minimum 6 characters"
            {...register('password', validationRules.password)}
          />

          <Input
            label="Confirm Password"
            type="password"
            placeholder="Re-enter your password"
            error={errors.confirm_password?.message}
            {...register('confirm_password', confirmPassword(password))}
          />

          {selectedRole === 'craftsman' && (
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-900">
                <strong>Note for Craftsmen:</strong> After registration, you'll need to complete
                your profile and upload verification documents (business license, insurance
                certificate, etc.) to start receiving bookings.
              </p>
            </div>
          )}

          <Button type="submit" isLoading={isLoading} fullWidth>
            Create Account
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
