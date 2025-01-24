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
    BATCH_SIZE: int = 2
    TOTAL_ITEMS: Optional[int] = None  # None means process all items
    OUTPUT_FILE: str = "model_comparison_results.json"
    
    # New Robustness Testing Settings
    TEST_LANGUAGES: list[str] = ["en", "es", "fr", "de"]  # Default languages to test
    MISSPELLING_SEVERITY: str = "medium"  # light, medium, severe
    MALFORMED_TYPES: list[str] = ["extra_spaces", "no_spaces", "random_case", "punctuation_errors"]
    EDGE_CASE_TYPES: list[str] = ["empty", "very_long", "special_chars", "numeric_only"]
    
    # Output settings for different test types
    MISSPELLING_OUTPUT: str = "misspelling_results.json"
    MALFORMED_OUTPUT: str = "malformed_results.json"
    LANGUAGE_OUTPUT: str = "language_results.json"
    EDGE_CASE_OUTPUT: str = "edge_case_results.json"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow any extra environment variables
        case_sensitive = False  # Be flexible with casing

# Create global settings instance
settings = Settings() 