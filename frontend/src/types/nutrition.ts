export interface NutritionPlan {
  id: string;
  title: string;
  daily_calories: number;
  daily_protein_g: number;
  daily_fat_g: number;
  daily_carbs_g: number;
  is_ai_generated: boolean;
  is_active: boolean;
  meals: Meal[];
}

export interface Meal {
  id: string;
  name: string;
  order_index: number;
  target_calories: number | null;
  items: MealItem[];
}

export interface MealItem {
  id: string;
  food_item: FoodItem;
  quantity_g: number;
  notes: string | null;
}

export interface FoodItem {
  id: string;
  name: string;
  name_ru: string;
  brand: string | null;
  calories_per_100g: number;
  protein_per_100g: number;
  fat_per_100g: number;
  carbs_per_100g: number;
  fiber_per_100g: number | null;
  serving_size_g: number | null;
  category: string | null;
}

export interface NutritionLog {
  id: string;
  food_name: string;
  meal_type: string;
  quantity_g: number;
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
  photo_url: string | null;
  logged_at: string;
  notes: string | null;
}

export interface DailySummary {
  date: string;
  total_calories: number;
  total_protein_g: number;
  total_fat_g: number;
  total_carbs_g: number;
  meals_logged: number;
}

export interface FoodRecognitionResult {
  is_food: boolean;
  items: RecognizedFoodItem[];
  total_calories: number;
  total_protein_g: number;
  total_fat_g: number;
  total_carbs_g: number;
}

export interface RecognizedFoodItem {
  food_name: string;
  confidence_score: number;
  portion_grams: number;
  calories: number;
  protein_g: number;
  fat_g: number;
  carbs_g: number;
}
