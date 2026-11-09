import logging
from uuid import UUID

from sqlalchemy.orm import Session


from app.core.exceptions import AppException
from app.repositories.conversation_repository import ConversationRepository
from app.db.models import Conversation,Message, MessageRole
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self,db: AsyncSession,):
        self.db = db
        self.conversation_repository = ConversationRepository(db=db)

    async def create_conversation(self,user_id: UUID,title: str | None = None,) -> Conversation:
        try:
            conversation = await self.conversation_repository.create_conversation(user_id=user_id,title=title,)
            
            await self.db.commit()

            logger.info(
                "Conversation creation completed: conversation_id=%s",
                conversation.id,
            )

            return conversation

        except Exception:
            await self.db.rollback()
            logger.exception("Conversation creation failed")
            raise

    async def list_conversations(self,user_id: UUID,limit: int = 20,offset: int = 0,) -> list[Conversation]:
        return await self.conversation_repository.list_conversations(user_id=user_id,limit=limit,offset=offset,)

    async def get_conversation(self,conversation_id: UUID,user_id: UUID,) -> Conversation | None:
        return await self.conversation_repository.get_conversation(conversation_id=conversation_id,user_id=user_id)

    async def get_messages(self,conversation_id: UUID,user_id: UUID,limit:int=50,before_id: UUID | None = None) -> list[Message]:
        conversation = await self.conversation_repository.get_conversation(conversation_id=conversation_id,user_id=user_id,)

        if conversation is None:
            raise AppException(
                code="CONVERSATION_NOT_FOUND",
                message="Conversation not found",
                status_code=404,
            )
        return await self.conversation_repository.get_messages(conversation_id=conversation_id,limit=limit,before_id=before_id)       

    async def save_message(self,conversation_id: UUID,user_id: UUID,role: MessageRole,content: str,) -> Message:
        conversation = await self.conversation_repository.get_conversation(conversation_id=conversation_id,user_id=user_id,)

        if conversation is None:
            raise AppException(
                code="CONVERSATION_NOT_FOUND",
                message="Conversation not found",
                status_code=404,
            )

        try:
            message = await self.conversation_repository.add_message(
                conversation_id=conversation_id,
                role=role,
                content=content,
            )

            await self.db.commit()
            await self.db.refresh(message)

            return message

        except SQLAlchemyError as exc:
            await self.db.rollback()
            logger.exception(
                "Failed to save message",
                extra={
                    "conversation_id": str(conversation_id),
                    "user_id": str(user_id),
                },
            )
            raise AppException(
                code="MESSAGE_SAVE_FAILED",
                message="Unable to save message",
                status_code=500,
            ) from exc