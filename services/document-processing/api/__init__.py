"""
API Router Package
Manages API versioning
"""
from fastapi import APIRouter
from .v1 import router as v1_router

# Main API router
api_router = APIRouter()

# Include v1 routes with prefix
api_router.include_router(v1_router, prefix="/v1")

# Future: You can add v2 here
# from .v2 import router as v2_router
# api_router.include_router(v2_router, prefix="/v2")
