'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { workoutsApi } from '@/lib/api/workouts';
import type { GenerateWorkoutRequest, LogSetRequest, AddScheduleEntryRequest } from '@/lib/api/workouts';
import type { WorkoutPlan, WorkoutPlanBrief, ExerciseSet, CalendarEntry } from '@/types/workout';

export function useWorkoutPlans() {
  return useQuery<WorkoutPlanBrief[]>({
    queryKey: queryKeys.workouts.plans(),
    queryFn: workoutsApi.getPlans,
  });
}

export function useWorkoutPlan(id: string | undefined, entryId?: string) {
  return useQuery<WorkoutPlan>({
    queryKey: [...queryKeys.workouts.plan(id!), entryId ?? 'all'],
    queryFn: () => workoutsApi.getPlan(id!, entryId),
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

  return useMutation<void, Error, string>({
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

export function useWorkoutCalendar(year: number, month: number) {
  return useQuery<CalendarEntry[]>({
    queryKey: [...queryKeys.workouts.all, 'calendar', year, month],
    queryFn: () => workoutsApi.getCalendar(year, month),
  });
}

export function useRescheduleEntry() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, { entryId: string; scheduledDate: string }>({
    mutationFn: ({ entryId, scheduledDate }) =>
      workoutsApi.rescheduleEntry(entryId, scheduledDate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.all });
    },
  });
}

export function useAutoSchedulePlan() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (planId) => workoutsApi.autoSchedulePlan(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.all });
    },
  });
}

export function useToggleComplete() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (entryId) => workoutsApi.toggleComplete(entryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.all });
    },
  });
}

export function useAddScheduleEntry() {
  const queryClient = useQueryClient();

  return useMutation<CalendarEntry, Error, AddScheduleEntryRequest>({
    mutationFn: (data) => workoutsApi.addScheduleEntry(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.all });
    },
  });
}

export function useStartWorkout() {
  const queryClient = useQueryClient();

  return useMutation<CalendarEntry, Error, AddScheduleEntryRequest>({
    mutationFn: (data) => workoutsApi.startWorkout(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.all });
    },
  });
}

export function useDeleteScheduleEntry() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (entryId) => workoutsApi.deleteScheduleEntry(entryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workouts.all });
    },
  });
}
