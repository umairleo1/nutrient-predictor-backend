from typing import List
from ..schemas import UserProfile, NutrientPrediction, Recommendation

class RecommendationEngine:
    """
    Generate evidence-based, clinically safe personalized recommendations.
    Recommendations are conservative and emphasize discussion with a healthcare provider.
    
    Clinical references:
    - B12: NIH Office of Dietary Supplements
    - Iron/Anemia: WHO anemia guidelines  
    - Vitamin D: Endocrine Society clinical practice guidelines
    """
    
    @staticmethod
    def generate_recommendations(predictions: List[NutrientPrediction], profile: UserProfile) -> List[Recommendation]:
        recommendations = []
        
        for pred in predictions:
            if pred.risk_category in ['High', 'Moderate']:
                priority = 'High' if pred.risk_category == 'High' else 'Medium'
                
                if 'B12' in pred.nutrient:
                    recommendations.extend(RecommendationEngine._get_b12_recommendations(pred, priority))
                elif 'Iron' in pred.nutrient or 'Anemia' in pred.nutrient:
                    recommendations.extend(RecommendationEngine._get_iron_recommendations(pred, profile, priority))
                elif 'Vitamin D' in pred.nutrient:
                    recommendations.extend(RecommendationEngine._get_vitd_recommendations(pred, priority))
        
        recommendations.extend(RecommendationEngine._get_lifestyle_recommendations(profile))
        return recommendations

    # ------------------------------
    #  B12 Recommendations
    # ------------------------------
    @staticmethod
    def _get_b12_recommendations(pred: NutrientPrediction, priority: str) -> List[Recommendation]:
        recs = []

        if pred.risk_category == 'High':
            recs.append(Recommendation(
                category='Medical',
                priority=priority,
                recommendation=(
                    "Discuss B12 testing and possible supplementation with a healthcare professional. "
                    "High-dose B12 supplements (commonly 1000 μg) are available over-the-counter, "
                    "but dosage should be clinically guided."
                ),
                rationale=f'High predicted risk of B12 deficiency (risk score: {pred.risk_score:.2f})'
            ))

        recs.append(Recommendation(
            category='Dietary',
            priority=priority,
            recommendation=(
                "Increase B12-rich foods such as fortified cereals, dairy products, eggs, fish, "
                "and lean meats."
            ),
            rationale="Vitamin B12 is primarily obtained from animal products and fortified foods."
        ))

        return recs

    # ------------------------------
    #  Iron (Anemia) Recommendations
    # ------------------------------
    @staticmethod
    def _get_iron_recommendations(pred: NutrientPrediction, profile: UserProfile, priority: str) -> List[Recommendation]:
        recs = []

        recs.append(Recommendation(
            category='Dietary',
            priority=priority,
            recommendation=(
                "Increase intake of iron-rich foods such as lean red meat, poultry, fish, "
                "legumes, dark leafy greens, and fortified cereals."
            ),
            rationale=f'{pred.risk_category} predicted risk of anemia/iron deficiency (risk score: {pred.risk_score:.2f}).'
        ))

        # SAFETY IMPROVEMENT — No automatic dosage recommendation
        # Supplementation requires medical assessment.
        if profile.gender == "Female":
            recs.append(Recommendation(
                category='Medical',
                priority=priority,
                recommendation=(
                    "Consider discussing iron supplementation with a healthcare provider. "
                    "Women often have higher iron requirements, but supplementation should "
                    "only be started after clinical evaluation."
                ),
                rationale="Additional iron needs may occur due to menstrual blood loss."
            ))

        recs.append(Recommendation(
            category='Dietary',
            priority='Medium',
            recommendation=(
                "Enhance iron absorption by consuming vitamin C-rich foods (e.g., citrus fruits) "
                "together with iron-rich meals."
            ),
            rationale="Vitamin C improves non-heme iron absorption."
        ))

        return recs

    # ------------------------------
    #  Vitamin D Recommendations
    # ------------------------------
    @staticmethod
    def _get_vitd_recommendations(pred: NutrientPrediction, priority: str) -> List[Recommendation]:
        recs = []

        recs.append(Recommendation(
            category='Lifestyle',
            priority=priority,
            recommendation=(
                "Get regular safe sunlight exposure when possible (10–30 minutes depending on skin type). "
                "Discuss vitamin D supplementation with a healthcare provider if sunlight exposure is limited."
            ),
            rationale=f'{pred.risk_category} predicted risk of vitamin D deficiency (risk score: {pred.risk_score:.2f}).'
        ))

        recs.append(Recommendation(
            category='Dietary',
            priority=priority,
            recommendation=(
                "Include vitamin D-rich foods such as fatty fish (e.g., salmon, mackerel), "
                "fortified dairy or plant milks, and egg yolks."
            ),
            rationale="Few foods naturally contain vitamin D."
        ))

        return recs

    # ------------------------------
    #  Lifestyle-based Recommendations
    # ------------------------------
    @staticmethod
    def _get_lifestyle_recommendations(profile: UserProfile) -> List[Recommendation]:
        recs = []

        bmi = profile.weight / ((profile.height / 100) ** 2)

        if bmi < 18.5:
            recs.append(Recommendation(
                category='Lifestyle',
                priority='Medium',
                recommendation=(
                    "Consider speaking with a registered dietitian to develop a healthy weight-gain plan."
                ),
                rationale=f"BMI of {bmi:.1f} is below the healthy range."
            ))
        
        elif bmi > 25:
            recs.append(Recommendation(
                category='Lifestyle',
                priority='Medium',
                recommendation=(
                    "Engage in regular physical activity and follow a balanced diet to support healthy "
                    "weight management."
                ),
                rationale=f"BMI of {bmi:.1f} is {'slightly ' if bmi < 30 else ''}above the healthy range."
            ))

        if profile.age > 65:
            recs.append(Recommendation(
                category='Medical',
                priority='Medium',
                recommendation=(
                    "Older adults may benefit from routine screening for vitamin D, B12, and iron status."
                ),
                rationale="Nutrient absorption and dietary intake often change with age."
            ))

        recs.append(Recommendation(
            category='Lifestyle',
            priority='Low',
            recommendation="Maintain a balanced diet with a variety of food groups.",
            rationale="Dietary diversity supports adequate nutrient intake."
        ))

        return recs