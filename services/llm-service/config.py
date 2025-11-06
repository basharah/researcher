"""
LLM Service Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Settings
    app_name: str = "LLM Service"
    app_version: str = "1.0.0"
    debug: bool = False
        
    # Service info
    service_name: str = "llm-service"
    
    # API Settings
    api_prefix: str = "/api"
    api_v1_prefix: str = "/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    
    # LLM API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Default LLM Settings
    default_llm_provider: str = "openai"  # "openai" or "anthropic"
    default_model: str = "gpt-4-turbo-preview"  # or "claude-3-opus-20240229"
    max_tokens: int = 4000
    temperature: float = 0.7
    
    # OpenAI Models
    openai_model_gpt4: str = "gpt-4-turbo-preview"
    openai_model_gpt35: str = "gpt-3.5-turbo"
    
    # Anthropic Models
    anthropic_model_opus: str = "claude-3-opus-20240229"
    anthropic_model_sonnet: str = "claude-3-sonnet-20240229"
    anthropic_model_haiku: str = "claude-3-haiku-20240307"
    
    # Service URLs
    vector_service_url: str = "http://vector-db:8000"
    document_service_url: str = "http://document-processing:8000"
    
    # Analysis Settings
    enable_vector_rag: bool = True  # Use Vector DB for RAG
    rag_top_k: int = 5  # Number of chunks to retrieve
    
    # Cache Settings
    enable_response_cache: bool = True
    cache_ttl: int = 3600  # 1 hour in seconds
    
    # CORS Settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
