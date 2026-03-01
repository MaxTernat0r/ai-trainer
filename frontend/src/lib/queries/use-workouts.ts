'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { workoutsApi } from '@/lib/api/workouts';
import type { GenerateWorkoutRequest, LogSetRequest } from '@/lib/api/workouts';
import type { WorkoutPlan, WorkoutPlanBrief, ExerciseSet } from '@/types/workout';

export function useWorkoutPlans() {
  return useQuery<WorkoutPlanBrief[]>({
    queryKey: queryKeys.workouts.plans(),
    queryFn: workoutsApi.getPlans,
  });
}

export function useWorkoutPlan(id: string | undefined) {
  return useQuery<WorkoutPlan>({
    queryKey: queryKeys.workouts.plan(id!),
    queryFn: () => workoutsApi.getPlan(id!),
    enabled: !!id,
  });
}

export function useGenerateWorkout() {
  const queryClient = useQueryClient();

  return useMutation<WorkoutPlan, Error, GenerateWorkoutRequest>({
    mutationFn: (data) => workoutsApi.generate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.plans() });
    },
  });
}

export function useDeleteWorkoutPlan() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (id) => workoutsApi.deletePlan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.plans() });
    },
  });
}

export function useActivateWorkoutPlan() {
  const queryClient = useQueryClient();

  return useMutation<WorkoutPlan, Error, string>({
    mutationFn: (id) => workoutsApi.activatePlan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.plans() });
    },
  });
}

export function useLogSet() {
  const queryClient = useQueryClient();

  return useMutation<ExerciseSet, Error, LogSetRequest & { planId: string }>({
    mutationFn: ({ planId: _planId, ...data }) => workoutsApi.logSet(data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.workouts.plan(variables.planId),
      });
    },
  });
}
