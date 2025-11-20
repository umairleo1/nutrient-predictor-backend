import joblib
import numpy as np
import pandas as pd
import shap
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from ..schemas import UserProfile, NutrientPrediction, FeatureContribution

class NutrientPredictor:
    """Main predictor service for nutrient deficiency prediction"""
    
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.models_loaded = False
        self.models = {}
        self.calibrated_models = {}
        self.explainers = {}
        self.scalers = {}
        self.feature_names = []
        
        # Clinical thresholds for reference (evidence-based)
        self.clinical_thresholds = {
            'b12_threshold_pg_ml': 200,  # NIH Office of Dietary Supplements
            'hgb_threshold_male_g_dl': 13.0,  # WHO criteria for anemia in men
            'hgb_threshold_female_g_dl': 12.0,  # WHO criteria for anemia in women  
            'vitd_threshold_ng_ml': 20,  # Endocrine Society clinical practice guideline
        }
        
    def load_models(self) -> bool:
        """Load all trained models, calibrated models, and preprocessors"""
        try:
            nutrients = ['b12_deficient', 'iron_deficient', 'diabetes_risk']
            
            # Load base models
            self.models = {}
            self.calibrated_models = {}
            self.scalers = {}
            
            for nutrient in nutrients:
                # Load base model for interpretability
                self.models[nutrient] = joblib.load(self.model_dir / f"{nutrient}_model.pkl")
                
                # Load calibrated model for reliable probabilities
                try:
                    self.calibrated_models[nutrient] = joblib.load(
                        self.model_dir / f"{nutrient}_calibrated_model.pkl"
                    )
                except FileNotFoundError:
                    print(f"Warning: Calibrated model not found for {nutrient}, using base model")
                    self.calibrated_models[nutrient] = self.models[nutrient]
                
                # Load individual scalers
                try:
                    self.scalers[nutrient] = joblib.load(self.model_dir / f"{nutrient}_scaler.pkl")
                except FileNotFoundError:
                    print(f"Warning: Individual scaler not found for {nutrient}")
            
            # Fallback to shared scaler and feature names if individual ones don't exist
            if not self.scalers:
                self.scaler = joblib.load(self.model_dir / "scaler.pkl")
                for nutrient in nutrients:
                    self.scalers[nutrient] = self.scaler
                    
            self.feature_names = joblib.load(self.model_dir / "feature_names.pkl")
            
            # Create SHAP explainers
            self.explainers = {
                'b12_deficient': shap.TreeExplainer(self.models['b12_deficient']),
                'iron_deficient': shap.TreeExplainer(self.models['iron_deficient']),
                'diabetes_risk': shap.TreeExplainer(self.models['diabetes_risk'])
            }
            
            self.models_loaded = True
            print(f"Models loaded successfully! Features: {len(self.feature_names)}")
            return True
            
        except Exception as e:
            print(f"Error loading models: {e}")
            self.models_loaded = False
            return False
    
    def create_feature_vector(self, profile: UserProfile) -> pd.DataFrame:
        """Convert user profile to NHANES feature vector"""
        feature_dict = {}
        
        for feat in self.feature_names:
            if feat == 'RIDAGEYR':
                feature_dict[feat] = profile.age
            elif feat == 'RIAGENDR':
                feature_dict[feat] = 1 if profile.gender == "Male" else 2
            elif feat == 'RIDRETH3':
                race_mapping = {
                    "Mexican American": 1,
                    "Other Hispanic": 2, 
                    "Non-Hispanic White": 3,
                    "Non-Hispanic Black": 4,
                    "Other Race": 6
                }
                feature_dict[feat] = race_mapping.get(profile.race, 6)
            elif feat == 'BMXWT':
                feature_dict[feat] = profile.weight
            elif feat == 'BMXHT':
                feature_dict[feat] = profile.height
            elif feat == 'BMXBMI':
                height_m = profile.height / 100
                feature_dict[feat] = profile.weight / (height_m ** 2)
            elif feat == 'DMDBORN4':
                feature_dict[feat] = 1 if profile.country_of_birth == "US" else 2
            elif feat == 'DMDEDUC2':
                education_mapping = {
                    "Less than 9th grade": 1,
                    "9-11th grade": 2,
                    "High school graduate": 3,
                    "Some college": 4,
                    "College graduate or above": 5
                }
                feature_dict[feat] = education_mapping.get(profile.education, 3)
            elif feat == 'DMDMARTL':
                marital_mapping = {
                    "Married": 1,
                    "Widowed": 2,
                    "Divorced": 3,
                    "Separated": 4,
                    "Never married": 5,
                    "Living with partner": 6
                }
                feature_dict[feat] = marital_mapping.get(profile.marital_status, 5)
            elif feat == 'SDDSRVYR':
                feature_dict[feat] = 8  # 2013-2014 survey
            elif feat == 'RIDSTATR':
                feature_dict[feat] = 2  # Both interviewed and examined
            elif feat == 'RIDRETH1':
                feature_dict[feat] = feature_dict.get('RIDRETH3', 3)
            elif feat == 'RIDEXMON':
                feature_dict[feat] = 6  # Default examination month
            elif feat in ['DMQMILIZ', 'DMDCITZN']:
                feature_dict[feat] = 1  # Default values
            elif feat in ['SIALANG', 'FIALANG']:
                feature_dict[feat] = 1  # English
            elif feat in ['SIAPROXY', 'SIAINTRP', 'FIAPROXY']:
                feature_dict[feat] = 2  # No proxy/interpreter
            else:
                feature_dict[feat] = 0.0  # Default
        
        df = pd.DataFrame([feature_dict])
        return df[self.feature_names]
    
    def predict(self, profile: UserProfile) -> Tuple[List[NutrientPrediction], List[FeatureContribution]]:
        """Make predictions and return results with interpretability"""
        if not self.models_loaded:
            raise RuntimeError("Models not loaded")
        
        # Create features
        features = self.create_feature_vector(profile)
        
        # Make predictions
        predictions = []
        all_shap_values = []
        
        nutrient_mapping = {
            'b12_deficient': 'Vitamin B12',
            'iron_deficient': 'Iron',
            'diabetes_risk': 'Diabetes Risk'
        }
        
        for nutrient_key, nutrient_name in nutrient_mapping.items():
            model = self.models[nutrient_key]
            explainer = self.explainers[nutrient_key]
            
            # Get calibrated probability for reliable estimates
            calibrated_model = self.calibrated_models[nutrient_key]
            scaler = self.scalers[nutrient_key]  # Use individual scaler
            
            # Scale features using nutrient-specific scaler
            features_scaled_individual = scaler.transform(features)
                
            # Get calibrated probability
            proba = calibrated_model.predict_proba(features_scaled_individual)[0, 1]
            
            # Categorize risk with clinical context
            if proba < 0.15:
                risk_category = 'Low'
            elif proba < 0.4:
                risk_category = 'Moderate'  
            else:
                risk_category = 'High'
            
            # Calculate confidence interval instead of misleading "100%" confidence
            # Use prediction uncertainty from ensemble or bootstrap if available
            base_proba = model.predict_proba(features_scaled_individual)[0, 1]
            uncertainty = abs(proba - base_proba) + 0.05  # Minimum uncertainty
            
            # Confidence interval bounds
            conf_lower = max(0.0, proba - uncertainty)
            conf_upper = min(1.0, proba + uncertainty)
            
            # Create condition-specific naming and notes with actionable next steps
            if nutrient_key == 'iron_deficient':
                display_name = 'Anemia Risk'
                note = 'Based on hemoglobin levels (WHO criteria). Not iron deficiency specifically. Next step: Confirm with lab Hb test; if low, clinician should check ferritin.'
            elif nutrient_key == 'diabetes_risk':
                display_name = 'Diabetes Risk (Limited)'
                note = 'Based on demographic indicators only. This prediction has very limited accuracy for diabetes screening. Next step: Consult healthcare provider for proper diabetes screening (HbA1c, fasting glucose).'
            else:
                display_name = nutrient_name
                note = 'Based on demographic and health indicators. This prediction does not diagnose B12 deficiency. Next step: If high risk → request serum B12 (and MMA) from GP.'
            
            predictions.append(NutrientPrediction(
                nutrient=display_name,
                risk_score=float(proba),
                risk_category=risk_category,
                confidence=float(proba),  # Use calibrated probability as confidence
                confidence_lower=float(conf_lower),
                confidence_upper=float(conf_upper),
                note=note
            ))
            
            # SHAP values using base model for interpretability
            shap_values = explainer.shap_values(features_scaled_individual)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Positive class
            all_shap_values.append(shap_values[0])
        
        # Aggregate SHAP values
        avg_shap = np.mean(all_shap_values, axis=0)
        
        # Top features
        top_features = []
        for i, feat_name in enumerate(self.feature_names):
            top_features.append(FeatureContribution(
                feature=feat_name,
                feature_name=self._get_feature_description(feat_name),
                value=float(features.iloc[0, i]),
                impact=float(avg_shap[i])
            ))
        
        # Sort by absolute impact
        top_features.sort(key=lambda x: abs(x.impact), reverse=True)
        
        return predictions, top_features[:5]
    
    def _get_feature_description(self, feature_code: str) -> str:
        """Convert NHANES feature codes to human-readable descriptions"""
        descriptions = {
            'RIDAGEYR': 'Age (years)',
            'RIAGENDR': 'Gender',
            'RIDRETH3': 'Race/Ethnicity',
            'BMXWT': 'Weight (kg)',
            'BMXHT': 'Height (cm)',
            'BMXBMI': 'Body Mass Index',
            'SDDSRVYR': 'Survey Year',
            'RIDSTATR': 'Interview/Examination Status',
            'RIDRETH1': 'Race/Ethnicity (Detailed)',
            'RIDEXMON': 'Examination Month',
            'DMQMILIZ': 'Military Service',
            'DMDBORN4': 'Country of Birth',
            'DMDCITZN': 'Citizenship Status',
            'DMDEDUC2': 'Education Level',
            'DMDMARTL': 'Marital Status',
            'SIALANG': 'Interview Language',
            'SIAPROXY': 'Proxy Used in Interview',
            'SIAINTRP': 'Interpreter Used',
            'FIALANG': 'Family Interview Language',
            'FIAPROXY': 'Family Proxy Used'
        }
        return descriptions.get(feature_code, feature_code)
    
    def get_feature_info(self) -> Dict:
        """Get information about model features"""
        return {
            "features": [
                {
                    "code": feat,
                    "description": self._get_feature_description(feat)
                } for feat in self.feature_names
            ],
            "total_features": len(self.feature_names)
        }