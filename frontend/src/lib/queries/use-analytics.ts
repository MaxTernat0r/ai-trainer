'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { analyticsApi } from '@/lib/api/analytics';
import type { LogWeightRequest, LogMeasurementRequest } from '@/lib/api/analytics';
import type {
  DashboardData,
  WeightLog,
  MeasurementLog,
  ExerciseSummary,
  BestSetPoint,
  SessionSets,
  CompletedSession,
} from '@/types/analytics';

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

export function useTrainedExercises() {
  return useQuery<ExerciseSummary[]>({
    queryKey: [...queryKeys.analytics.all, 'trained-exercises'],
    queryFn: analyticsApi.getTrainedExercises,
  });
}

export function useExerciseProgress(exerciseId: string | null) {
  return useQuery<BestSetPoint[]>({
    queryKey: [...queryKeys.analytics.all, 'exercise-progress', exerciseId],
    queryFn: () => analyticsApi.getExerciseProgress(exerciseId!),
    enabled: !!exerciseId,
  });
}

export function useExerciseSessions(exerciseId: string | null) {
  return useQuery<SessionSets[]>({
    queryKey: [...queryKeys.analytics.all, 'exercise-sessions', exerciseId],
    queryFn: () => analyticsApi.getExerciseSessions(exerciseId!),
    enabled: !!exerciseId,
  });
}

export function useCompletedSessions() {
  return useQuery<CompletedSession[]>({
    queryKey: [...queryKeys.analytics.all, 'completed-sessions'],
    queryFn: analyticsApi.getCompletedSessions,
  });
}
