import httpx
from openai import AsyncOpenAI

from app.core.config import settings

_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        http_client = None
        if settings.OPENAI_PROXY_URL:
            http_client = httpx.AsyncClient(proxy=settings.OPENAI_PROXY_URL)
        _client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            http_client=http_client,
        )
    return _client
