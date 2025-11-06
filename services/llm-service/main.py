from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import local modules
from config import settings
from api import api_router
from llm_client import get_llm_client

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Service for AI-powered research paper analysis using LLMs",
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


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize LLM client
    llm_client = get_llm_client()
    available_providers = llm_client.get_available_providers()
    
    if available_providers:
        logger.info(f"LLM providers available: {', '.join(available_providers)}")
    else:
        logger.warning("No LLM providers configured! Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    logger.info(f"RAG enabled: {settings.enable_vector_rag}")
    logger.info(f"Vector DB URL: {settings.vector_service_url}")
    logger.info(f"Document Service URL: {settings.document_service_url}")


@app.get("/")
async def root():
    """Health check endpoint"""
    llm_client = get_llm_client()
    return {
        "service": settings.app_name,
        "status": "running",
        "version": settings.app_version,
        "api_versions": ["v1"],
        "docs": settings.docs_url,
        "llm_providers": llm_client.get_available_providers(),
        "features": {
            "document_analysis": True,
            "question_answering": True,
            "document_comparison": True,
            "chat": True,
            "rag": settings.enable_vector_rag
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
