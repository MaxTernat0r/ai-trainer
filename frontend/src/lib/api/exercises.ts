import { apiClient } from './client';

export interface Exercise {
  id: string;
  name: string;
  name_ru: string | null;
  description: string | null;
  muscle_group: string;
  secondary_muscles: string[];
  equipment: string | null;
  difficulty: string;
  instructions: string | null;
  video_url: string | null;
  image_url: string | null;
}

export interface MuscleGroup {
  id: string;
  name: string;
  name_ru: string | null;
}

export interface Equipment {
  id: string;
  name: string;
  name_ru: string | null;
}

export const exercisesApi = {
  getList: async (filters: Record<string, string> = {}): Promise<Exercise[]> => {
    const searchParams = new URLSearchParams(filters);
    return apiClient.get('exercises', { searchParams }).json<Exercise[]>();
  },

  getDetail: async (id: string): Promise<Exercise> => {
    return apiClient.get(`exercises/${id}`).json<Exercise>();
  },

  getMuscleGroups: async (): Promise<MuscleGroup[]> => {
    return apiClient.get('exercises/muscle-groups').json<MuscleGroup[]>();
  },

  getEquipment: async (): Promise<Equipment[]> => {
    return apiClient.get('exercises/equipment').json<Equipment[]>();
  },
};
