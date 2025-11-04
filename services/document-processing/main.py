from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import local modules
from database import engine, Base
from api import api_router
from config import settings


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
    return {
        "status": "healthy",
        "database": "connected",
        "upload_dir": str(settings.upload_dir),
        "upload_dir_exists": settings.upload_dir.exists()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
