from fastapi import Request,Depends
from typing import Annotated
from app.core.config import Settings, get_settings
from app.clients.OpenAI.client import OpenAIClient
from app.api.v1.services.chat_service import ChatService

def get_app_settings() -> Settings:
    return get_settings()

def get_request_settings(request:Request) -> Settings:
    return request.app.state.settings

def get_openai_client(request:Request) -> OpenAIClient:
    return request.app.state.openai_client

def get_chat_service(request: Request) -> ChatService:
    openai_client = get_openai_client(request)

    return ChatService(openai_client=openai_client)

#dependency annotation

OpenaiDep = Annotated[OpenAIClient, Depends(get_openai_client)]
chatserviceDep= Annotated[ChatService, Depends(get_chat_service)]