import { apiClient } from './client';

export interface MuscleGroup {
  id: string;
  name: string;
  name_ru: string;
  body_area: string;
}

export interface Equipment {
  id: string;
  name: string;
  name_ru: string;
  category: string;
}

export interface ExerciseMuscleGroupEntry {
  muscle_group: MuscleGroup;
  is_primary: boolean;
}

/** Краткая запись упражнения (список) */
export interface ExerciseListItem {
  id: string;
  name: string;
  name_ru: string;
  difficulty: string;
  exercise_type: string;
  equipment: Equipment | null;
  model_3d_key: string | null;
}

/** Полная запись упражнения (детальная) */
export interface Exercise {
  id: string;
  name: string;
  name_ru: string;
  description: string | null;
  description_ru: string | null;
  instructions: string | null;
  instructions_ru: string | null;
  difficulty: string;
  exercise_type: string;
  equipment: Equipment | null;
  model_3d_key: string | null;
  muscle_groups: ExerciseMuscleGroupEntry[];
}

export const exercisesApi = {
  getList: async (filters: Record<string, string> = {}): Promise<ExerciseListItem[]> => {
    const searchParams = new URLSearchParams(filters);
    return apiClient.get('exercises', { searchParams }).json<ExerciseListItem[]>();
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
