"""Food photo recognition using OpenAI Vision API.

Takes image bytes, encodes them to base64, sends to OpenAI's vision model
for food identification, and parses the structured JSON response into
a FoodRecognitionResult schema.
"""

import base64
import json
import logging

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.schemas.nutrition import FoodRecognitionResult, RecognizedFoodItem
from app.services.ai.openai_client import get_openai_client

logger = logging.getLogger(__name__)

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


async def recognize_food_from_photo(image_data: bytes) -> FoodRecognitionResult:
    """Recognize food items from a photo using OpenAI Vision API.

    Args:
        image_data: Raw image bytes (JPEG, PNG, or WebP).

    Returns:
        FoodRecognitionResult with identified food items and nutritional info.

    Raises:
        AIServiceError: If the API call fails or the response cannot be parsed.
    """
    try:
        # Base64-encode the image
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        # Detect a reasonable MIME type from the image header bytes
        mime_type = _detect_mime_type(image_data)

        # Build the vision API request
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": FOOD_RECOGNITION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1024,
            temperature=0.3,
        )

        raw_content = response.choices[0].message.content
        if not raw_content:
            raise AIServiceError("AI returned an empty response for food recognition")

        # Parse the JSON response
        try:
            result_data = json.loads(raw_content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI food recognition response: %s", e)
            raise AIServiceError(
                "Failed to parse AI response for food recognition"
            )

        # Build the result schema
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

    except AIServiceError:
        raise
    except Exception as e:
        logger.exception("Unexpected error during food recognition")
        raise AIServiceError(f"Failed to recognize food from photo: {e}") from e


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
