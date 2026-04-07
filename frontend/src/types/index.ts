export interface User {
  id: number;
  email: string;
  full_name: string;
  phone: string;
  role: 'homeowner' | 'craftsman' | 'admin';
  created_at: string;
}

export interface CraftsmanProfile {
  id: number;
  user_id: number;
  company_name?: string;
  bio?: string;
  years_experience?: number;
  trades: string[];
  service_areas: string[];
  hourly_rate?: number;
  average_rating?: number;
  total_reviews: number;
  total_jobs: number;
  is_verified: boolean;
  accepts_bookings: boolean;
  portfolio_images: string[];
}

export interface Booking {
  id: number;
  homeowner_id: number;
  craftsman_id: number;
  job_title: string;
  job_description: string;
  service_address: string;
  requested_date: string;
  scheduled_date?: string;
  estimated_hours?: number;
  actual_hours?: number;
  hourly_rate: number;
  estimated_cost: number;
  final_cost?: number;
  status: 'pending' | 'accepted' | 'rejected' | 'confirmed' | 'in_progress' | 'completed' | 'paid' | 'cancelled' | 'disputed';
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: number;
  booking_id: number;
  craftsman_id: number;
  homeowner_id: number;
  rating: number;
  quality_rating: number;
  communication_rating: number;
  punctuality_rating: number;
  value_rating: number;
  comment?: string;
  response?: string;
  created_at: string;
}

export interface Message {
  id: number;
  sender_id: number;
  receiver_id: number;
  booking_id?: number;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface Payment {
  id: number;
  booking_id: number;
  homeowner_id: number;
  craftsman_id: number;
  amount: number;
  platform_fee: number;
  craftsman_payout: number;
  stripe_payment_intent_id: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  created_at: string;
}

export interface VerificationDocument {
  id: number;
  profile_id: number;
  document_type: 'business_license' | 'handwerkskammer_certificate' | 'insurance_certificate' | 'id_card' | 'tax_certificate';
  file_path: string;
  is_verified: boolean;
  verified_at?: string;
  verified_by?: number;
  notes?: string;
  uploaded_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  role: 'homeowner' | 'craftsman';
}

export type TradeType =
  | 'electrician'
  | 'plumber'
  | 'carpenter'
  | 'painter'
  | 'roofer'
  | 'mason'
  | 'tiler'
  | 'flooring'
  | 'hvac'
  | 'locksmith'
  | 'glazier'
  | 'landscaper'
  | 'renovation'
  | 'other';

export interface SearchFilters {
  trade?: TradeType;
  service_area?: string;
  min_rating?: number;
  max_hourly_rate?: number;
  verified_only?: boolean;
}
