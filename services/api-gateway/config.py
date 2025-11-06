"""
API Gateway Configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Settings
    app_name: str = "API Gateway"
    app_version: str = "1.0.0"
    debug: bool = False
        
    # Service info
    service_name: str = "api-gateway"
    
    # API Settings
    api_prefix: str = "/api"
    api_v1_prefix: str = "/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    
    # Service URLs (Docker network)
    document_service_url: str = "http://document-processing:8000"
    vector_service_url: str = "http://vector-db:8000"
    llm_service_url: str = "http://llm-service:8000"
    
    # Timeouts (seconds)
    request_timeout: int = 60
    upload_timeout: int = 300  # 5 minutes for large PDFs
    analysis_timeout: int = 120  # 2 minutes for LLM analysis
    
    # Rate Limiting
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 100  # requests per minute
    rate_limit_window: int = 60  # window in seconds
    
    # CORS Settings
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Authentication (basic)
    enable_auth: bool = False
    api_key: str = ""  # For simple API key auth
    
    # Logging
    log_requests: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
