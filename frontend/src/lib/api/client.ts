import ky from 'ky';
import { useAuthStore } from '@/lib/stores/auth-store';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const response = await fetch('/api/auth/refresh', { method: 'POST' });
  if (!response.ok) {
    useAuthStore.getState().clearAuth();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new Error('Session expired');
  }
  const data = await response.json();
  useAuthStore.getState().setAccessToken(data.accessToken);
  return data.accessToken;
}

export const apiClient = ky.create({
  prefixUrl: `${API_BASE_URL}/api/v1`,
  timeout: 30_000,
  retry: { limit: 1, methods: ['get'] },
  hooks: {
    beforeRequest: [
      (request) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
      },
    ],
    afterResponse: [
      async (request, options, response) => {
        if (response.status === 401 && !request.url.includes('/auth/')) {
          if (!refreshPromise) {
            refreshPromise = refreshAccessToken().finally(() => {
              refreshPromise = null;
            });
          }
          try {
            const newToken = await refreshPromise;
            request.headers.set('Authorization', `Bearer ${newToken}`);
            return ky(request, options);
          } catch {
            return response;
          }
        }
      },
    ],
  },
});
