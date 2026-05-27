"""Food photo recognition using the configured AI vision provider.

Takes image bytes, encodes them to base64, sends them to the configured
vision-capable model, and parses the structured JSON response into a
FoodRecognitionResult schema.
"""

import base64
import json
import logging
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.core.exceptions import AIServiceError, BadRequestError
from app.schemas.nutrition import FoodRecognitionResult, RecognizedFoodItem
from app.services.ai.provider import generate_vision_json, get_configured_ai_provider

logger = logging.getLogger(__name__)

MAX_RECOGNIZE_BYTES = 6 * 1024 * 1024
ALLOWED_RECOGNIZE_FORMATS = {"JPEG", "PNG", "WEBP"}

FOOD_RECOGNITION_PROMPT = """\
Проанализируй это изображение и определи, есть ли на нём еда.

Если на изображении НЕТ еды, верни:
{"is_food": false, "items": [], "total_calories": 0, "total_protein_g": 0, "total_fat_g": 0, "total_carbs_g": 0}

Если на изображении ЕСТЬ еда, определи каждый продукт/блюдо и оцени:
- Название продукта (на русском)
- Уверенность в распознавании (0.0 - 1.0)
- Примерный размер порции в граммах
- Калории для этой порции
- Белки, жиры, углеводы для этой порции

Отвечай ТОЛЬКО валидным JSON следующей структуры:
{
  "is_food": true,
  "items": [
    {
      "food_name": "Название блюда/продукта",
      "confidence_score": 0.85,
      "portion_grams": 200,
      "calories": 350,
      "protein_g": 25,
      "fat_g": 15,
      "carbs_g": 30
    }
  ],
  "total_calories": 350,
  "total_protein_g": 25,
  "total_fat_g": 15,
  "total_carbs_g": 30
}

Не добавляй никакого текста вне JSON. Только чистый JSON.
Будь реалистичен в оценке размеров порций и питательной ценности.
"""


def _build_fallback_food_recognition_result() -> FoodRecognitionResult:
    fallback_item = RecognizedFoodItem(
        food_name="Продукт с фото (уточните вручную)",
        confidence_score=0.25,
        portion_grams=100,
        calories=150,
        protein_g=8,
        fat_g=5,
        carbs_g=18,
    )
    return FoodRecognitionResult(
        is_food=True,
        items=[fallback_item],
        total_calories=fallback_item.calories,
        total_protein_g=fallback_item.protein_g,
        total_fat_g=fallback_item.fat_g,
        total_carbs_g=fallback_item.carbs_g,
    )


async def recognize_food_from_photo(image_data: bytes) -> FoodRecognitionResult:
    """Recognize food items from a photo using the configured vision provider.

    Args:
        image_data: Raw image bytes (JPEG, PNG, or WebP).

    Returns:
        FoodRecognitionResult with identified food items and nutritional info.

    Raises:
        BadRequestError: If the upload is not a valid image or exceeds the
            size limit.
        AIServiceError: If the vision provider is not configured or fails.
    """
    if not image_data:
        raise BadRequestError("Empty image upload")
    if len(image_data) > MAX_RECOGNIZE_BYTES:
        raise BadRequestError(
            f"Image too large (max {MAX_RECOGNIZE_BYTES // (1024 * 1024)} MB)"
        )

    try:
        with Image.open(BytesIO(image_data)) as img:
            img.verify()
        with Image.open(BytesIO(image_data)) as img:
            pil_format = (img.format or "").upper()
    except Image.DecompressionBombError as exc:
        raise BadRequestError("Image dimensions are too large") from exc
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise BadRequestError("Uploaded file is not a valid image") from exc

    if pil_format not in ALLOWED_RECOGNIZE_FORMATS:
        raise BadRequestError(
            f"Unsupported image format: {pil_format or 'unknown'}"
        )

    if not get_configured_ai_provider():
        raise AIServiceError("AI provider is not configured for vision")

    image_base64 = base64.b64encode(image_data).decode("utf-8")
    mime_type = _detect_mime_type(image_data)

    raw_content = await generate_vision_json(
        FOOD_RECOGNITION_PROMPT,
        image_base64,
        mime_type,
        max_tokens=1024,
        temperature=0.3,
    )

    try:
        result_data = json.loads(raw_content)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse AI food recognition response: %s", exc)
        raise AIServiceError("Failed to parse AI response for food recognition") from exc

    items = [
        RecognizedFoodItem(
            food_name=item.get("food_name", "Unknown"),
            confidence_score=min(1.0, max(0.0, item.get("confidence_score", 0.5))),
            portion_grams=item.get("portion_grams", 100),
            calories=item.get("calories", 0),
            protein_g=item.get("protein_g", 0),
            fat_g=item.get("fat_g", 0),
            carbs_g=item.get("carbs_g", 0),
        )
        for item in result_data.get("items", [])
    ]

    return FoodRecognitionResult(
        is_food=result_data.get("is_food", False),
        items=items,
        total_calories=result_data.get("total_calories", 0),
        total_protein_g=result_data.get("total_protein_g", 0),
        total_fat_g=result_data.get("total_fat_g", 0),
        total_carbs_g=result_data.get("total_carbs_g", 0),
    )


def _detect_mime_type(image_data: bytes) -> str:
    """Detect image MIME type from magic bytes.

    Falls back to image/jpeg if the format cannot be determined.
    """
    if image_data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_data[:4] == b"RIFF" and image_data[8:12] == b"WEBP":
        return "image/webp"
    # JPEG starts with FF D8 FF
    if image_data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    # Default to JPEG
    return "image/jpeg"
