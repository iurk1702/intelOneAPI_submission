# Backend Deployment to Render - Quick Start

## Prerequisites
- GitHub repository with backend code
- Render account (free tier available)
- Trained models in `../models/` directory

## Deployment Steps

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository and branch
5. Configure:
   - **Name**: `refugee-predictor-api`
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### 3. Set Environment Variables

In Render dashboard → Environment tab:
- `PORT`: `10000` (Render sets this automatically)
- `MODEL_DIR`: `../models`
- `CORS_ORIGINS`: (Leave empty for now, update after frontend deployment)

### 4. Upload Models

**Option A: Git LFS (Recommended)**
```bash
git lfs install
git lfs track "*.pkl"
git add .gitattributes models/*.pkl
git commit -m "Add models with LFS"
git push
```

**Option B: Persistent Disk**
1. Enable Persistent Disk in Render settings
2. SSH into service
3. Upload models via scp or Render shell

**Option C: Cloud Storage**
- Upload to S3/cloud storage
- Modify code to download on startup

### 5. Get Backend URL

After deployment, note your Render URL:
```
https://your-service-name.onrender.com
```

### 6. Update CORS

Once frontend is deployed, update `CORS_ORIGINS`:
```
https://your-frontend.vercel.app
```

## Testing

```bash
# Health check
curl https://your-service.onrender.com/health

# Test prediction
curl -X POST https://your-service.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"origin":"Syria","asylum":"Germany","year":"2015","procedure":"Government"}'
```

## Troubleshooting

- **Models not loading**: Check `MODEL_DIR` path and ensure models are uploaded
- **CORS errors**: Verify `CORS_ORIGINS` includes frontend URL
- **Port errors**: Render sets `$PORT` automatically, don't hardcode

## Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Consider upgrading for production use

