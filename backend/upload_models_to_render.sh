#!/bin/bash
# Script to upload models to Render service
# Usage: ./upload_models_to_render.sh <render-service-url>

if [ -z "$1" ]; then
    echo "Usage: ./upload_models_to_render.sh <render-service-url>"
    echo "Example: ./upload_models_to_render.sh https://refugee-predictor-api.onrender.com"
    exit 1
fi

RENDER_URL=$1
MODELS_DIR="../models"

echo "Uploading models to Render..."
echo "Service URL: $RENDER_URL"
echo "Models directory: $MODELS_DIR"

# Check if models directory exists
if [ ! -d "$MODELS_DIR" ]; then
    echo "Error: Models directory not found at $MODELS_DIR"
    exit 1
fi

# Note: Render doesn't support direct file upload via script
# You'll need to use one of these methods:
echo ""
echo "Render doesn't support direct file upload via script."
echo "Please use one of these methods:"
echo ""
echo "Method 1: Use Render's Persistent Disk"
echo "  1. Enable Persistent Disk in Render dashboard"
echo "  2. SSH into your service"
echo "  3. Use scp to upload files:"
echo "     scp -r $MODELS_DIR/* user@your-service.onrender.com:/opt/render/project/src/models/"
echo ""
echo "Method 2: Use Git LFS"
echo "  1. Install Git LFS: git lfs install"
echo "  2. Track .pkl files: git lfs track '*.pkl'"
echo "  3. Add and commit: git add .gitattributes models/*.pkl && git commit -m 'Add models'"
echo "  4. Push: git push"
echo ""
echo "Method 3: Store in cloud storage (S3, etc.)"
echo "  - Upload models to S3/cloud storage"
echo "  - Modify model_loader.py to download on startup"
echo ""

