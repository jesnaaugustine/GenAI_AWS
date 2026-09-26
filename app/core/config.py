import os
from pathlib import Path
from typing import List, Literal, Optional
from functools import lru_cache

from pydantic import Field, field_validator,SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", str(ENV_FILE_PATH)],
        extra="ignore",
        frozen=True,
        env_nested_delimiter="__",
        case_sensitive=False,
    )
    app_name: str = Field(default="GenAI Chat API")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")

    aws_region: str = Field(default="us-east-1")
    bedrock_model_id: str = Field(default="qwen.qwen3-32b-v1:0")

    log_level: str = Field(default="INFO")

    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_model: str = Field(default="gpt-5.6-luna")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
