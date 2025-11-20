from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class RiskCategory(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"

class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class RecommendationCategory(str, Enum):
    MEDICAL = "Medical"
    DIETARY = "Dietary"
    LIFESTYLE = "Lifestyle"

class FeatureContribution(BaseModel):
    feature: str = Field(..., description="NHANES feature code")
    feature_name: str = Field(..., description="Human-readable feature name")
    value: float = Field(..., description="Feature value for this user")
    impact: float = Field(..., description="SHAP impact on prediction")

class NutrientPrediction(BaseModel):
    nutrient: str = Field(..., description="Nutrient name")
    risk_score: float = Field(..., ge=0, le=1, description="Calibrated probability of deficiency (0-1)")
    risk_category: RiskCategory = Field(..., description="Risk level category")
    confidence: float = Field(..., ge=0, le=1, description="Calibrated probability estimate")
    confidence_lower: float = Field(..., ge=0, le=1, description="Lower bound of confidence interval")
    confidence_upper: float = Field(..., ge=0, le=1, description="Upper bound of confidence interval")
    note: str = Field(..., description="Clinical context and threshold information")

class Recommendation(BaseModel):
    category: RecommendationCategory = Field(..., description="Type of recommendation")
    priority: Priority = Field(..., description="Priority level")
    recommendation: str = Field(..., description="Specific recommendation text")
    rationale: str = Field(..., description="Clinical rationale")

class PredictionResponse(BaseModel):
    predictions: List[NutrientPrediction] = Field(..., description="Nutrient deficiency predictions")
    top_features: List[FeatureContribution] = Field(..., description="Most influential features")
    recommendations: List[Recommendation] = Field(..., description="Personalized recommendations")
    overall_health_score: float = Field(..., ge=0, le=1, description="Overall nutritional health score")