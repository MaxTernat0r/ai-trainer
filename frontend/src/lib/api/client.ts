import ky from 'ky';
import { useAuthStore } from '@/lib/stores/auth-store';

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

function isLoopbackHost(hostname: string): boolean {
  return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0';
}

function isIpv4Host(hostname: string): boolean {
  return /^\d{1,3}(?:\.\d{1,3}){3}$/.test(hostname);
}

function resolveApiBaseUrl(): string {
  const configuredUrl = process.env.NEXT_PUBLIC_API_URL?.trim() || DEFAULT_API_BASE_URL;

  if (typeof window === 'undefined') {
    return configuredUrl;
  }

  const current = window.location;

  try {
    const apiUrl = new URL(configuredUrl);

    if (isLoopbackHost(apiUrl.hostname) && !isLoopbackHost(current.hostname)) {
      apiUrl.hostname = current.hostname;
      apiUrl.protocol = current.protocol;
      return apiUrl.origin;
    }

    if (isIpv4Host(current.hostname) && !isLoopbackHost(current.hostname)) {
      return current.origin;
    }

    if (current.protocol === 'http:' && apiUrl.protocol === 'https:' && apiUrl.hostname === current.hostname) {
      return current.origin;
    }

    return apiUrl.origin;
  } catch {
    return current.origin;
  }
}

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
  prefixUrl: `${resolveApiBaseUrl()}/api/v1`,
  timeout: 90_000,
  credentials: 'include',
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
