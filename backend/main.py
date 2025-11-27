"""
FastAPI backend for refugee acceptance rate prediction.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional
import os
from dotenv import load_dotenv
from model_loader import ModelLoader
from predict import predict_acceptance_rate

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Refugee Acceptance Rate Predictor API",
    description="API for predicting asylum acceptance rates using XGBoost",
    version="1.0.0"
)

# CORS configuration
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8080")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
# Allow all Vercel preview deployments if CORS_ORIGINS is not set or empty
if not cors_origins or cors_origins == [""]:
    cors_origins = ["http://localhost:5173", "http://localhost:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model loader
model_loader = ModelLoader()

# Load models on startup
@app.on_event("startup")
async def startup_event():
    model_dir = os.getenv("MODEL_DIR", "../models")
    success, error = model_loader.load_models(model_dir)
    if not success:
        print(f"WARNING: Failed to load models: {error}")
        print("API will return errors until models are loaded.")

# Request/Response models
class PredictionRequest(BaseModel):
    origin: str = Field(..., description="Country of origin")
    asylum: str = Field(..., description="Country/territory of asylum/residence")
    year: str = Field(..., description="Year (2000-2016)")
    procedure: str = Field(..., description="RSD procedure type: Government, UNHCR, Joint, or Unknown")
    
    @validator('year')
    def validate_year(cls, v):
        try:
            year_int = int(v)
            if not (2000 <= year_int <= 2016):
                raise ValueError("Year must be between 2000 and 2016")
            return v
        except ValueError:
            raise ValueError("Year must be a valid integer")
    
    @validator('procedure')
    def validate_procedure(cls, v):
        valid_procedures = ["Government", "UNHCR", "Joint", "Unknown"]
        if v not in valid_procedures:
            raise ValueError(f"Procedure must be one of: {', '.join(valid_procedures)}")
        return v

class PredictionResponse(BaseModel):
    rate: float = Field(..., description="Predicted acceptance rate as percentage")
    confidence: float = Field(..., description="Confidence interval as ± percentage")

class ModelInfoResponse(BaseModel):
    model_type: str
    rmse: float
    mae: Optional[float] = None
    training_date: Optional[str] = None
    n_samples_train: Optional[int] = None
    n_samples_test: Optional[int] = None

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    models_loaded = model_loader.is_loaded()
    return {
        "status": "healthy" if models_loaded else "degraded",
        "models_loaded": models_loaded
    }

@app.get("/model/info", response_model=ModelInfoResponse)
async def model_info():
    """Get model metadata."""
    if not model_loader.is_loaded():
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    metadata = model_loader.metadata or {}
    return ModelInfoResponse(
        model_type=metadata.get("model_type", "XGBoost"),
        rmse=metadata.get("rmse", 0.0),
        mae=metadata.get("mae"),
        training_date=metadata.get("training_date"),
        n_samples_train=metadata.get("n_samples_train"),
        n_samples_test=metadata.get("n_samples_test")
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Predict acceptance rate for given inputs.
    
    - **origin**: Country of origin (e.g., "Syria", "Afghanistan")
    - **asylum**: Country/territory of asylum/residence (e.g., "Germany", "United States")
    - **year**: Year between 2000-2016 (as string)
    - **procedure**: RSD procedure type ("Government", "UNHCR", "Joint", or "Unknown")
    
    Returns predicted acceptance rate as percentage and confidence interval.
    """
    if not model_loader.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please check server logs."
        )
    
    # Make prediction
    rate, confidence, error = predict_acceptance_rate(
        country=request.asylum,
        origin=request.origin,
        procedure=request.procedure,
        model_loader=model_loader
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # Convert rate from [0, 1] to percentage [0, 100]
    rate_percentage = rate * 100
    confidence_percentage = confidence * 100
    
    return PredictionResponse(
        rate=round(rate_percentage, 1),
        confidence=round(confidence_percentage, 1)
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

