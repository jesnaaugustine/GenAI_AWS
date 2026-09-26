from langchain_openai import ChatOpenAI
import logging

from app.core.config import Settings
logger = logging.getLogger(__name__)

class LLMClientException(Exception):
    """Raised when the LLM provider cannot process a request."""


class OpenAIClient:
    def __init__(self,  settings:Settings):
        self.model = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key.get_secret_value(),
            temperature=0,
            max_retries=2,
            timeout=30,
        )

    async def generate(self, message: str) -> str:
        logger.info("Sending request to OpenAI")
        try:
            response = await self.model.ainvoke(message)
            return response.content
        except Exception as e:
            logger.exception("OpenAI request failed")

            raise LLMClientException(
                "LLM provider request failed"
            ) from None