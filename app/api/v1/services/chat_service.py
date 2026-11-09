import logging

from app.clients.OpenAI.client import OpenAIClient,LLMClientException
from app.core.exceptions import AppException
from app.api.v1.services.conversation_service import ConversationService
from uuid import UUID
from app.db.models import Message,MessageRole
from app.prompts.chat_prompts import get_prompt, build_chat_prompt

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, openai_client: OpenAIClient,
                 conversation_service: ConversationService):
        self.openai_client = openai_client
        self.conversation_service = conversation_service

    @property
    def model_name(self) -> str:
        return self.openai_client.model.model
    
    async def send_message(self,conversation_id: UUID,user_id: UUID,content: str,) -> Message:
        # 1. Persist the user's message first.
        await self.conversation_service.save_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=content,
        )

        history = await self.conversation_service.get_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=50,
        )
        # 3. Convert ORM messages into role/content tuples.
        messages = [
            (message.role.value if hasattr(message.role, "value")
             else message.role, message.content)
            for message in history
        ]
        # 4. Add the current message to the prompt context.
        messages.append(("user", content))
        prompt_definition = get_prompt("chat_assistant")
        prompt = build_chat_prompt(
            messages=messages,
            prompt=prompt_definition,
        )

        # 2. Generate the assistant response.
        response = await self.chat(prompt)

        # 3. Persist the assistant response.
        assistant_message = await self.conversation_service.save_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=response,
        )

        return assistant_message

    
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

    