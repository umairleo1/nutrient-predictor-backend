# Nutrient Deficiency Predictor API

A FastAPI-based backend service for predicting nutrient deficiencies using machine learning models trained on NHANES (National Health and Nutrition Examination Survey) data.

## Overview

This REST API provides personalized nutrient deficiency predictions based on demographic and physiological data. The system uses XGBoost models with SHAP (SHapley Additive exPlanations) interpretability to predict risks for B12 deficiency, iron deficiency, and diabetes.

## Features

- **Machine Learning Predictions**: XGBoost models for nutrient deficiency prediction
- **Model Interpretability**: SHAP values for prediction explanations
- **Health Monitoring**: System health and model status endpoints
- **Data Validation**: Comprehensive input validation using Pydantic
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **CORS Support**: Configured for web application integration

## Technology Stack

- **Framework**: FastAPI
- **Machine Learning**: XGBoost, scikit-learn
- **Model Interpretability**: SHAP
- **Data Validation**: Pydantic
- **Development**: uvicorn, Python 3.9+

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/umairleo1/nutrient-predictor-backend.git
cd nutrient-predictor-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

```http
GET /health
```

Returns system status and model loading information.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "service": "Nutrient Deficiency Predictor API"
}
```

### Prediction

```http
POST /api/predict
```

Generates nutrient deficiency predictions based on user profile data.

**Request Body:**
```json
{
  "age": 25,
  "gender": "Female",
  "race": "White",
  "weight": 65.0,
  "height": 165.0,
  "education": "College graduate",
  "marital_status": "Single",
  "country_of_birth": "United States"
}
```

**Response:**
```json
{
  "predictions": {
    "b12_deficient": {
      "risk_score": 0.15,
      "risk_level": "Low",
      "confidence": 0.85
    },
    "iron_deficient": {
      "risk_score": 0.25,
      "risk_level": "Low",
      "confidence": 0.78
    },
    "diabetes_risk": {
      "risk_score": 0.08,
      "risk_level": "Very Low",
      "confidence": 0.92
    }
  },
  "shap_explanations": {},
  "recommendations": []
}
```

### Feature Information

```http
GET /api/features
```

Returns information about model features and their descriptions.

## Model Information

The system includes trained models for:

1. **B12 Deficiency Prediction**
   - AUC: 0.758
   - Calibrated AUC: 0.785
   - Training samples: 9,813

2. **Iron Deficiency Prediction**
   - AUC: 0.809
   - Calibrated AUC: 0.810
   - Training samples: 9,813

3. **Diabetes Risk Prediction**
   - AUC: 0.517
   - Calibrated AUC: 0.509
   - Training samples: 9,813

All models use 20 demographic and physiological features derived from NHANES data.

## Data Source

Models are trained on the National Health and Nutrition Examination Survey (NHANES) 2013-2014 dataset, which provides nationally representative data on the health and nutritional status of adults and children in the United States.

## Project Structure

```
app/
├── api/                 # API route handlers
│   ├── health.py       # Health check endpoints
│   └── predictions.py  # Prediction endpoints
├── core/               # Core functionality
│   └── dependencies.py # Dependency injection
├── models/             # ML model logic
│   ├── predictor.py    # Prediction service
│   └── recommendations.py # Recommendation engine
├── schemas/            # Pydantic data models
│   ├── prediction.py   # Prediction schemas
│   └── user_profile.py # User profile schemas
└── main.py            # FastAPI application entry point

saved_models/          # Trained ML models and metadata
requirements.txt       # Python dependencies
```

## Development

### Running Tests

```bash
# Add test commands when tests are implemented
pytest
```

### Code Quality

The project follows Python best practices:
- Type hints throughout codebase
- Pydantic for data validation
- Structured logging
- Comprehensive error handling

## Deployment

This API is designed for easy deployment on cloud platforms:

- **Railway**: Automatic deployment from GitHub
- **Heroku**: Compatible with Procfile
- **Docker**: Container-ready architecture
- **AWS/GCP**: Cloud platform compatible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and research purposes only. Not intended for medical diagnosis or treatment.

## Disclaimer

This system is designed for educational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.

## Contact

**Author**: Muhammad Umair  
**LinkedIn**: [muhammad-umair-amin](https://www.linkedin.com/in/muhammad-umair-amin/)  
**GitHub**: [umairleo1](https://github.com/umairleo1)

---

**Note**: This is a research demonstration project showcasing machine learning applications in healthcare analytics.