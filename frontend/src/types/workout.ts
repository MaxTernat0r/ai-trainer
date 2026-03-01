export interface WorkoutPlan {
  id: string;
  title: string;
  description: string | null;
  goal: string;
  difficulty: string;
  duration_weeks: number;
  days_per_week: number;
  is_ai_generated: boolean;
  is_active: boolean;
  sessions: WorkoutSession[];
}

export interface WorkoutSession {
  id: string;
  day_number: number;
  name: string;
  notes: string | null;
  order_index: number;
  exercises: WorkoutExercise[];
}

export interface WorkoutExercise {
  id: string;
  exercise_id: string;
  exercise_name: string | null;
  exercise_name_ru: string | null;
  order_index: number;
  target_sets: number;
  target_reps: string;
  target_rest_seconds: number | null;
  notes: string | null;
  logged_sets: ExerciseSet[];
}

export interface ExerciseSet {
  id: string;
  set_number: number;
  reps_completed: number | null;
  weight_kg: number | null;
  duration_seconds: number | null;
  is_warmup: boolean;
  completed_at: string;
}

export interface WorkoutPlanBrief {
  id: string;
  title: string;
  goal: string;
  difficulty: string;
  duration_weeks: number;
  days_per_week: number;
  is_ai_generated: boolean;
  is_active: boolean;
}
