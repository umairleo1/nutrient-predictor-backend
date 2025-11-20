from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/")
async def root() -> Dict:
    """Root endpoint with API information"""
    return {
        "message": "Nutrient Deficiency Prediction API",
        "status": "active",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@router.get("/health")
async def health_check() -> Dict:
    """Health check endpoint"""
    # Import here to avoid circular imports
    from ..core.dependencies import get_predictor
    
    predictor = get_predictor()
    return {
        "status": "healthy",
        "models_loaded": predictor.models_loaded,
        "service": "nutrient-prediction-api"
    }