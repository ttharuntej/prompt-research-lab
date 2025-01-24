from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    # Required Settings
    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    
    # Optional Settings with defaults
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    MAX_TOKENS: int = 1000
    BATCH_SIZE: int = 20
    OUTPUT_FILE: str = "failed_comparisons.json"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow any extra environment variables
        case_sensitive = False  # Be flexible with casing

# Create global settings instance
settings = Settings() 