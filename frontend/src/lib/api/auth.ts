import { apiClient } from './client';
import type { UserBrief } from '@/types/user';

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserBrief;
}

interface RegisterResponse {
  detail: string;
  email: string;
  requires_verification: boolean;
}

export const authApi = {
  register: async (email: string, password: string): Promise<RegisterResponse> => {
    return apiClient.post('auth/register', { json: { email, password } }).json<RegisterResponse>();
  },

  login: async (email: string, password: string): Promise<TokenResponse> => {
    return apiClient.post('auth/login', { json: { email, password } }).json<TokenResponse>();
  },

  verifyEmail: async (payload: { token?: string; email?: string; code?: string }): Promise<TokenResponse> => {
    return apiClient.post('auth/verify-email', { json: payload }).json<TokenResponse>();
  },

  resendVerification: async (email: string): Promise<{ detail: string }> => {
    return apiClient.post('auth/resend-verification', { json: { email } }).json<{ detail: string }>();
  },

  logout: async (): Promise<void> => {
    await apiClient.post('auth/logout');
  },
};
