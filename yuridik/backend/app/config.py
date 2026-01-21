"""
Imtiyoz-AI Configuration Settings
Manages all environment variables and application configuration.
"""

from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Imtiyoz-AI"
    debug: bool = False
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # LLM Configuration
    llm_provider: Literal["groq", "gemini"] = "groq"
    llm_model: str = "openai/gpt-oss-120b"
    groq_api_key: str = Field(default="", description="Groq API Key")
    google_api_key: str = Field(default="", description="Google API Key for Gemini")
    
    # ChromaDB
    chroma_persist_directory: str = "./data/chroma_db"
    chroma_collection_name: str = "imtiyoz_legal_docs"
    
    # RAG Configuration
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    chunk_size: int = 512
    chunk_overlap: int = 100
    top_k_results: int = 5
    
    # Scout Agent
    scout_search_delay_seconds: float = 2.0
    scout_max_results_per_keyword: int = 10
    scout_date_filter: str = "after:2025-01-01"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def active_api_key(self) -> str:
        """Get the active API key based on provider."""
        if self.llm_provider == "groq":
            return self.groq_api_key
        return self.google_api_key
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
