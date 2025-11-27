"""
Prediction logic with confidence interval calculation.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from model_loader import ModelLoader

def predict_acceptance_rate(
    country: str,
    origin: str,
    procedure: str,
    model_loader: ModelLoader
) -> Tuple[float, float, Optional[str]]:
    """
    Predict acceptance rate with confidence interval.
    
    Args:
        country: Country/territory of asylum/residence
        origin: Origin country
        procedure: RSD procedure type/level
        model_loader: ModelLoader instance
        
    Returns:
        Tuple of (rate: float, confidence: float, error_message: Optional[str])
        Rate is returned as a value between 0 and 1 (will be converted to percentage in API)
        Confidence is the ± value as a percentage
    """
    if not model_loader.is_loaded():
        return 0.0, 0.0, "Models not loaded"
    
    # Encode inputs
    encoded_features, error = model_loader.encode_input(country, origin, procedure)
    if error:
        return 0.0, 0.0, error
    
    # Prepare input array
    X = np.array([encoded_features])
    
    try:
        # Get main prediction
        prediction = model_loader.model.predict(X)[0]
        
        # Clamp prediction to valid range [0, 1]
        prediction = max(0.0, min(1.0, prediction))
        
        # Calculate confidence interval
        if model_loader.model_lower is not None and model_loader.model_upper is not None:
            # Use quantile regression models
            pred_lower = model_loader.model_lower.predict(X)[0]
            pred_upper = model_loader.model_upper.predict(X)[0]
            
            # Ensure bounds are valid
            pred_lower = max(0.0, min(1.0, pred_lower))
            pred_upper = max(0.0, min(1.0, pred_upper))
            
            # Calculate confidence as half the interval width
            confidence = (pred_upper - pred_lower) / 2.0
            
        else:
            # Fallback: use statistical approach
            # Try to load residual statistics, otherwise use RMSE
            try:
                import joblib
                from pathlib import Path
                residual_stats_path = Path(__file__).parent.parent / "models" / "residual_stats.pkl"
                if residual_stats_path.exists():
                    residual_stats = joblib.load(residual_stats_path)
                    residual_std = residual_stats.get('residual_std', 0.439)
                    # Use 1.96 * std for 95% confidence interval
                    confidence = 1.96 * residual_std / 2.0
                else:
                    # Use RMSE from metadata
                    rmse = model_loader.metadata.get('rmse', 0.439)
                    confidence = 1.96 * rmse / 2.0
            except Exception:
                # Final fallback
                rmse = model_loader.metadata.get('rmse', 0.439)
                confidence = 1.96 * rmse / 2.0
        
        # Ensure confidence is reasonable (not negative, not too large)
        confidence = max(0.01, min(0.5, confidence))  # Between 1% and 50%
        
        return prediction, confidence, None
        
    except Exception as e:
        return 0.0, 0.0, f"Prediction error: {str(e)}"

