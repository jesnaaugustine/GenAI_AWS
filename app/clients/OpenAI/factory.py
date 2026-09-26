from functools import lru_cache

from app.core.config import get_settings
from app.clients.OpenAI.client import OpenAIClient


@lru_cache(maxsize=1)
def make_openai_client() -> OpenAIClient:
    settings = get_settings()
    return OpenAIClient(settings)