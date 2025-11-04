from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import local modules
from database import engine, Base
from api import api_router
from config import settings
from vector_client import get_vector_client


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Service for uploading and processing research papers",
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include API router
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": settings.app_name,
        "status": "running",
        "version": settings.app_version,
        "api_versions": ["v1"],
        "docs": settings.docs_url
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "database": "connected",
        "upload_dir": str(settings.upload_dir),
        "upload_dir_exists": settings.upload_dir.exists(),
        "vector_db_enabled": settings.enable_vector_db,
        "vector_db_status": "disabled"
    }
    
    # Check Vector DB if enabled
    if settings.enable_vector_db:
        vector_client = get_vector_client()
        is_healthy = await vector_client.health_check()
        health_status["vector_db_status"] = "healthy" if is_healthy else "unavailable"
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
