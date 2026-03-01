'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queries/keys';
import { nutritionApi } from '@/lib/api/nutrition';
import type { GenerateNutritionRequest, LogFoodRequest } from '@/lib/api/nutrition';
import type {
  NutritionPlan,
  FoodItem,
  NutritionLog,
  DailySummary,
  FoodRecognitionResult,
} from '@/types/nutrition';

export function useNutritionPlans() {
  return useQuery<NutritionPlan[]>({
    queryKey: queryKeys.nutrition.plans(),
    queryFn: nutritionApi.getPlans,
  });
}

export function useGenerateNutrition() {
  const queryClient = useQueryClient();

  return useMutation<NutritionPlan, Error, GenerateNutritionRequest>({
    mutationFn: (data) => nutritionApi.generate(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.nutrition.plans() });
    },
  });
}

export function useSearchFoods(query: string) {
  return useQuery<FoodItem[]>({
    queryKey: [...queryKeys.nutrition.all, 'search', query],
    queryFn: () => nutritionApi.searchFoods(query),
    enabled: query.length >= 2,
  });
}

export function useLogFood() {
  const queryClient = useQueryClient();

  return useMutation<NutritionLog, Error, LogFoodRequest & { date: string }>({
    mutationFn: ({ date: _date, ...data }) => nutritionApi.logFood(data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.nutrition.daily(variables.date),
      });
    },
  });
}

export function useNutritionLogs(date: string) {
  return useQuery<NutritionLog[]>({
    queryKey: queryKeys.nutrition.daily(date),
    queryFn: () => nutritionApi.getLogs(date),
    enabled: !!date,
  });
}

export function useDailySummary(date: string) {
  return useQuery<DailySummary>({
    queryKey: [...queryKeys.nutrition.daily(date), 'summary'],
    queryFn: () => nutritionApi.getDailySummary(date),
    enabled: !!date,
  });
}

export function useRecognizeFood() {
  return useMutation<FoodRecognitionResult, Error, File>({
    mutationFn: (file) => nutritionApi.recognizeFood(file),
  });
}
