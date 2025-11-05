from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    APP_NAME: str = "Claims Reimbursement System"
    DEBUG: bool = True
    HOST: str = "localhost"
    PORT: int = 8000
    
    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/claims_db"
    DB_POOL_MIN: int = 5
    DB_POOL_MAX: int = 20
    DB_ECHO: bool = False
    
    # Development fallback to SQLite if PostgreSQL unavailable
    USE_SQLITE_FALLBACK: bool = True
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GCS_BUCKET_NAME: str = "claims-documents"
    
    # Vertex AI Configuration
    VERTEX_AI_LOCATION: str = "us-central1"
    
    # OCR Configuration
    OCR_CONFIDENCE_THRESHOLD: float = 0.85
    DOCUMENT_AI_PROCESSOR_ID: Optional[str] = None
    
    # ADK Configuration
    LITELLM_MODEL: str = "gemini/gemini-1.5-pro"
    AGENT_TEMPERATURE: float = 0.1
    AGENT_MAX_TOKENS: int = 4096
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()