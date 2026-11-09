import logging
from unittest import result
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message, MessageRole
from app.db.models import utc_now
from app.core.exceptions import AppException
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class ConversationRepository:
    """Database operations for conversations and messages."""
    def __init__(self, db: AsyncSession):
        self.db = db

    
    async def get_conversation(self,conversation_id: UUID, user_id: UUID) -> Conversation | None:
        """Get a conversation owned by the specified user."""

        try:
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            conversation = await self.db.scalar(statement)

            logger.debug(
                "Conversation lookup: conversation_id=%s user_id=%s found=%s",
                conversation_id,
                user_id,
                conversation is not None,
            )

            return conversation

        except SQLAlchemyError as exc:
            logger.exception(
                "Failed to retrieve conversation: "
                "conversation_id=%s user_id=%s",
                conversation_id,
                user_id,
            )

            raise AppException(
                code="CONVERSATION_FETCH_FAILED",
                message="Unable to retrieve conversation",
                status_code=500,
            ) from exc

        
    async def create_conversation( self,user_id: UUID,title: str | None = None,) -> Conversation:
        """Create a new conversation."""

        try:
            conversation = Conversation(user_id=user_id,title=title)
            self.db.add(conversation)
            await self.db.flush()

            logger.info(
                "Conversation created | conversation_id=%s | user_id=%s",
                conversation.id,
                user_id,
            )
            return conversation

        except SQLAlchemyError as exc:
            logger.exception(
                "Failed to create conversation | user_id=%s",
                user_id)
            raise AppException(
                code="CONVERSATION_CREATE_FAILED",
                message="Unable to create conversation",
                status_code=500,
            ) from exc

    async def list_conversations(self,user_id: UUID,limit: int = 20,offset: int = 0) -> list[Conversation]:
        try:
            statement = (
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )

            result = await self.db.scalars(statement)
            conversations = list(result.all())

            logger.debug("Retrieved %d conversations for user_id=%s",len(conversations), user_id)

            return conversations

        except SQLAlchemyError as exc:
            logger.exception(
                "Failed to list conversations for user_id=%s",
                user_id,
            )

            raise AppException(
                code="CONVERSATION_LIST_FAILED",
                message="Unable to retrieve conversations",
                status_code=500,
            ) from exc

    
    async def add_message(self,conversation_id: UUID,role: MessageRole,content: str) -> Message:
        """Add a message to a conversation."""

        try:
            message = Message(conversation_id=conversation_id,role=role.value,content=content)

            self.db.add(message)
            await self.db.flush()

            logger.info(
                "Message created: message_id=%s conversation_id=%s role=%s",
                message.id,
                conversation_id,
                role,
            )

            return message

        except SQLAlchemyError as exc:
            logger.exception(
                "Failed to add message: conversation_id=%s role=%s",
                conversation_id,
                role,
            )

            raise AppException(
                code="MESSAGE_CREATE_FAILED",
                message="Unable to save message",
                status_code=500,
            ) from exc

    async def get_messages(self,conversation_id: UUID,limit:int=50,before_id: UUID | None = None) -> list[Message]:
        """Get all messages for a conversation."""

        try:
            statement = (select(Message).where(Message.conversation_id == conversation_id))
            if before_id is not None:
                cursor_message = await self.db.scalar(
                    select(Message).where(
                        Message.id == before_id,
                        Message.conversation_id == conversation_id,
                    )
                )

                if cursor_message is None:
                    return []

                statement = statement.where(
                    Message.created_at < cursor_message.created_at,
                )

            statement = (statement.order_by(Message.created_at.desc(), Message.id.desc()).limit(limit))

            result = await self.db.scalars(statement)
            messages = list(result.all())

            # Return the selected page in chronological order.
            messages.reverse()
            return messages

        except SQLAlchemyError as exc:
            logger.exception(
                "Failed to retrieve messages: conversation_id=%s",
                conversation_id,
            )

            raise AppException(
                code="MESSAGE_FETCH_FAILED",
                message="Unable to retrieve conversation messages",
                status_code=500,
            ) from exc

