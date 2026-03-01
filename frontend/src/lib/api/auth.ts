import { apiClient } from './client';
import type { UserBrief } from '@/types/user';

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserBrief;
}

export const authApi = {
  register: async (email: string, password: string): Promise<TokenResponse> => {
    return apiClient.post('auth/register', { json: { email, password } }).json<TokenResponse>();
  },

  login: async (email: string, password: string): Promise<TokenResponse> => {
    return apiClient.post('auth/login', { json: { email, password } }).json<TokenResponse>();
  },

  logout: async (): Promise<void> => {
    await apiClient.post('auth/logout');
  },
};
