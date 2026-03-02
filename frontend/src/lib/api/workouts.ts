import { apiClient } from './client';
import type { WorkoutPlan, WorkoutPlanBrief, ExerciseSet, CalendarEntry } from '@/types/workout';

export interface AddScheduleEntryRequest {
  session_id: string;
  scheduled_date: string;
  is_completed?: boolean;
}

export interface GenerateWorkoutRequest {
  weeks?: number;
  days_per_week?: number;
  periodization?: string;
}

export interface LogSetRequest {
  workout_exercise_id: string;
  set_number: number;
  reps_completed: number | null;
  weight_kg: number | null;
  duration_seconds: number | null;
  is_warmup?: boolean;
  scheduled_workout_id?: string;
}

export const workoutsApi = {
  getPlans: async (): Promise<WorkoutPlanBrief[]> => {
    return apiClient.get('workouts/plans').json<WorkoutPlanBrief[]>();
  },

  getPlan: async (id: string, entryId?: string): Promise<WorkoutPlan> => {
    const searchParams: Record<string, string> = {};
    if (entryId) searchParams.entry_id = entryId;
    return apiClient.get(`workouts/plans/${id}`, { searchParams }).json<WorkoutPlan>();
  },

  generate: async (data: GenerateWorkoutRequest): Promise<WorkoutPlan> => {
    return apiClient.post('workouts/generate', { json: data }).json<WorkoutPlan>();
  },

  deletePlan: async (id: string): Promise<void> => {
    await apiClient.delete(`workouts/plans/${id}`);
  },

  activatePlan: async (id: string): Promise<void> => {
    await apiClient.post(`workouts/plans/${id}/activate`);
  },

  logSet: async (data: LogSetRequest): Promise<ExerciseSet> => {
    const { workout_exercise_id, ...body } = data;
    return apiClient
      .post(`workouts/exercises/${workout_exercise_id}/log`, {
        json: body,
      })
      .json<ExerciseSet>();
  },

  startWorkout: async (data: AddScheduleEntryRequest): Promise<CalendarEntry> => {
    return apiClient
      .post('workouts/schedule/start', { json: data })
      .json<CalendarEntry>();
  },

  getCalendar: async (year: number, month: number): Promise<CalendarEntry[]> => {
    return apiClient
      .get('workouts/calendar', { searchParams: { year, month } })
      .json<CalendarEntry[]>();
  },

  rescheduleEntry: async (entryId: string, scheduledDate: string): Promise<void> => {
    await apiClient.patch(`workouts/schedule/${entryId}/reschedule`, {
      json: { scheduled_date: scheduledDate },
    });
  },

  autoSchedulePlan: async (planId: string): Promise<void> => {
    await apiClient.post(`workouts/plans/${planId}/schedule`);
  },

  toggleComplete: async (entryId: string): Promise<void> => {
    await apiClient.patch(`workouts/schedule/${entryId}/complete`);
  },

  addScheduleEntry: async (data: AddScheduleEntryRequest): Promise<CalendarEntry> => {
    return apiClient
      .post('workouts/schedule', { json: data })
      .json<CalendarEntry>();
  },

  deleteScheduleEntry: async (entryId: string): Promise<void> => {
    await apiClient.delete(`workouts/schedule/${entryId}`);
  },
};
