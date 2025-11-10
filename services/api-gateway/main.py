"""
API Gateway Service - Main Application
Unified entry point for all microservices
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from config import settings
from api import api_router
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Research Paper Analysis API Gateway",
    description="Unified API for Document Processing, Vector DB, and LLM services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Allow frontend access
logger.info(f"Configuring CORS with origins: {settings.cors_origins}, allow_credentials: True")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],  # Explicitly expose Set-Cookie header
)

# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event():
    """Log startup information and initialize database"""
    # Initialize database tables
    logger.info("Initializing database tables...")
    init_db()
    
    logger.info("=" * 60)
    logger.info("API Gateway Service Starting")
    logger.info("=" * 60)
    logger.info(f"Service: {settings.service_name}")
    logger.info(f"API Prefix: {settings.api_prefix}")
    logger.info(f"CORS Origins: {settings.cors_origins}")
    logger.info(f"Authentication: {'Enabled' if settings.enable_auth else 'Disabled'}")
    logger.info("")
    logger.info("Backend Services:")
    logger.info(f"  - Document Processing: {settings.document_service_url}")
    logger.info(f"  - Vector DB: {settings.vector_service_url}")
    logger.info(f"  - LLM Service: {settings.llm_service_url}")
    logger.info("")
    logger.info(f"Request Timeout: {settings.request_timeout}s")
    if settings.enable_rate_limiting:
        logger.info(f"Rate Limiting: {settings.rate_limit_requests} requests per minute")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("API Gateway Service Shutting Down")


@app.get("/")
async def root():
    """Root endpoint - Basic info"""
    return {
        "service": "API Gateway",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "api": settings.api_prefix
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Development only
        log_level="info"
    )
