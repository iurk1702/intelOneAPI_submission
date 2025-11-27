# Complete Testing Guide - End-to-End Flow

This guide walks you through testing the entire system from model training to frontend prediction.

## Prerequisites Check

1. ✅ Training virtual environment created (`intelOneAPI_submission/venv/`)
2. ✅ Backend virtual environment created (`backend/venv/`)
3. ✅ `asylum_seekers.csv` file exists in `intelOneAPI_submission/`
4. ✅ Frontend code exists in `refugee-insights/`

---

## Step 1: Train the Model

**In Terminal Window 1 (or your main terminal):**

```bash
# Navigate to project root
cd /Users/vaarunaykaushal/Documents/iurk1702/intelOneAPI_submission

# Activate training environment
source venv/bin/activate

# Train and save the model
python train_and_save_model.py
```

**Expected Output:**
- Data loading messages
- Preprocessing messages
- "Training XGBoost model..."
- Model performance metrics (RMSE, MAE)
- "Models saved successfully!"
- Models saved to `models/` directory

**Verify models were created:**
```bash
ls -la models/
# Should see:
# - xgboost_model.pkl
# - label_encoders.pkl
# - model_metadata.pkl
# - (possibly) xgboost_model_lower.pkl, xgboost_model_upper.pkl, or residual_stats.pkl
```

**Deactivate when done:**
```bash
deactivate
```

---

## Step 2: Start the Backend Server

**In Terminal Window 1 (or a new terminal):**

```bash
# Navigate to backend directory
cd /Users/vaarunaykaushal/Documents/iurk1702/intelOneAPI_submission/backend

# Activate backend environment
source venv/bin/activate

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: ['/Users/.../backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using WatchFiles
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test the backend is working:**
Open a new terminal and run:
```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","models_loaded":true}
```

**Keep this terminal running!** The server needs to stay active.

---

## Step 3: Start the Frontend

**In a NEW Cursor Window (or Terminal Window 2):**

```bash
# Navigate to frontend directory
cd /Users/vaarunaykaushal/Documents/iurk1702/refugee-insights

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**The frontend will automatically open in your browser at `http://localhost:5173`**

---

## Step 4: Test a Prediction

### Option A: Using the Frontend UI

1. **Open your browser** to `http://localhost:5173`
2. **Scroll down** to the "Predict Acceptance Rate" section
3. **Fill in the form:**
   - **Origin Country:** Select "Syria" (or any from dropdown)
   - **Asylum Country:** Select "Germany" (or any from dropdown)
   - **Year:** Select "2015" (or any year 2000-2016)
   - **Procedure Type:** Select "Government" (or UNHCR/Joint)
4. **Click "Predict Acceptance Rate"**
5. **Wait for the result** - you should see:
   - A percentage rate (e.g., "67.3%")
   - Confidence interval (e.g., "±12.4%")
   - Interpretation badge (High/Moderate/Low Likelihood)

### Option B: Using curl (for quick testing)

**In a new terminal:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Syria",
    "asylum": "Germany",
    "year": "2015",
    "procedure": "Government"
  }'
```

**Expected Response:**
```json
{
  "rate": 67.3,
  "confidence": 12.4
}
```

### Option C: Using the API Documentation

1. **Open** `http://localhost:8000/docs` in your browser
2. **Click** on `POST /predict`
3. **Click** "Try it out"
4. **Fill in** the request body:
   ```json
   {
     "origin": "Syria",
     "asylum": "Germany",
     "year": "2015",
     "procedure": "Government"
   }
   ```
5. **Click** "Execute"
6. **View** the response

---

## Troubleshooting

### Backend Issues

**Error: "Models not loaded"**
- Make sure you ran `train_and_save_model.py` first
- Check that `models/` directory exists with `.pkl` files
- Verify the `MODEL_DIR` path in backend is correct (default: `../models`)

**Error: "Unknown country"**
- The model only supports countries that were in the training data
- Try using countries from the frontend dropdown
- Check backend logs for the exact error message

**CORS Errors**
- Make sure backend is running on port 8000
- Frontend should be on port 5173 (Vite default)
- Check `CORS_ORIGINS` in backend `.env` if you created one

### Frontend Issues

**API call fails**
- Verify backend is running: `curl http://localhost:8000/health`
- Check browser console (F12) for error messages
- Verify `VITE_API_URL` is set correctly (defaults to `http://localhost:8000`)

**No response from API**
- Check backend terminal for error logs
- Verify the request format matches the API schema
- Check network tab in browser DevTools

### Model Issues

**Model training fails**
- Ensure `asylum_seekers.csv` exists in the project root
- Check that you have enough disk space
- Verify all dependencies are installed in training venv

---

## Quick Test Checklist

- [ ] Model trained successfully (`models/` directory has files)
- [ ] Backend server running (`http://localhost:8000/health` returns OK)
- [ ] Frontend running (`http://localhost:5173` loads)
- [ ] Can make a prediction through frontend UI
- [ ] Prediction shows rate and confidence
- [ ] API documentation accessible (`http://localhost:8000/docs`)

---

## Example Test Cases

Try these combinations to test different scenarios:

1. **High likelihood scenario:**
   - Origin: Syria
   - Asylum: Germany
   - Year: 2015
   - Procedure: Government

2. **Different procedure type:**
   - Origin: Afghanistan
   - Asylum: United States
   - Year: 2016
   - Procedure: UNHCR

3. **Different country pair:**
   - Origin: Iraq
   - Asylum: Turkey
   - Year: 2014
   - Procedure: Joint

---

## Stopping Services

**To stop the backend:**
- Press `Ctrl+C` in the backend terminal

**To stop the frontend:**
- Press `Ctrl+C` in the frontend terminal

**To deactivate virtual environments:**
```bash
deactivate
```

---

## Next Steps

Once everything is working:
1. ✅ Test with various country combinations
2. ✅ Verify confidence intervals are reasonable
3. ✅ Check that error handling works (try invalid inputs)
4. ✅ Test the frontend with different scenarios
5. ✅ Review the API documentation at `/docs`

Happy testing! 🚀

