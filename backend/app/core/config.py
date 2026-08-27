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

    # API Endpoint Configuration
    AUTH_ENDPOINT: str = "/auth"
    USERS_ENDPOINT: str = "/users"
    FILES_ENDPOINT: str = "/files"
    HEALTH_ENDPOINT: str = "/health"

    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE"
    CORS_ORIGINS: List[str] = ["*"]
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg", ".docx", ".txt", ".csv"]
    UPLOAD_DIR: str = "uploads"
    
    DATABASE_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "file_guard"

    # Blockchain settings
    WEB3_PROVIDER_URI: str = "http://127.0.0.1:8545"
    ETH_PRIVATE_KEY: str = ""  # Anvil default account private key
    CONTRACT_ADDRESS: str = ""  # Deployed FileIntegrity contract address

    LOG_LEVEL: str = "DEBUG"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
