from fastapi import Request,Depends
from typing import Annotated
from app.core.config import Settings, get_settings
from app.clients.OpenAI.client import OpenAIClient

def get_app_settings() -> Settings:
    return get_settings()

def get_request_settings(request:Request) -> Settings:
    return request.app.state.settings

def get_openai_client(request:Request) -> OpenAIClient:
    return request.app.state.openai_client

#dependency annotation

OpenaiDep = Annotated[OpenAIClient, Depends(get_openai_client)]