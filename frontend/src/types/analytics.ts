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
