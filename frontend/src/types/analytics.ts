export interface WeightLog {
  id: string;
  weight_kg: number;
  logged_at: string;
}

export interface MeasurementLog {
  id: string;
  measurement_type: string;
  value_cm: number;
  logged_at: string;
}

export interface DashboardData {
  current_weight: number | null;
  weight_change_30d: number | null;
  workouts_this_week: number;
  calories_today: number;
  protein_today: number;
  streak_days: number;
}

export interface ExerciseSummary {
  exercise_id: string;
  exercise_name: string;
  exercise_name_ru: string;
  total_sets: number;
}

export interface SetDetail {
  set_number: number;
  reps_completed: number | null;
  weight_kg: number | null;
  duration_seconds: number | null;
  is_warmup: boolean;
  completed_at: string;
}

export interface SessionSets {
  session_date: string;
  session_name: string;
  workout_exercise_id: string;
  scheduled_workout_id: string | null;
  sets: SetDetail[];
}

export interface BestSetPoint {
  date: string;
  weight_kg: number | null;
  reps_completed: number | null;
  volume: number;
  session_name: string;
}

export interface CompletedExerciseBrief {
  exercise_id: string;
  exercise_name_ru: string;
  workout_exercise_id: string;
  sets_count: number;
}

export interface CompletedSession {
  entry_id: string;
  session_name: string;
  scheduled_date: string;
  exercises: CompletedExerciseBrief[];
}
