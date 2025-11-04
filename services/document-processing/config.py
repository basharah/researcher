"""
Configuration management using Pydantic Settings
Loads configuration from environment variables and .env file
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    app_name: str = "Document Processing Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Settings
    api_prefix: str = "/api"
    api_v1_prefix: str = "/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # Database Settings
    database_url: str = "postgresql://researcher:researcher_pass@localhost:5432/research_papers"
    database_echo: bool = False  # Set to True to see SQL queries in logs
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_decode_responses: bool = True
    
    # File Upload Settings
    upload_dir: Path = Path("./uploads")
    max_file_size: int = 10 * 1024 * 1024  # 10MB in bytes
    allowed_extensions: list[str] = ["pdf"]
    
    # PDF Processing Settings
    pdf_extraction_timeout: int = 60  # seconds
    max_page_count: int = 500
    
    # Service URLs
    vector_service_url: str = "http://vector-db:8000"  # Docker internal network
    llm_service_url: Optional[str] = None
    
    # Vector DB Integration
    enable_vector_db: bool = True  # Enable automatic vector DB processing
    vector_db_timeout: int = 300  # 5 minutes for embedding generation
    
    # Security Settings (for future use)
    secret_key: Optional[str] = None
    api_key: Optional[str] = None
    
    # LLM API Keys (for Phase 3)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def full_api_v1_prefix(self) -> str:
        """Get full API v1 prefix"""
        return f"{self.api_prefix}{self.api_v1_prefix}"
    
    def create_upload_dir(self) -> None:
        """Create upload directory if it doesn't exist"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Create upload directory on import
settings.create_upload_dir()
