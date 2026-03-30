"""
Configuration settings for the Drug Traceability System Backend
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "drug_traceability"
    
    # Blockchain Configuration
    BLOCKCHAIN_PROVIDER_URL: str = "http://127.0.0.1:7545"
    CONTRACT_ADDRESS: str = ""
    PRIVATE_KEY: str = ""
    
    # CORS Configuration
    # In production, this should be locked down. Empty means allow all origins via app.main fallback.
    CORS_ORIGINS: List[str] = []
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()
