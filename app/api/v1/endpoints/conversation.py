import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException,status, Query as fastapi_Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query, Session


from app.dependencies import ConversationServiceDep, SessionDep, UserServiceDep,chatserviceDep
from app.repositories.conversation_repository import ConversationRepository
from app.api.v1.schemas.chat import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageResponse,MessageCreateRequest
)

from app.api.v1.services.conversation_service import ConversationService
from app.auth.dependencies import AuthenticatedPrincipal,principalDep

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: ConversationCreateRequest,
    ConversationServiceDep: ConversationServiceDep,
    principalDep: principalDep,
    UserServiceDep: UserServiceDep
) -> ConversationResponse:
    try:
        user = await UserServiceDep.get_or_create_user(principalDep.cognito_sub)
        conversation = await ConversationServiceDep.create_conversation(
            user_id=user.id,
            title=request.title,
        )
        logger.info(
        "Conversation created successfully: conversation_id=%s user_id=%s",
        conversation.id,
        user.id,
     )

        return ConversationResponse.model_validate(conversation)
    except SQLAlchemyError as e:
        logger.error(
            "Failed to create conversation: user_id=%s error=%s",
            principalDep.cognito_sub,
            str(e),   
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation",
        ) from e 

@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
     ConversationServiceDep: ConversationServiceDep,
        principalDep: principalDep,
        UserServiceDep: UserServiceDep,
        limit: int = fastapi_Query(20, ge=1, le=100),
        offset: int = fastapi_Query(default=0, ge=0),
    ) -> list[ConversationResponse]:

    try:
        user = await UserServiceDep.get_or_create_user(principalDep.cognito_sub)
        conversations = await ConversationServiceDep.list_conversations(
            user_id=user.id,
            limit=limit,
            offset=offset,
        )
        return [ConversationResponse.model_validate(conversation) for conversation in conversations]
    except SQLAlchemyError as e:
        logger.error(
            "Failed to list conversations: user_id=%s error=%s",
            principalDep.cognito_sub,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations",
        ) from e

@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: UUID,
    ConversationServiceDep: ConversationServiceDep,
    principalDep: principalDep,
    UserServiceDep: UserServiceDep,
    limit: int = fastapi_Query(50, ge=1, le=100),
    before_id: UUID | None = fastapi_Query(default=None),
) -> list[MessageResponse]:
    if not 1<= limit <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100",
        )   
    try:
        user = await UserServiceDep.get_or_create_user(principalDep.cognito_sub)
        messages = await ConversationServiceDep.get_messages(
            conversation_id=conversation_id,
            user_id=user.id,
            limit=limit,
            before_id=before_id,
        )
        return [MessageResponse.model_validate(message) for message in messages]
    except SQLAlchemyError as e:
        logger.error(
            "Failed to get messages: user_id=%s error=%s",
            principalDep.cognito_sub,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get messages",
        ) from e

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: UUID,
    request: MessageCreateRequest,
    chatserviceDep: chatserviceDep,
    principalDep: principalDep,
    UserServiceDep: UserServiceDep
) -> MessageResponse:
    try:
        user = await UserServiceDep.get_or_create_user(principalDep.cognito_sub)
        assistant_message = await chatserviceDep.send_message(
            conversation_id=conversation_id,
            user_id=user.id,
            content=MessageCreateRequest.model_validate(request).content,
        )
        return MessageResponse.model_validate(assistant_message)
    except SQLAlchemyError as e:
        logger.error(
            "Failed to send message: user_id=%s error=%s",
            principalDep.cognito_sub,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        ) from e