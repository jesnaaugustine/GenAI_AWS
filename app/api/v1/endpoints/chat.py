from fastapi import APIRouter
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0,str(PROJECT_ROOT))

from app.api.v1.schemas.chat import ChatRequest, ChatResponse
from app.dependencies import OpenaiDep ,chatserviceDep
from app.api.v1.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest,ChatService:chatserviceDep) -> ChatResponse:
    response = await ChatService.chat(request.message)
    return ChatResponse(response=response,model=ChatService.model_name)