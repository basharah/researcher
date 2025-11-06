"""
Database setup for API Gateway
PostgreSQL connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from config import settings

logger = logging.getLogger(__name__)

# Database URL - reuse the same PostgreSQL as document-processing
# In production, you might want a separate database or schema
DATABASE_URL = settings.database_url if hasattr(settings, 'database_url') else \
    "postgresql://researcher:researcher_pass@postgres:5432/research_papers"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.debug if hasattr(settings, 'debug') else False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    
    Usage:
        @router.post("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            user = db.query(User).filter(User.email == email).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Called on application startup
    """
    from models import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
