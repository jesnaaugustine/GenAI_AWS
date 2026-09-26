import logging

from app.clients.OpenAI.client import OpenAIClient,LLMClientException
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    async def chat(self, message: str) -> str:
        logger.info("Processing chat request")

        try:
            response = await self.openai_client.generate(message)
            logger.info("Chat request processed successfully")
            return response
        except LLMClientException as e:
            logger.error("Failed to generate chat response")
            raise AppException(
                code="LLM_PROVIDER_UNAVAILABLE",
                message="Unable to process chat request",
                status_code=503,
            ) from e

        logger.info("Chat request processed successfully")

        return response