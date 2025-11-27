"""
Script to train and save the XGBoost model for the refugee acceptance rate predictor.
This extracts the model training logic from the notebook and saves it for deployment.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import xgboost as xgb
import joblib
import os
from datetime import datetime

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

print("Loading data...")
# Load data
path = "asylum_seekers.csv"
data = pd.read_csv(path, low_memory=False)

print("Preprocessing data...")
# Convert numeric columns
cols_to_convert = ['Tota pending start-year', 'Applied during year', 'decisions_recognized', 'decisions_other', 'Rejected']
for col in cols_to_convert:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# Feature engineering
data['E+G'] = data['Tota pending start-year'] + data['Applied during year']
data['acceptance_rate'] = data['decisions_recognized'] / data['E+G']
data['decision_pending_rate'] = data['decisions_other'] / data['E+G']
data['rejection_rate'] = data['Rejected'] / data['E+G']

# Clean data
data_cleaned = data.dropna()
data_cleaned = data_cleaned.replace([np.inf, -np.inf], np.nan).dropna(axis=0)

print("Encoding categorical features...")
# Create label encoders for each categorical feature
label_encoder_country = LabelEncoder()
label_encoder_origin = LabelEncoder()
label_encoder_procedure = LabelEncoder()

# Fit and transform
data_cleaned['Country / territory of asylum/residence encoded'] = label_encoder_country.fit_transform(
    data_cleaned['Country / territory of asylum/residence']
)
data_cleaned['Origin encoded'] = label_encoder_origin.fit_transform(data_cleaned['Origin'])
data_cleaned['RSD procedure type / level encoded'] = label_encoder_procedure.fit_transform(
    data_cleaned['RSD procedure type / level']
)

# Prepare features and target
selected_columns = [
    'Country / territory of asylum/residence encoded',
    'Origin encoded',
    'RSD procedure type / level encoded'
]
x = data_cleaned[selected_columns]
y = data_cleaned['acceptance_rate']

print(f"Data shape: {x.shape}, Target shape: {y.shape}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

print("Training XGBoost model...")
# Train XGBoost model
model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)

print(f"Model Performance:")
print(f"RMSE: {rmse:.6f}")
print(f"MAE: {mae:.6f}")

# Train quantile models for confidence intervals
# XGBoost supports quantile regression through the 'reg:quantileerror' objective
# If not available, we'll use a statistical approach based on residuals
print("Training quantile regression models for confidence intervals...")
try:
    # Try to use quantile regression (available in XGBoost 1.6+)
    model_lower = xgb.XGBRegressor(objective='reg:quantileerror', quantile_alpha=0.05, random_state=42)
    model_upper = xgb.XGBRegressor(objective='reg:quantileerror', quantile_alpha=0.95, random_state=42)
    
    model_lower.fit(X_train, y_train)
    model_upper.fit(X_train, y_train)
    
    # Evaluate quantile models
    y_pred_lower = model_lower.predict(X_test)
    y_pred_upper = model_upper.predict(X_test)
    print("Quantile regression models trained successfully.")
except Exception as e:
    print(f"Quantile regression not available ({str(e)}), using statistical approach.")
    # Fallback: calculate confidence based on residuals
    y_train_pred = model.predict(X_train)
    residuals = y_train - y_train_pred
    residual_std = np.std(residuals)
    
    # Create dummy models that will use statistical confidence
    model_lower = None
    model_upper = None

print("Saving models and encoders...")
# Save models
joblib.dump(model, 'models/xgboost_model.pkl')
if model_lower is not None and model_upper is not None:
    joblib.dump(model_lower, 'models/xgboost_model_lower.pkl')
    joblib.dump(model_upper, 'models/xgboost_model_upper.pkl')
else:
    # Save residual statistics for statistical confidence calculation
    residual_stats = {
        'residual_std': float(residual_std) if 'residual_std' in locals() else rmse,
        'mean_residual': float(np.mean(residuals)) if 'residuals' in locals() else 0.0
    }
    joblib.dump(residual_stats, 'models/residual_stats.pkl')

# Save encoders
encoders = {
    'country': label_encoder_country,
    'origin': label_encoder_origin,
    'procedure': label_encoder_procedure
}
joblib.dump(encoders, 'models/label_encoders.pkl')

# Save model metadata
metadata = {
    'rmse': float(rmse),
    'mae': float(mae),
    'training_date': datetime.now().isoformat(),
    'feature_names': selected_columns,
    'n_samples_train': len(X_train),
    'n_samples_test': len(X_test),
    'model_type': 'XGBoost',
    'objective': 'reg:squarederror'
}
joblib.dump(metadata, 'models/model_metadata.pkl')

print("Models saved successfully!")
print(f"Model files saved in: {os.path.abspath('models')}")
print(f"\nModel Metadata:")
print(f"  RMSE: {rmse:.6f}")
print(f"  MAE: {mae:.6f}")
print(f"  Training samples: {len(X_train)}")
print(f"  Test samples: {len(X_test)}")

