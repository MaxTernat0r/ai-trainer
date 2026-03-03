import { apiClient } from './client';
import type {
  NutritionPlan,
  FoodItem,
  NutritionLog,
  DailySummary,
  FoodRecognitionResult,
} from '@/types/nutrition';

export interface GenerateNutritionRequest {
  goal?: string;
  daily_calories?: number;
  meals_per_day?: number;
}

export interface LogFoodRequest {
  food_name: string;
  meal_type: string;
  quantity_g: number;
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  photo_url?: string | null;
  notes?: string | null;
  logged_at?: string;
}

export const nutritionApi = {
  getPlans: async (): Promise<NutritionPlan[]> => {
    return apiClient.get('nutrition/plans').json<NutritionPlan[]>();
  },

  getPlan: async (planId: string): Promise<NutritionPlan> => {
    return apiClient.get(`nutrition/plans/${planId}`).json<NutritionPlan>();
  },

  generate: async (data: GenerateNutritionRequest): Promise<NutritionPlan> => {
    return apiClient.post('nutrition/generate', { json: data }).json<NutritionPlan>();
  },

  searchFoods: async (query: string): Promise<FoodItem[]> => {
    return apiClient
      .get('nutrition/foods/search', { searchParams: { q: query } })
      .json<FoodItem[]>();
  },

  logFood: async (data: LogFoodRequest): Promise<NutritionLog> => {
    return apiClient.post('nutrition/logs', { json: data }).json<NutritionLog>();
  },

  getLogs: async (date: string): Promise<NutritionLog[]> => {
    return apiClient
      .get('nutrition/logs', { searchParams: { date } })
      .json<NutritionLog[]>();
  },

  getDailySummary: async (date: string): Promise<DailySummary> => {
    return apiClient
      .get('nutrition/summary', { searchParams: { date } })
      .json<DailySummary>();
  },

  recognizeFood: async (file: File): Promise<FoodRecognitionResult> => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient
      .post('nutrition/recognize', { body: formData })
      .json<FoodRecognitionResult>();
  },
};
