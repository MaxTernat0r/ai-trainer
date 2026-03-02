def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor equation."""
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "lightly_active": 1.375,
    "moderate": 1.55,
    "moderately_active": 1.55,
    "active": 1.725,
    "very_active": 1.725,
    "very_active_extra": 1.9,
    "extra_active": 1.9,
}


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return bmr * multiplier


def calculate_macro_targets(tdee: float, goal: str) -> dict:
    if goal == "fat_loss":
        target_kcal = tdee * 0.80
        protein_pct, fat_pct, carbs_pct = 0.35, 0.25, 0.40
    elif goal == "muscle_gain":
        target_kcal = tdee * 1.10
        protein_pct, fat_pct, carbs_pct = 0.30, 0.25, 0.45
    else:
        target_kcal = tdee
        protein_pct, fat_pct, carbs_pct = 0.30, 0.25, 0.45

    return {
        "tdee": round(tdee),
        "target_kcal": round(target_kcal),
        "protein_g": round((target_kcal * protein_pct) / 4),
        "fat_g": round((target_kcal * fat_pct) / 9),
        "carbs_g": round((target_kcal * carbs_pct) / 4),
    }
