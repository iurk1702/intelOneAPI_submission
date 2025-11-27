# Refugee Acceptance Rate Predictor - Backend API

FastAPI backend service for predicting asylum acceptance rates using a trained XGBoost model.

## Setup

### 1. Train and Save the Model

First, train the model and save it to disk:

```bash
cd /Users/vaarunaykaushal/Documents/iurk1702/intelOneAPI_submission
python train_and_save_model.py
```

This will create the following files in the `models/` directory:
- `xgboost_model.pkl` - Main XGBoost model
- `xgboost_model_lower.pkl` - Lower quantile model (if quantile regression is available)
- `xgboost_model_upper.pkl` - Upper quantile model (if quantile regression is available)
- `residual_stats.pkl` - Residual statistics (fallback for confidence calculation)
- `label_encoders.pkl` - Label encoders for categorical features
- `model_metadata.pkl` - Model metadata (RMSE, training date, etc.)

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

Copy the example environment file and modify if needed:

```bash
cp .env.example .env
```

Edit `.env` to set:
- `PORT` - Server port (default: 8000)
- `MODEL_DIR` - Path to models directory (default: ../models)
- `CORS_ORIGINS` - Comma-separated list of allowed origins

### 4. Run the Server

```bash
# From the backend directory
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py directly
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /predict

Predict acceptance rate for given inputs.

**Request:**
```json
{
  "origin": "Syria",
  "asylum": "Germany",
  "year": "2015",
  "procedure": "Government"
}
```

**Response:**
```json
{
  "rate": 67.3,
  "confidence": 12.4
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input (unknown country, invalid year, etc.)
- `503 Service Unavailable` - Models not loaded

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

### GET /model/info

Get model metadata.

**Response:**
```json
{
  "model_type": "XGBoost",
  "rmse": 0.439356,
  "mae": 0.137031,
  "training_date": "2024-01-15T10:30:00",
  "n_samples_train": 64051,
  "n_samples_test": 16013
}
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Integration

The frontend is configured to call the API at `http://localhost:8000/predict`. 

To change the API URL, set the `VITE_API_URL` environment variable in the frontend:

```bash
# In refugee-insights directory
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

## Supported Countries and Procedures

### Origin Countries:
- Afghanistan, Syria, Iraq, Somalia, Eritrea, Sudan, Myanmar, Colombia, Venezuela, and others from the training data

### Asylum Countries:
- United States, Germany, France, United Kingdom, Canada, Sweden, Turkey, Kenya, South Africa, and others from the training data

### Procedure Types:
- "Government" - Government procedure
- "UNHCR" - UNHCR procedure
- "Joint" - Joint procedure
- "Unknown" - Unknown procedure type

## Notes

- The model uses only 3 features: origin country, asylum country, and procedure type
- Year is validated but not used in predictions (as per the original notebook)
- Confidence intervals are calculated using quantile regression (if available) or statistical methods based on model RMSE
- Unknown countries/procedures will return a 400 error with a helpful message

