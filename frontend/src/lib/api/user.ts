import { apiClient } from './client';
import type { Profile, OnboardingData } from '@/types/user';

export const userApi = {
  getProfile: async (): Promise<Profile> => {
    return apiClient.get('profiles/me').json<Profile>();
  },

  updateProfile: async (data: Partial<OnboardingData>): Promise<Profile> => {
    return apiClient.put('profiles/me', { json: data }).json<Profile>();
  },
};
