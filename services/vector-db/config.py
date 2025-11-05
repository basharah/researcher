"""
Vector DB Service Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Settings
    app_name: str = "Document Processing Service"
    app_version: str = "1.0.0"
    debug: bool = False
        
    # Service info
    service_name: str = "vector-db"
    
    # API Settings
    api_prefix: str = "/api"
    api_v1_prefix: str = "/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Database
    database_url: str = "postgresql://researcher:researcher_pass@localhost:5432/research_papers"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Fast and good quality
    embedding_dimension: int = 384  # Dimension for all-MiniLM-L6-v2
    use_gpu: bool = True  # Enable GPU acceleration if available
    
    # Chunking settings
    chunk_size: int = 500  # Characters per chunk
    chunk_overlap: int = 50  # Overlap between chunks
    
    # Search settings
    max_search_results: int = 10
    
    # CORS Settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def full_api_v1_prefix(self) -> str:
        """Get full API v1 prefix"""
        return f"{self.api_prefix}{self.api_v1_prefix}"

        
settings = Settings()
