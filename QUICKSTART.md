# Quick Start Guide

## Backend Setup

### Step 1: Train the Model
```bash
cd /Users/vaarunaykaushal/Documents/iurk1702/intelOneAPI_submission
python train_and_save_model.py
```

This will:
- Load and preprocess the asylum_seekers.csv data
- Train the XGBoost model
- Train quantile regression models for confidence intervals (if supported)
- Save all models and encoders to the `models/` directory

### Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Run the Backend Server
```bash
# Option 1: Using the run script
./run.sh

# Option 2: Using uvicorn directly
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using Python directly
python main.py
```

The API will be available at `http://localhost:8000`

### Step 4: Test the API
```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Syria",
    "asylum": "Germany",
    "year": "2015",
    "procedure": "Government"
  }'
```

## Frontend Setup

The frontend has been updated to call the backend API. To run:

```bash
cd /Users/vaarunaykaushal/Documents/iurk1702/refugee-insights
npm install  # if not already done
npm run dev
```

The frontend will call `http://localhost:8000/predict` by default.

To change the API URL, create a `.env.local` file:
```
VITE_API_URL=http://localhost:8000
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Models not loading
- Ensure `train_and_save_model.py` has been run successfully
- Check that the `models/` directory exists and contains the required `.pkl` files
- Verify the `MODEL_DIR` in `.env` points to the correct path

### CORS errors
- Ensure the frontend URL is in the `CORS_ORIGINS` environment variable
- Default is `http://localhost:5173` (Vite default port)

### Unknown country errors
- The model only supports countries that were in the training data
- Check the training data to see which countries are available
- The frontend dropdown may include countries not in the training data

## Project Structure

```
intelOneAPI_submission/
├── train_and_save_model.py    # Script to train and save models
├── models/                     # Saved models and encoders
│   ├── xgboost_model.pkl
│   ├── xgboost_model_lower.pkl
│   ├── xgboost_model_upper.pkl
│   ├── label_encoders.pkl
│   └── model_metadata.pkl
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── model_loader.py         # Model loading utilities
│   ├── predict.py              # Prediction logic
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment configuration template
│   └── README.md               # Detailed backend documentation
└── asylum_seekers.csv          # Training data
```

