"""
API Router Configuration
"""
from fastapi import APIRouter

# Import v1 router
from api.v1 import router as v1_router

# Create main API router
api_router = APIRouter()

# Include v1 router
api_router.include_router(v1_router, prefix="/v1", tags=["v1"])
