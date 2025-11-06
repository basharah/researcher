"""
API v1 Router
"""
from fastapi import APIRouter
from api.v1 import endpoints, auth_endpoints

# Create v1 router
router = APIRouter()

# Include endpoint routers
router.include_router(endpoints.router)
router.include_router(auth_endpoints.router, prefix="/auth", tags=["authentication"])
