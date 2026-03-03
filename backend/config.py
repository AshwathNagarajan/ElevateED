from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
from urllib.parse import quote_plus

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Project info
    PROJECT_NAME: str = "ElevateED API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "FastAPI backend for ElevateED"
    
    # Server config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]
    
    # Database - PostgreSQL
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "dharsini@3031"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "elevated_db"
    
    @property
    def DATABASE_URL(self) -> str:
        # URL-encode the password to handle special characters like @
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # API Keys and secrets
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )

settings = Settings()
