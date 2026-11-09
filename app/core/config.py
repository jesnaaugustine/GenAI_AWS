import os
from pathlib import Path
from turtle import st
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

    cognito_user_pool_id: str
    cognito_client_id: str

    db_username:str = Field(default="genai_app", description="Database username")
    db_password:str = Field(description="Database password")
    db_host:str = Field(default="genai-postgres.c0twiocwwhdi.us-east-1.rds.amazonaws.com", description="Database host")
    db_port:int = Field(default=5432, description="Database port")
    db_name:str = Field(default="genai_db", description="Database name")

   # database_url: str = Field(default="sqlite+aiosqlite:///./genai.db", description="RDS URL")
    echo_sql: bool = Field(default=False, description="Enable SQL query logging")
    pool_size: int = Field(default=10, description="Database connection pool size")
    max_overflow: int = Field(default=5, description="Maximum pool overflow")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
