"""
API v1 Router
"""
from fastapi import APIRouter
from api.v1 import endpoints

# Create v1 router
router = APIRouter()

# Include endpoint routers
router.include_router(endpoints.router)
