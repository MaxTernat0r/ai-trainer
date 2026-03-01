'use client';

import { useState, useCallback } from 'react';
import { useAuthStore } from '@/lib/stores/auth-store';
import { authApi } from '@/lib/api/auth';
import { useQueryClient } from '@tanstack/react-query';
import type { UserBrief } from '@/types/user';

interface UseAuthReturn {
  user: UserBrief | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

export function useAuth(): UseAuthReturn {
  const { user, isAuthenticated, setAuth, clearAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const queryClient = useQueryClient();

  const login = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      try {
        const response = await authApi.login(email, password);
        setAuth(response.access_token, response.user);
      } finally {
        setIsLoading(false);
      }
    },
    [setAuth]
  );

  const register = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      try {
        const response = await authApi.register(email, password);
        setAuth(response.access_token, response.user);
      } finally {
        setIsLoading(false);
      }
    },
    [setAuth]
  );

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await authApi.logout();
    } catch {
      // Proceed with client-side logout even if API call fails
    } finally {
      clearAuth();
      queryClient.clear();
      setIsLoading(false);
    }
  }, [clearAuth, queryClient]);

  return { user, isAuthenticated, isLoading, login, register, logout };
}
