import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  User,
  AuthResponse,
  LoginCredentials,
  RegisterData,
  CraftsmanProfile,
  Booking,
  Review,
  Message,
  Payment,
  SearchFilters
} from '@/types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const { data } = await this.client.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return data;
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const { data } = await this.client.post<AuthResponse>('/auth/register', userData);
    return data;
  }

  async getCurrentUser(): Promise<User> {
    const { data } = await this.client.get<User>('/auth/me');
    return data;
  }

  // Craftsman endpoints
  async searchCraftsmen(filters?: SearchFilters): Promise<CraftsmanProfile[]> {
    const { data } = await this.client.get<CraftsmanProfile[]>('/craftsman/search', {
      params: filters,
    });
    return data;
  }

  async getCraftsmanProfile(id: number): Promise<CraftsmanProfile> {
    const { data } = await this.client.get<CraftsmanProfile>(`/craftsman/${id}`);
    return data;
  }

  async getMyCraftsmanProfile(): Promise<CraftsmanProfile> {
    const { data } = await this.client.get<CraftsmanProfile>('/craftsman/profile/me');
    return data;
  }

  async updateCraftsmanProfile(profileData: Partial<CraftsmanProfile>): Promise<CraftsmanProfile> {
    const { data } = await this.client.put<CraftsmanProfile>('/craftsman/profile', profileData);
    return data;
  }

  async getTrades(): Promise<string[]> {
    const { data } = await this.client.get<string[]>('/craftsman/trades');
    return data;
  }

  async getServiceAreas(): Promise<string[]> {
    const { data } = await this.client.get<string[]>('/craftsman/service-areas');
    return data;
  }

  // Booking endpoints
  async createBooking(bookingData: Partial<Booking>): Promise<Booking> {
    const { data } = await this.client.post<Booking>('/bookings/', bookingData);
    return data;
  }

  async getMyBookings(): Promise<Booking[]> {
    const { data } = await this.client.get<Booking[]>('/bookings/');
    return data;
  }

  async getBooking(id: number): Promise<Booking> {
    const { data } = await this.client.get<Booking>(`/bookings/${id}`);
    return data;
  }

  async acceptBooking(id: number, scheduledDate: string, estimatedHours?: number): Promise<Booking> {
    const { data } = await this.client.post<Booking>(`/bookings/${id}/accept`, {
      scheduled_date: scheduledDate,
      estimated_hours: estimatedHours,
    });
    return data;
  }

  async rejectBooking(id: number): Promise<Booking> {
    const { data } = await this.client.post<Booking>(`/bookings/${id}/reject`);
    return data;
  }

  async startWork(id: number): Promise<Booking> {
    const { data } = await this.client.post<Booking>(`/bookings/${id}/start`);
    return data;
  }

  async completeBooking(id: number, actualHours?: number, notes?: string): Promise<Booking> {
    const { data } = await this.client.post<Booking>(`/bookings/${id}/complete`, {
      actual_hours: actualHours,
      notes,
    });
    return data;
  }

  async cancelBooking(id: number): Promise<Booking> {
    const { data } = await this.client.post<Booking>(`/bookings/${id}/cancel`);
    return data;
  }

  // Review endpoints
  async createReview(reviewData: Partial<Review>): Promise<Review> {
    const { data } = await this.client.post<Review>('/reviews/', reviewData);
    return data;
  }

  async getCraftsmanReviews(craftsmanId: number): Promise<Review[]> {
    const { data } = await this.client.get<Review[]>(`/reviews/craftsman/${craftsmanId}`);
    return data;
  }

  async getBookingReview(bookingId: number): Promise<Review | null> {
    try {
      const { data } = await this.client.get<Review>(`/reviews/booking/${bookingId}`);
      return data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async respondToReview(reviewId: number, response: string): Promise<Review> {
    const { data } = await this.client.post<Review>(`/reviews/${reviewId}/respond`, {
      response,
    });
    return data;
  }

  // Message endpoints
  async sendMessage(receiverId: number, content: string, bookingId?: number): Promise<Message> {
    const { data } = await this.client.post<Message>('/messages/', {
      receiver_id: receiverId,
      content,
      booking_id: bookingId,
    });
    return data;
  }

  async getBookingMessages(bookingId: number): Promise<Message[]> {
    const { data } = await this.client.get<Message[]>(`/messages/booking/${bookingId}`);
    return data;
  }

  async getMessageThreads(): Promise<any[]> {
    const { data } = await this.client.get<any[]>('/messages/threads');
    return data;
  }

  async markMessageAsRead(messageId: number): Promise<void> {
    await this.client.post(`/messages/${messageId}/read`);
  }

  async getUnreadCount(): Promise<number> {
    const { data } = await this.client.get<{ unread_count: number }>('/messages/unread-count');
    return data.unread_count;
  }

  // Payment endpoints
  async createPaymentIntent(bookingId: number): Promise<{ client_secret: string }> {
    const { data } = await this.client.post('/payments/intent', { booking_id: bookingId });
    return data;
  }

  async confirmPayment(bookingId: number, paymentIntentId: string): Promise<Payment> {
    const { data } = await this.client.post<Payment>('/payments/confirm', {
      booking_id: bookingId,
      payment_intent_id: paymentIntentId,
    });
    return data;
  }

  async getPaymentHistory(): Promise<Payment[]> {
    const { data } = await this.client.get<Payment[]>('/payments/history');
    return data;
  }

  // Verification endpoints
  async uploadDocument(file: File, documentType: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    const { data } = await this.client.post('/verification/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  }

  async getVerificationStatus(): Promise<any> {
    const { data } = await this.client.get('/verification/status');
    return data;
  }

  // i18n endpoints
  async getTranslations(language: string): Promise<any> {
    const { data } = await this.client.get('/i18n/translations', {
      params: { lang: language },
    });
    return data;
  }

  async getSupportedLanguages(): Promise<string[]> {
    const { data } = await this.client.get<{ supported_languages: string[] }>('/i18n/languages');
    return data.supported_languages;
  }
}

export const api = new ApiService();
