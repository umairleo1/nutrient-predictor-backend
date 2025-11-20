from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from ..schemas import UserProfile, PredictionResponse
from ..models import NutrientPredictor, RecommendationEngine
from ..core.dependencies import get_predictor

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_deficiencies(
    profile: UserProfile,
    predictor: NutrientPredictor = Depends(get_predictor)
) -> PredictionResponse:
    """
    Predict nutrient deficiencies and provide personalized recommendations
    
    Returns:
        - Individual nutrient risk predictions
        - Top contributing features with SHAP explanations
        - Evidence-based personalized recommendations
        - Overall nutritional health score
    """
    if not predictor.models_loaded:
        raise HTTPException(
            status_code=503, 
            detail="Models not loaded. Please ensure trained models are in saved_models/ directory"
        )
    
    try:
        # Make predictions
        predictions, top_features = predictor.predict(profile)
        
        # Generate recommendations
        recommendations = RecommendationEngine.generate_recommendations(predictions, profile)
        
        # Calculate overall health score
        risk_scores = [p.risk_score for p in predictions]
        overall_health_score = max(0, 1 - (sum(risk_scores) / len(risk_scores)))
        
        return PredictionResponse(
            predictions=predictions,
            top_features=top_features,
            recommendations=recommendations,
            overall_health_score=float(overall_health_score)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/features")
async def get_features(
    predictor: NutrientPredictor = Depends(get_predictor)
) -> Dict:
    """
    Get information about the features used by the model
    
    Returns:
        - List of feature codes and descriptions
        - Total number of features
    """
    if not predictor.models_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return predictor.get_feature_info()