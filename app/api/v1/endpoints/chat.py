from fastapi import APIRouter
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0,str(PROJECT_ROOT))

from app.api.v1.schemas.chat import ChatRequest, ChatResponse
from app.dependencies import OpenaiDep 
from app.api.v1.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest,openai_client:OpenaiDep) -> ChatResponse:
    chat_service = ChatService(openai_client)
    response = await chat_service.chat(request.message)
    return ChatResponse(response=response,model=openai_client.model.model_name)