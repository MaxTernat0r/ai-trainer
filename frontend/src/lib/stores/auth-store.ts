import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserBrief } from '@/types/user';

interface AuthState {
  accessToken: string | null;
  user: UserBrief | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: UserBrief) => void;
  clearAuth: () => void;
  setAccessToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      isAuthenticated: false,
      setAuth: (accessToken, user) =>
        set({ accessToken, user, isAuthenticated: true }),
      clearAuth: () =>
        set({ accessToken: null, user: null, isAuthenticated: false }),
      setAccessToken: (accessToken) => set({ accessToken }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user }),
    }
  )
);
