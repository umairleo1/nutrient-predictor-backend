from fastapi import APIRouter
from .health import router as health_router
from .predictions import router as predictions_router

api_router = APIRouter()

# Include health routes at root level
api_router.include_router(health_router, tags=["health"])

# Include prediction routes with prefix
api_router.include_router(predictions_router, prefix="/api", tags=["predictions"])