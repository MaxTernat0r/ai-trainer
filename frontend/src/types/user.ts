export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  avatar_url: string | null;
}

export interface UserBrief {
  id: string;
  email: string;
  is_verified: boolean;
  avatar_url: string | null;
}

export interface Profile {
  id: string;
  first_name: string | null;
  last_name: string | null;
  date_of_birth: string | null;
  gender: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  experience_level: string;
  goal: string | null;
  sport_type: string | null;
  activity_level: string | null;
  target_weight_kg: number | null;
  equipment_available: string | null;
  training_days_per_week: number | null;
  meals_per_day: number | null;
  food_allergies: string | null;
  disliked_foods: string | null;
  custom_health_notes: string | null;
  medical_restrictions: MedicalRestriction[];
}

export interface MedicalRestriction {
  id: string;
  name: string;
  description: string | null;
}

export interface OnboardingData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  height_cm: number;
  weight_kg: number;
  experience_level: string;
  goal: string;
  sport_type: string;
  activity_level: string;
  target_weight_kg: number | null;
  equipment_available: string;
  training_days_per_week: number;
  meals_per_day: number;
  food_allergies: string;
  disliked_foods: string;
  custom_health_notes: string;
  medical_restriction_ids: string[];
}
