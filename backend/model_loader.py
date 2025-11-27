"""
Model loading utilities with singleton pattern for performance.
Loads models and encoders once at startup.
"""

import joblib
import os
from typing import Dict, Optional, Tuple
from pathlib import Path

class ModelLoader:
    """Singleton class to load and manage models."""
    
    _instance = None
    _models_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._models_loaded:
            self.model = None
            self.model_lower = None
            self.model_upper = None
            self.encoders = None
            self.metadata = None
            self._models_loaded = True
    
    def load_models(self, model_dir: str = "../models") -> Tuple[bool, Optional[str]]:
        """
        Load all models and encoders from disk.
        
        Args:
            model_dir: Directory containing model files (relative to backend directory)
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            # Resolve path: backend/model_loader.py -> backend/ -> parent (intelOneAPI_submission) -> models/
            if model_dir.startswith("../"):
                # Relative path from backend directory - strip "../" and use "models"
                model_dir_path = Path(__file__).parent.parent / "models"
            elif os.path.isabs(model_dir):
                # Absolute path
                model_dir_path = Path(model_dir)
            else:
                # Relative path - resolve from backend directory
                model_dir_path = (Path(__file__).parent / model_dir).resolve()
            
            # Load main model
            model_path = model_dir_path / "xgboost_model.pkl"
            if not model_path.exists():
                return False, f"Model file not found: {model_path}"
            self.model = joblib.load(model_path)
            
            # Load quantile models for confidence intervals (if available)
            model_lower_path = model_dir_path / "xgboost_model_lower.pkl"
            model_upper_path = model_dir_path / "xgboost_model_upper.pkl"
            
            if model_lower_path.exists() and model_upper_path.exists():
                try:
                    self.model_lower = joblib.load(model_lower_path)
                    self.model_upper = joblib.load(model_upper_path)
                except Exception as e:
                    print(f"Warning: Could not load quantile models: {e}")
                    self.model_lower = None
                    self.model_upper = None
            else:
                # Fallback: use statistical confidence
                self.model_lower = None
                self.model_upper = None
            
            # Load encoders
            encoders_path = model_dir_path / "label_encoders.pkl"
            if not encoders_path.exists():
                return False, f"Encoders file not found: {encoders_path}"
            self.encoders = joblib.load(encoders_path)
            
            # Load metadata
            metadata_path = model_dir_path / "model_metadata.pkl"
            if metadata_path.exists():
                self.metadata = joblib.load(metadata_path)
            else:
                self.metadata = {"rmse": 0.439, "mae": 0.137}  # Default from notebook
            
            return True, None
            
        except Exception as e:
            return False, f"Error loading models: {str(e)}"
    
    def encode_input(
        self, 
        country: str, 
        origin: str, 
        procedure: str
    ) -> Tuple[Optional[list], Optional[str]]:
        """
        Encode categorical inputs using saved label encoders.
        
        Args:
            country: Country/territory of asylum/residence
            origin: Origin country
            procedure: RSD procedure type/level
            
        Returns:
            Tuple of (encoded_features: Optional[list], error_message: Optional[str])
        """
        if self.encoders is None:
            return None, "Encoders not loaded"
        
        try:
            # Encode each feature
            country_encoded = self._encode_value(
                self.encoders['country'], 
                country, 
                'country'
            )
            if country_encoded is None:
                return None, f"Unknown country: {country}"
            
            origin_encoded = self._encode_value(
                self.encoders['origin'], 
                origin, 
                'origin'
            )
            if origin_encoded is None:
                return None, f"Unknown origin: {origin}"
            
            procedure_encoded = self._encode_value(
                self.encoders['procedure'], 
                procedure, 
                'procedure'
            )
            if procedure_encoded is None:
                return None, f"Unknown procedure type: {procedure}"
            
            return [country_encoded, origin_encoded, procedure_encoded], None
            
        except Exception as e:
            return None, f"Encoding error: {str(e)}"
    
    def _get_country_mapping(self) -> dict:
        """Get mapping of common country name variations to encoder names."""
        return {
            # Origin country mappings
            'syria': 'Syrian Arab Rep.',
            'syrian arab republic': 'Syrian Arab Rep.',
            'syrian': 'Syrian Arab Rep.',
            # Add more mappings as needed
        }
    
    def _get_procedure_mapping(self) -> dict:
        """Get mapping of procedure type names to encoder names."""
        # The encoder uses codes like "G / AR", "J / FA", "U / AR"
        # G = Government, J = Joint, U = UNHCR
        # We'll use common codes as defaults
        return {
            'government': 'G / AR',  # Government - most common
            'unhcr': 'U / AR',      # UNHCR - most common
            'joint': 'J / AR',      # Joint - most common
            'unknown': 'U / AR',    # Default to UNHCR if unknown
        }
    
    def _encode_value(self, encoder: object, value: str, feature_name: str) -> Optional[int]:
        """Encode a single value, handling unknown values."""
        try:
            # Check if value is in encoder classes
            if hasattr(encoder, 'classes_'):
                original_value = value
                
                # First, try exact match
                if value in encoder.classes_:
                    return encoder.transform([value])[0]
                
                # Try case-insensitive match
                value_lower = value.lower()
                matching_classes = [c for c in encoder.classes_ if str(c).lower() == value_lower]
                if matching_classes:
                    return encoder.transform([matching_classes[0]])[0]
                
                # Try country name mapping (for origin/country features)
                if feature_name in ['origin', 'country']:
                    mapping = self._get_country_mapping()
                    if value_lower in mapping:
                        mapped_value = mapping[value_lower]
                        if mapped_value in encoder.classes_:
                            return encoder.transform([mapped_value])[0]
                
                # Try procedure type mapping
                if feature_name == 'procedure':
                    mapping = self._get_procedure_mapping()
                    if value_lower in mapping:
                        mapped_value = mapping[value_lower]
                        if mapped_value in encoder.classes_:
                            return encoder.transform([mapped_value])[0]
                
                # Try partial match (contains)
                matching_classes = [c for c in encoder.classes_ if value_lower in str(c).lower() or str(c).lower() in value_lower]
                if matching_classes:
                    # Prefer exact substring match
                    exact_match = [c for c in matching_classes if value_lower == str(c).lower()[:len(value_lower)]]
                    if exact_match:
                        return encoder.transform([exact_match[0]])[0]
                    return encoder.transform([matching_classes[0]])[0]
                
                return None
            return encoder.transform([value])[0]
        except Exception:
            return None
    
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self.model is not None and self.encoders is not None

