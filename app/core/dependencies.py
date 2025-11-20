from functools import lru_cache
from pathlib import Path
from ..models import NutrientPredictor

# Global predictor instance
_predictor_instance = None

@lru_cache()
def get_predictor() -> NutrientPredictor:
    """Get or create the predictor instance (singleton pattern)"""
    global _predictor_instance
    
    if _predictor_instance is None:
        model_dir = Path(__file__).parent.parent.parent / "saved_models"
        _predictor_instance = NutrientPredictor(model_dir)
        _predictor_instance.load_models()
    
    return _predictor_instance