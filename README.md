# Refugee Acceptance Rate Predictor

Machine Learning system for predicting asylum acceptance rates using XGBoost, Random Forest, and Neural Networks. This project addresses UN SDG Goal 16 by analyzing 80,064 asylum cases (2000-2016) to predict acceptance rates.

## 🌐 Live Deployment

- **Frontend**: [https://refugee-insights-frontend-odpdwqv0x.vercel.app/](https://refugee-insights-frontend-odpdwqv0x.vercel.app/)

## 📊 Project Overview

This project analyzes UNHCR asylum seeker data to predict acceptance rates based on:
- **Origin Country**: Country of origin of the asylum seeker
- **Asylum Country**: Country/territory where asylum is being sought
- **Procedure Type**: RSD (Refugee Status Determination) procedure type

The system uses an XGBoost model trained on historical data to predict acceptance rates with confidence intervals.

## 🏗️ Project Structure

```
intelOneAPI_submission/
├── backend/                 # FastAPI backend service
│   ├── main.py             # FastAPI application
│   ├── model_loader.py     # Model loading utilities
│   ├── predict.py          # Prediction logic
│   └── requirements.txt    # Python dependencies
├── models/                  # Trained ML models
│   ├── xgboost_model.pkl
│   ├── label_encoders.pkl
│   └── model_metadata.pkl
├── train_and_save_model.py  # Model training script
├── asylum_seekers.csv      # Training data
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- Git

### Local Development

#### 1. Train the Model

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train and save the model
python train_and_save_model.py
```

#### 2. Run Backend

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

#### 3. Run Frontend

```bash
cd ../refugee-insights

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📖 API

**Response:**
```json
{
  "rate": 67.3,
  "confidence": 12.4
}
```

## 🧪 Model Performance

- **Model**: XGBoost Regressor
- **RMSE**: 0.439
- **MAE**: 0.137
- **Training Samples**: ~64,000
- **Test Samples**: ~16,000

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **XGBoost** - Gradient boosting framework
- **scikit-learn** - Machine learning utilities
- **pandas** - Data manipulation
- **numpy** - Numerical computing

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components

### Deployment
- **Render** - Backend hosting
- **Vercel** - Frontend hosting

## 📝 Features

- ✅ Predict acceptance rates for asylum applications
- ✅ Calculate confidence intervals for predictions
- ✅ Support for multiple countries and procedure types
- ✅ RESTful API with automatic documentation
- ✅ Responsive web interface
- ✅ Real-time predictions

## 🔧 Environment Variables

### Backend (Render)
- `MODEL_DIR`: Path to models directory (default: `../models`)
- `CORS_ORIGINS`: Allowed frontend origins (comma-separated)
- `ALLOW_ALL_ORIGINS`: Set to `true` to allow all origins
- `PORT`: Server port (auto-set by Render)

### Frontend (Vercel)
- `VITE_API_URL`: Backend API URL

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Testing Guide](TESTING_GUIDE.md) - End-to-end testing instructions

## 🎯 Use Cases

- **Policy Analysis**: Understand historical acceptance patterns
- **Decision Support**: Assist in understanding likely outcomes
- **Research**: Analyze trends in asylum decisions
- **Education**: Demonstrate ML applications for social good

## ⚠️ Important Ethical Note

This project is an academic exploration of asylum patterns, not a deployment-ready system for actual asylum decisions. Models may inherit historical biases from training data, and predictions should never replace human judgment in asylum decisions.

## 📄 License

This project is for educational purposes. Data from UNHCR.

## 👥 Authors

- Vaarunay Kaushal
- Arihant Gupta

**MIT Manipal | Intel OneAPI Hackathon 2023**

## 🔗 Links

- **Frontend Repository**: [refugee-insights-frontend](https://github.com/iurk1702/refugee-insights-frontend)
- **Backend Repository**: [intelOneAPI_submission](https://github.com/iurk1702/intelOneAPI_submission)
- **Live Demo**: [https://refugee-insights-frontend-odpdwqv0x.vercel.app/](https://refugee-insights-frontend-odpdwqv0x.vercel.app/)

## 📞 Support

For issues or questions, please open an issue in the respective repository.

