"""
API v1 Router
Aggregates all v1 endpoints
"""
from fastapi import APIRouter
from api.v1 import endpoints

# Create v1 router
router = APIRouter()

# Include all v1 endpoints
router.include_router(endpoints.router, tags=["vector"])