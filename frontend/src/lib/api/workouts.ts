import { apiClient } from './client';
import type { WorkoutPlan, WorkoutPlanBrief, ExerciseSet } from '@/types/workout';

export interface GenerateWorkoutRequest {
  goal?: string;
  days_per_week?: number;
  duration_weeks?: number;
  difficulty?: string;
  equipment?: string;
}

export interface LogSetRequest {
  workout_exercise_id: string;
  set_number: number;
  reps_completed: number | null;
  weight_kg: number | null;
  duration_seconds: number | null;
  is_warmup?: boolean;
}

export const workoutsApi = {
  getPlans: async (): Promise<WorkoutPlanBrief[]> => {
    return apiClient.get('workouts/plans').json<WorkoutPlanBrief[]>();
  },

  getPlan: async (id: string): Promise<WorkoutPlan> => {
    return apiClient.get(`workouts/plans/${id}`).json<WorkoutPlan>();
  },

  generate: async (data: GenerateWorkoutRequest): Promise<WorkoutPlan> => {
    return apiClient.post('workouts/generate', { json: data }).json<WorkoutPlan>();
  },

  deletePlan: async (id: string): Promise<void> => {
    await apiClient.delete(`workouts/plans/${id}`);
  },

  activatePlan: async (id: string): Promise<WorkoutPlan> => {
    return apiClient.post(`workouts/plans/${id}/activate`).json<WorkoutPlan>();
  },

  logSet: async (data: LogSetRequest): Promise<ExerciseSet> => {
    return apiClient.post('workouts/sets', { json: data }).json<ExerciseSet>();
  },
};
