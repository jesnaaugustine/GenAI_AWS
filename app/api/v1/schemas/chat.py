from pydantic import BaseModel, ConfigDict, Field,field_validator
from uuid import UUID
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message",
    )


class ChatResponse(BaseModel):
    response: str
    model: str


class ConversationCreateRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError("Title cannot be empty or whitespace only")

        return value


class ConversationResponse(BaseModel):
    id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MessageCreateRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=10000,
        description="The user's message",
    )

    @field_validator("content", mode="before")
    @classmethod
    def trim_content(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Message cannot be empty or whitespace only")
        return value