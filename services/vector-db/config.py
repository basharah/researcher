"""
Vector DB Service Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Service info
    service_name: str = "vector-db"
    
    # Database
    database_url: str = "postgresql://researcher:researcher_pass@localhost:5432/research_papers"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Fast and good quality
    embedding_dimension: int = 384  # Dimension for all-MiniLM-L6-v2
    
    # Chunking settings
    chunk_size: int = 500  # Characters per chunk
    chunk_overlap: int = 50  # Overlap between chunks
    
    # Search settings
    max_search_results: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
