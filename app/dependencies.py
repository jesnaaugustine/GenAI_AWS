from fastapi import Request,Depends
from typing import Annotated
from app.core.config import Settings, get_settings
from app.clients.OpenAI.client import OpenAIClient
from app.api.v1.services.chat_service import ChatService
from app.db.interfaces.database import BaseDatabase
from sqlalchemy.orm import Session
from app.api.v1.services.user_service import UserService
from app.api.v1.services.conversation_service import ConversationService
from sqlalchemy.ext.asyncio import AsyncSession

def get_app_settings() -> Settings:
    return get_settings()

def get_request_settings(request:Request) -> Settings:
    return request.app.state.settings

def get_openai_client(request:Request) -> OpenAIClient:
    return request.app.state.openai_client



def get_database(request: Request) -> BaseDatabase:
    return request.app.state.database

async def get_db_session(database: Annotated[BaseDatabase, Depends(get_database)]):
    async with database.get_session() as session:
        yield session
   

def get_conversation_service( db: Annotated[AsyncSession, Depends(get_db_session)]) -> ConversationService:
    return ConversationService(db)

def get_user_service( db: Annotated[AsyncSession, Depends(get_db_session)]) -> UserService:
    return UserService(db)

def get_chat_service(openai_clinet:Annotated[OpenAIClient, Depends(get_openai_client)],
                     ConversationServiceDep: Annotated[ConversationService, Depends(get_conversation_service)]) -> ChatService:
    return ChatService(openai_client=openai_clinet,conversation_service=ConversationServiceDep)

    

OpenaiDep = Annotated[OpenAIClient, Depends(get_openai_client)]
chatserviceDep= Annotated[ChatService, Depends(get_chat_service)]
DatabaseDep = Annotated[BaseDatabase, Depends(get_database)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]