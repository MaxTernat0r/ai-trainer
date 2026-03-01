export const queryKeys = {
  auth: {
    all: ['auth'] as const,
    profile: () => [...queryKeys.auth.all, 'profile'] as const,
  },
  workouts: {
    all: ['workouts'] as const,
    plans: () => [...queryKeys.workouts.all, 'plans'] as const,
    plan: (id: string) => [...queryKeys.workouts.all, 'plan', id] as const,
  },
  nutrition: {
    all: ['nutrition'] as const,
    plans: () => [...queryKeys.nutrition.all, 'plans'] as const,
    daily: (date: string) => [...queryKeys.nutrition.all, 'daily', date] as const,
  },
  exercises: {
    all: ['exercises'] as const,
    list: (filters: Record<string, string>) => [...queryKeys.exercises.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.exercises.all, 'detail', id] as const,
  },
  analytics: {
    all: ['analytics'] as const,
    dashboard: () => [...queryKeys.analytics.all, 'dashboard'] as const,
  },
  chat: {
    all: ['chat'] as const,
    conversations: () => [...queryKeys.chat.all, 'conversations'] as const,
    conversation: (id: string) => [...queryKeys.chat.all, 'conversation', id] as const,
  },
} as const;
