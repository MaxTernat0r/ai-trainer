'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { userApi } from '@/lib/api/user';
import type { Profile, OnboardingData } from '@/types/user';

export function useProfile() {
  return useQuery<Profile>({
    queryKey: queryKeys.auth.profile(),
    queryFn: userApi.getProfile,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<OnboardingData>) => userApi.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.profile() });
    },
  });
}
