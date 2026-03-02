'use client';

import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { exercisesApi } from '@/lib/api/exercises';
import type { Exercise, ExerciseListItem, MuscleGroup, Equipment } from '@/lib/api/exercises';

export function useExercises(filters: Record<string, string> = {}) {
  return useQuery<ExerciseListItem[]>({
    queryKey: queryKeys.exercises.list(filters),
    queryFn: () => exercisesApi.getList(filters),
  });
}

export function useExercise(id: string | undefined) {
  return useQuery<Exercise>({
    queryKey: queryKeys.exercises.detail(id!),
    queryFn: () => exercisesApi.getDetail(id!),
    enabled: !!id,
  });
}

export function useMuscleGroups() {
  return useQuery<MuscleGroup[]>({
    queryKey: [...queryKeys.exercises.all, 'muscle-groups'],
    queryFn: exercisesApi.getMuscleGroups,
    staleTime: 30 * 60 * 1000, // 30 minutes — rarely changes
  });
}

export function useEquipment() {
  return useQuery<Equipment[]>({
    queryKey: [...queryKeys.exercises.all, 'equipment'],
    queryFn: exercisesApi.getEquipment,
    staleTime: 30 * 60 * 1000,
  });
}
