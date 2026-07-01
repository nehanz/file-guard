from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings configured via environment variables.
    """
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "File Guard API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE"
    CORS_ORIGINS: List[str] = ["*"]
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    DATABASE_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "file_guard"
    
    LOG_LEVEL: str = "DEBUG"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
