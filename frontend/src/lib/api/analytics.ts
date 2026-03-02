import { apiClient } from './client';
import type {
  DashboardData,
  WeightLog,
  MeasurementLog,
  ExerciseSummary,
  BestSetPoint,
  SessionSets,
  CompletedSession,
} from '@/types/analytics';

export interface LogWeightRequest {
  weight_kg: number;
  logged_at?: string;
}

export interface LogMeasurementRequest {
  measurement_type: string;
  value_cm: number;
  logged_at?: string;
}

export const analyticsApi = {
  getDashboard: async (): Promise<DashboardData> => {
    return apiClient.get('analytics/dashboard').json<DashboardData>();
  },

  getWeightLogs: async (): Promise<WeightLog[]> => {
    return apiClient.get('analytics/weight').json<WeightLog[]>();
  },

  logWeight: async (data: LogWeightRequest): Promise<WeightLog> => {
    return apiClient.post('analytics/weight', { json: data }).json<WeightLog>();
  },

  getMeasurements: async (type?: string): Promise<MeasurementLog[]> => {
    const searchParams = type ? { type } : undefined;
    return apiClient
      .get('analytics/measurements', { searchParams })
      .json<MeasurementLog[]>();
  },

  logMeasurement: async (data: LogMeasurementRequest): Promise<MeasurementLog> => {
    return apiClient
      .post('analytics/measurements', { json: data })
      .json<MeasurementLog>();
  },

  getTrainedExercises: async (): Promise<ExerciseSummary[]> => {
    return apiClient.get('analytics/exercises-summary').json<ExerciseSummary[]>();
  },

  getExerciseProgress: async (exerciseId: string): Promise<BestSetPoint[]> => {
    return apiClient
      .get(`analytics/exercise-progress/${exerciseId}`)
      .json<BestSetPoint[]>();
  },

  getExerciseSessions: async (exerciseId: string): Promise<SessionSets[]> => {
    return apiClient
      .get(`analytics/exercise-sessions/${exerciseId}`)
      .json<SessionSets[]>();
  },

  getCompletedSessions: async (): Promise<CompletedSession[]> => {
    return apiClient.get('analytics/completed-sessions').json<CompletedSession[]>();
  },
};
