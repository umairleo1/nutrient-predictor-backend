from pydantic import BaseModel, Field
from typing import Literal

class UserProfile(BaseModel):
    age: int = Field(..., ge=18, le=120, description="Age in years")
    gender: Literal["Male", "Female"] = Field(..., description="Biological gender")
    race: Literal[
        "Mexican American", 
        "Other Hispanic", 
        "Non-Hispanic White", 
        "Non-Hispanic Black", 
        "Other Race"
    ] = Field(..., description="Race/ethnicity category")
    weight: float = Field(..., gt=30, lt=300, description="Weight in kilograms")
    height: float = Field(..., gt=100, lt=250, description="Height in centimeters")
    education: Literal[
        "Less than 9th grade",
        "9-11th grade", 
        "High school graduate",
        "Some college",
        "College graduate or above"
    ] = Field(..., description="Highest education level")
    marital_status: Literal[
        "Married",
        "Widowed", 
        "Divorced",
        "Separated",
        "Never married",
        "Living with partner"
    ] = Field(..., description="Current marital status")
    country_of_birth: Literal["US", "Other"] = Field(..., description="Country of birth")
    
    class Config:
        schema_extra = {
            "example": {
                "age": 35,
                "gender": "Female",
                "race": "Non-Hispanic White",
                "weight": 65.0,
                "height": 165.0,
                "education": "College graduate or above",
                "marital_status": "Married",
                "country_of_birth": "US"
            }
        }