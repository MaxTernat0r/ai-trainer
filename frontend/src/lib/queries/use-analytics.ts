'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { analyticsApi } from '@/lib/api/analytics';
import type { LogWeightRequest, LogMeasurementRequest } from '@/lib/api/analytics';
import type { DashboardData, WeightLog, MeasurementLog } from '@/types/analytics';

export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: queryKeys.analytics.dashboard(),
    queryFn: analyticsApi.getDashboard,
  });
}

export function useWeightLogs() {
  return useQuery<WeightLog[]>({
    queryKey: [...queryKeys.analytics.all, 'weight'],
    queryFn: analyticsApi.getWeightLogs,
  });
}

export function useLogWeight() {
  const queryClient = useQueryClient();

  return useMutation<WeightLog, Error, LogWeightRequest>({
    mutationFn: (data) => analyticsApi.logWeight(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.analytics.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.analytics.dashboard() });
    },
  });
}

export function useMeasurements(type?: string) {
  return useQuery<MeasurementLog[]>({
    queryKey: [...queryKeys.analytics.all, 'measurements', type],
    queryFn: () => analyticsApi.getMeasurements(type),
  });
}

export function useLogMeasurement() {
  const queryClient = useQueryClient();

  return useMutation<MeasurementLog, Error, LogMeasurementRequest>({
    mutationFn: (data) => analyticsApi.logMeasurement(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.analytics.all });
    },
  });
}
