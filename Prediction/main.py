"""
PRODUCTION-GRADE MULTIMODAL TIME-SERIES SEIZURE FORECASTER
Author: AI Assistant
Date: 2025-12-06

This system integrates Apple Watch sensor data, pain reports, and seizure logs
to generate probabilistic seizure forecasts for 24h, 48h, and 72h horizons.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import pickle
import warnings
from typing import Tuple, Dict, List
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support
from scipy import stats

warnings.filterwarnings('ignore')

# ============================================================================
# PATH CONFIGURATION
# ============================================================================
SERVER_BASE_PATH = "/home/tristan/API/API_Repoed/THOR_API"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data")):
    BASE_DATA_DIR = os.path.join(SERVER_BASE_PATH, "Data")
elif os.path.exists('/data/Data'):
    BASE_DATA_DIR = '/data/Data'
elif os.path.exists(os.path.join(PARENT_DIR, "Data")):
    BASE_DATA_DIR = os.path.join(PARENT_DIR, "Data")
else:
    BASE_DATA_DIR = os.path.join(PARENT_DIR, "Data")
    os.makedirs(BASE_DATA_DIR, exist_ok=True)

MODEL_DIR = os.path.join(SCRIPT_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================================
# CLASS 1: DataLoader - Data Ingestion and Harmonization
# ============================================================================
class DataLoader:
    """
    Responsible for data ingestion, cleaning, and harmonization to unified hourly index.
    """
    
    def __init__(self, data_folder: str = BASE_DATA_DIR):
        self.data_folder = data_folder
        self.apple_watch_path = os.path.join(data_folder, 'appleWatchData.csv')
        self.pain_path = os.path.join(data_folder, 'pain.csv')
        self.seizures_path = os.path.join(data_folder, 'seizures.csv')
        self.predictions_path = os.path.join(data_folder, 'longTermPredictions.json')
        
    def load_and_harmonize(self, include_feedback: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load all data sources and create unified hourly dataset.
        
        Returns:
            Tuple of (hourly_dataframe, seizures_dataframe)
        """
        print("=" * 70)
        print("DATA LOADING & HARMONIZATION")
        print("=" * 70)
        
        # Load raw data
        print("\n[1/5] Loading Apple Watch data...")
        apple_watch = self._load_apple_watch()
        print(f"        Loaded {len(apple_watch)} hourly records")
        
        print("[2/5] Loading pain data...")
        pain = self._load_pain()
        print(f"        Loaded {len(pain)} pain reports")
        
        print("[3/5] Loading seizure data...")
        seizures = self._load_seizures()
        print(f"        Loaded {len(seizures)} seizure events")
        
        # Determine global time range
        print("[4/5] Creating master hourly index...")
        min_date = min(apple_watch['DateTime'].min(), pain['DateTime'].min(), 
                      seizures['DateTime'].min())
        max_date = max(apple_watch['DateTime'].max(), pain['DateTime'].max(), 
                      seizures['DateTime'].max())
        
        hourly_index = pd.date_range(
            start=min_date.floor('H'),
            end=max_date.ceil('H'),
            freq='H'
        )
        
        df = pd.DataFrame({'DateTime': hourly_index})
        print(f"        Created {len(df)} hour index from {min_date.date()} to {max_date.date()}")
        
        # Merge data sources
        print("[5/5] Integrating multimodal data...")
        df = self._merge_apple_watch(df, apple_watch)
        df = self._merge_pain(df, pain)
        df = self._merge_seizures(df, seizures)
        
        if include_feedback:
            df = self._merge_predictions_feedback(df)
        
        print(f"        Final dataset: {len(df)} hours × {len(df.columns)} features")
        print("=" * 70)
        
        return df, seizures
    
    def _load_apple_watch(self) -> pd.DataFrame:
        """Load and clean Apple Watch sensor data."""
        df = pd.read_csv(self.apple_watch_path)
        df['DateTime'] = pd.to_datetime(df['Date/Time'])
        df = df.drop('Date/Time', axis=1)
        
        # Clean numeric columns
        numeric_cols = [
            'Heart Rate [Min] (count/min)', 'Heart Rate [Max] (count/min)',
            'Heart Rate [Avg] (count/min)', 'Sleep Analysis [Total] (hr)',
            'Sleep Analysis [Asleep] (hr)', 'Sleep Analysis [In Bed] (hr)',
            'Sleep Analysis [Core] (hr)', 'Sleep Analysis [Deep] (hr)',
            'Sleep Analysis [REM] (hr)', 'Sleep Analysis [Awake] (hr)',
            'Walking + Running Distance (mi)'
        ]
        
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.sort_values('DateTime').reset_index(drop=True)
    
    def _load_pain(self) -> pd.DataFrame:
        """Load and clean pain report data."""
        df = pd.read_csv(self.pain_path)
        df.columns = df.columns.str.strip()
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df['Pain'] = pd.to_numeric(df['Pain'], errors='coerce')
        
        return df[['DateTime', 'Pain']].sort_values('DateTime').reset_index(drop=True)
    
    def _load_seizures(self) -> pd.DataFrame:
        """Load and clean seizure event data."""
        df = pd.read_csv(self.seizures_path)
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')
        
        # Clean boolean columns
        df['Peiod'] = df['Peiod'].map({'True': True, 'False': False, 'NULL': None})
        df['Eaten'] = df['Eaten'].map({'True': True, 'False': False, 'NULL': None})
        
        return df.sort_values('DateTime').reset_index(drop=True)
    
    def _merge_apple_watch(self, df: pd.DataFrame, apple_watch: pd.DataFrame) -> pd.DataFrame:
        """Merge Apple Watch data via left join."""
        return df.merge(apple_watch, on='DateTime', how='left')
    
    def _merge_pain(self, df: pd.DataFrame, pain: pd.DataFrame) -> pd.DataFrame:
        """
        Merge pain data with Forward-Fill limited to 24 hours.
        Also track Pain_Report_Age for bias mitigation.
        """
        # Map pain to nearest hour
        pain['DateTime'] = pain['DateTime'].dt.floor('H')
        
        # Track original pain observation timestamps
        df = df.merge(pain, on='DateTime', how='left')
        
        # Create Pain_Report_Age_Hours before FFILL
        last_pain_time = None
        pain_ages = []
        
        for idx, row in df.iterrows():
            if pd.notna(row['Pain']):
                last_pain_time = row['DateTime']
                pain_ages.append(0.0)
            elif last_pain_time is not None:
                hours_since = (row['DateTime'] - last_pain_time).total_seconds() / 3600
                pain_ages.append(hours_since if hours_since <= 24 else np.nan)
            else:
                pain_ages.append(np.nan)
        
        df['Pain_Report_Age_Hours'] = pain_ages
        
        # Forward-fill pain with 24-hour limit
        df['Pain'] = df['Pain'].ffill(limit=24)
        
        return df
    
    def _merge_seizures(self, df: pd.DataFrame, seizures: pd.DataFrame) -> pd.DataFrame:
        """Map seizure events to exact hour of occurrence."""
        df['seizure'] = 0
        df['seizure_duration'] = 0.0
        
        for _, seizure in seizures.iterrows():
            hour = seizure['DateTime'].floor('H')
            mask = df['DateTime'] == hour
            df.loc[mask, 'seizure'] = 1
            if pd.notna(seizure['Duration']):
                df.loc[mask, 'seizure_duration'] = seizure['Duration']
        
        return df
    
    def _merge_predictions_feedback(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Load longTermPredictions.json and calculate 7-day rolling stats.
        Apply 24-hour FFILL limit.
        """
        try:
            if not os.path.exists(self.predictions_path):
                return df
            
            with open(self.predictions_path, 'r') as f:
                pred_data = json.load(f)
            
            if not pred_data:
                return df
            
            # Parse predictions
            pred_df = pd.DataFrame(pred_data)
            pred_df['DateTime'] = pd.to_datetime(pred_df['timestamp']).dt.floor('H')
            
            # Extract prediction values
            pred_df['pred_24h'] = pred_df['predictions'].apply(lambda x: x.get('24h', np.nan))
            pred_df['pred_48h'] = pred_df['predictions'].apply(lambda x: x.get('48h', np.nan))
            pred_df['pred_72h'] = pred_df['predictions'].apply(lambda x: x.get('72h', np.nan))
            
            # Merge with main dataframe
            df = df.merge(pred_df[['DateTime', 'pred_24h', 'pred_48h', 'pred_72h']], 
                         on='DateTime', how='left')
            
            # Calculate 7-day rolling statistics (168 hours)
            for horizon in ['24h', '48h', '72h']:
                col = f'pred_{horizon}'
                if col in df.columns:
                    df[f'{col}_7d_mean'] = df[col].rolling(window=168, min_periods=1).mean()
                    df[f'{col}_7d_std'] = df[col].rolling(window=168, min_periods=1).std()
                    
                    # Apply 24-hour FFILL limit
                    df[f'{col}_7d_mean'] = df[f'{col}_7d_mean'].ffill(limit=24)
                    df[f'{col}_7d_std'] = df[f'{col}_7d_std'].ffill(limit=24)
            
            # Drop raw prediction columns
            df = df.drop(['pred_24h', 'pred_48h', 'pred_72h'], axis=1, errors='ignore')
            
        except Exception as e:
            print(f"        Warning: Could not load prediction feedback - {e}")
        
        return df


# ============================================================================
# CLASS 2: FeatureEngineer - Complex Time-Series Feature Creation
# ============================================================================
class FeatureEngineer:
    """
    Creates comprehensive time-series features including lags, rolling statistics,
    temporal encoding, and contextual features.
    """
    
    def __init__(self):
        self.feature_names = []
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate complete feature set from raw data.
        """
        print("\n" + "=" * 70)
        print("FEATURE ENGINEERING")
        print("=" * 70)
        
        df = df.copy()
        initial_cols = len(df.columns)
        
        print("\n[1/8] Creating physiological volatility features...")
        df = self._create_volatility_features(df)
        
        print("[2/8] Calculating rolling window statistics...")
        df = self._create_rolling_features(df)
        
        print("[3/8] Applying temporal lags...")
        df = self._create_lag_features(df)
        
        print("[4/8] Engineering contextual features...")
        df = self._create_contextual_features(df)
        
        print("[5/8] Encoding cyclical time features...")
        df = self._create_temporal_encoding(df)
        
        print("[6/8] Creating target variables (Y_24, Y_48, Y_72)...")
        df = self._create_target_variables(df)
        
        print("[7/8] Handling residual missing values...")
        df = self._impute_missing_values(df)
        
        print(f"[8/8] Feature engineering complete!")
        print(f"        Created {len(df.columns) - initial_cols} new features")
        print(f"        Total features: {len(df.columns)}")
        print("=" * 70)
        
        return df
    
    def _create_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate HR volatility and physiological stress indicators."""
        if 'Heart Rate [Max] (count/min)' in df.columns and 'Heart Rate [Min] (count/min)' in df.columns:
            df['HR_Volatility'] = df['Heart Rate [Max] (count/min)'] - df['Heart Rate [Min] (count/min)']
        
        return df
    
    def _create_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate rolling statistics (mean, std, skew) for multiple windows.
        """
        windows = [4, 12, 24, 72]  # hours
        metrics = ['Heart Rate [Avg] (count/min)', 'HR_Volatility', 'Walking + Running Distance (mi)']
        
        for metric in metrics:
            if metric not in df.columns:
                continue
            
            for window in windows:
                # Mean
                df[f'{metric}_rolling_mean_{window}h'] = df[metric].rolling(
                    window=window, min_periods=1).mean()
                
                # Standard Deviation
                df[f'{metric}_rolling_std_{window}h'] = df[metric].rolling(
                    window=window, min_periods=1).std()
                
                # Skewness (requires at least 3 observations)
                df[f'{metric}_rolling_skew_{window}h'] = df[metric].rolling(
                    window=window, min_periods=3).apply(lambda x: stats.skew(x) if len(x) >= 3 else 0)
        
        return df
    
    def _create_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply aggressive time lags to primary metrics.
        Sleep metrics lagged by ~12 hours for daytime predictive influence.
        """
        lag_hours = [1, 3, 6, 12, 24]
        
        # Primary physiological metrics
        primary_metrics = [
            'Heart Rate [Avg] (count/min)', 'HR_Volatility',
            'Walking + Running Distance (mi)', 'Pain'
        ]
        
        for metric in primary_metrics:
            if metric not in df.columns:
                continue
            for lag in lag_hours:
                df[f'{metric}_lag_{lag}h'] = df[metric].shift(lag)
        
        # Sleep metrics with ~12 hour lag
        sleep_metrics = [
            'Sleep Analysis [Core] (hr)',
            'Sleep Analysis [Deep] (hr)',
            'Sleep Analysis [REM] (hr)'
        ]
        
        for metric in sleep_metrics:
            if metric not in df.columns:
                continue
            df[f'{metric}_lag_12h'] = df[metric].shift(12)
        
        return df
    
    def _create_contextual_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Hours_Since_Last_Seizure and other contextual features.
        """
        # Hours since last seizure
        df['Hours_Since_Last_Seizure'] = 0.0
        last_seizure_idx = None
        
        for idx in range(len(df)):
            if last_seizure_idx is not None:
                df.loc[idx, 'Hours_Since_Last_Seizure'] = idx - last_seizure_idx
            else:
                df.loc[idx, 'Hours_Since_Last_Seizure'] = -1  # No prior seizure
            
            if df.loc[idx, 'seizure'] == 1:
                last_seizure_idx = idx
        
        # Seizure count in recent windows
        for window in [24, 48, 72, 168]:
            df[f'seizure_count_{window}h'] = df['seizure'].rolling(
                window=window, min_periods=1).sum()
        
        return df
    
    def _create_temporal_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sine/cosine encoding for cyclical time features."""
        # Hour of day (0-23)
        df['hour'] = df['DateTime'].dt.hour
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Day of week (0-6)
        df['day_of_week'] = df['DateTime'].dt.dayofweek
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Weekend indicator
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        return df
    
    def _create_target_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create three binary target columns: Y_24, Y_48, Y_72.
        For hour t, Y_N = 1 if seizure occurs in [t+1h, t+Nh], else 0.
        """
        df['Y_24'] = 0
        df['Y_48'] = 0
        df['Y_72'] = 0
        
        for i in range(len(df)):
            # 24-hour window
            future_24 = df.iloc[i+1:i+25]['seizure'].sum() if i+1 < len(df) else 0
            df.loc[i, 'Y_24'] = 1 if future_24 > 0 else 0
            
            # 48-hour window
            future_48 = df.iloc[i+1:i+49]['seizure'].sum() if i+1 < len(df) else 0
            df.loc[i, 'Y_48'] = 1 if future_48 > 0 else 0
            
            # 72-hour window
            future_72 = df.iloc[i+1:i+73]['seizure'].sum() if i+1 < len(df) else 0
            df.loc[i, 'Y_72'] = 1 if future_72 > 0 else 0
        
        return df
    
    def _impute_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final imputation using median for production deployment."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col in ['seizure', 'seizure_duration', 'Y_24', 'Y_48', 'Y_72']:
                continue  # Don't impute targets
            
            # Use median imputation
            if df[col].isnull().any():
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val if pd.notna(median_val) else 0)
        
        return df


# ============================================================================
# CLASS 3: SeizureForecaster - Model Training, Persistence & Prediction
# ============================================================================
class SeizureForecaster:
    """
    Trains three separate GBM models for 24h, 48h, and 72h horizons.
    Handles model persistence, dynamic prediction, and risk output synthesis.
    """
    
    def __init__(self):
        self.model_24h = None
        self.model_48h = None
        self.model_72h = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        
    def train(self, df: pd.DataFrame) -> Dict:
        """
        Train three separate GBM models with class balancing.
        """
        print("\n" + "=" * 70)
        print("MODEL TRAINING")
        print("=" * 70)
        
        # Prepare features
        exclude_cols = ['DateTime', 'seizure', 'seizure_duration', 'Y_24', 'Y_48', 'Y_72']
        self.feature_columns = [col for col in df.columns if col not in exclude_cols]
        
        X = df[self.feature_columns].copy()
        
        # Remove rows with NaN targets
        valid_mask = df[['Y_24', 'Y_48', 'Y_72']].notna().all(axis=1)
        X = X[valid_mask]
        y_24 = df.loc[valid_mask, 'Y_24']
        y_48 = df.loc[valid_mask, 'Y_48']
        y_72 = df.loc[valid_mask, 'Y_72']
        
        print(f"\n[INFO] Training samples: {len(X)}")
        print(f"[INFO] Features: {len(self.feature_columns)}")
        print(f"[INFO] Y_24 positive rate: {y_24.mean():.2%}")
        print(f"[INFO] Y_48 positive rate: {y_48.mean():.2%}")
        print(f"[INFO] Y_72 positive rate: {y_72.mean():.2%}")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train three models
        print("\n[1/3] Training 24-hour model...")
        self.model_24h, metrics_24 = self._train_single_model(X_scaled, y_24)
        
        print("[2/3] Training 48-hour model...")
        self.model_48h, metrics_48 = self._train_single_model(X_scaled, y_48)
        
        print("[3/3] Training 72-hour model...")
        self.model_72h, metrics_72 = self._train_single_model(X_scaled, y_72)
        
        print("\n" + "=" * 70)
        print("TRAINING COMPLETE")
        print("=" * 70)
        
        return {
            '24h': metrics_24,
            '48h': metrics_48,
            '72h': metrics_72
        }
    
    def _train_single_model(self, X: np.ndarray, y: pd.Series) -> Tuple:
        """Train a single GBM with class balancing."""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Calculate class weights for imbalance
        neg_weight = len(y_train) / (2 * (y_train == 0).sum())
        pos_weight = len(y_train) / (2 * (y_train == 1).sum())
        sample_weights = np.where(y_train == 1, pos_weight, neg_weight)
        
        # Train Gradient Boosting Model
        model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            subsample=0.8,
            random_state=42
        )
        
        model.fit(X_train, y_train, sample_weight=sample_weights)
        
        # Evaluate
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='binary'
        )
        
        print(f"        ROC-AUC: {roc_auc:.4f} | Precision: {precision:.4f} | "
              f"Recall: {recall:.4f} | F1: {f1:.4f}")
        
        metrics = {
            'roc_auc': float(roc_auc),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1)
        }
        
        return model, metrics
    
    def save_models(self, output_dir: str = MODEL_DIR):
        """Serialize and save trained models to disk."""
        print(f"\n[SAVE] Saving models to {output_dir}/")
        
        with open(os.path.join(output_dir, 'model_24h.pkl'), 'wb') as f:
            pickle.dump(self.model_24h, f)
        
        with open(os.path.join(output_dir, 'model_48h.pkl'), 'wb') as f:
            pickle.dump(self.model_48h, f)
        
        with open(os.path.join(output_dir, 'model_72h.pkl'), 'wb') as f:
            pickle.dump(self.model_72h, f)
        
        with open(os.path.join(output_dir, 'scaler.pkl'), 'wb') as f:
            pickle.dump(self.scaler, f)
        
        with open(os.path.join(output_dir, 'feature_columns.pkl'), 'wb') as f:
            pickle.dump(self.feature_columns, f)
        
        print("[OK] Models saved successfully")
    
    def load_models(self, input_dir: str = MODEL_DIR):
        """Load trained models from disk."""
        print(f"\n[LOAD] Loading models from {input_dir}/")
        
        with open(os.path.join(input_dir, 'model_24h.pkl'), 'rb') as f:
            self.model_24h = pickle.load(f)
        
        with open(os.path.join(input_dir, 'model_48h.pkl'), 'rb') as f:
            self.model_48h = pickle.load(f)
        
        with open(os.path.join(input_dir, 'model_72h.pkl'), 'rb') as f:
            self.model_72h = pickle.load(f)
        
        with open(os.path.join(input_dir, 'scaler.pkl'), 'rb') as f:
            self.scaler = pickle.load(f)
        
        with open(os.path.join(input_dir, 'feature_columns.pkl'), 'rb') as f:
            self.feature_columns = pickle.load(f)
        
        print("[OK] Models loaded successfully")
    
    def predict(self, df: pd.DataFrame, t_run: datetime = None) -> Dict[str, float]:
        """
        Generate dynamic predictions for 72-hour window.
        Returns maximum probability for each horizon.
        """
        if t_run is None:
            t_run = df['DateTime'].max()
        
        # Filter data up to t_run
        df_historical = df[df['DateTime'] <= t_run].copy()
        
        # Generate feature set for 72-hour window starting at t_run + 1 hour
        future_hours = pd.date_range(
            start=t_run + timedelta(hours=1),
            periods=72,
            freq='H'
        )
        
        # Use last known features as template
        last_features = df_historical.iloc[-1:][self.feature_columns].copy()
        
        # Create predictions for each future hour
        predictions_24 = []
        predictions_48 = []
        predictions_72 = []
        
        for i, future_time in enumerate(future_hours):
            # Update temporal features
            features = last_features.copy()
            features['hour'] = future_time.hour
            features['hour_sin'] = np.sin(2 * np.pi * future_time.hour / 24)
            features['hour_cos'] = np.cos(2 * np.pi * future_time.hour / 24)
            features['day_of_week'] = future_time.dayofweek
            features['day_sin'] = np.sin(2 * np.pi * future_time.dayofweek / 7)
            features['day_cos'] = np.cos(2 * np.pi * future_time.dayofweek / 7)
            features['is_weekend'] = 1 if future_time.dayofweek >= 5 else 0
            
            # Update Hours_Since_Last_Seizure
            if 'Hours_Since_Last_Seizure' in features.columns:
                features['Hours_Since_Last_Seizure'] += (i + 1)
            
            # Scale and predict
            X_scaled = self.scaler.transform(features)
            
            prob_24 = self.model_24h.predict_proba(X_scaled)[0, 1]
            prob_48 = self.model_48h.predict_proba(X_scaled)[0, 1]
            prob_72 = self.model_72h.predict_proba(X_scaled)[0, 1]
            
            predictions_24.append(prob_24)
            predictions_48.append(prob_48)
            predictions_72.append(prob_72)
        
        # Extract maximum probabilities
        max_prob_24 = max(predictions_24[:24]) if len(predictions_24) >= 24 else max(predictions_24)
        max_prob_48 = max(predictions_48[:48]) if len(predictions_48) >= 48 else max(predictions_48)
        max_prob_72 = max(predictions_72)
        
        return {
            '24h': float(max_prob_24 * 100),  # Convert to percentage
            '48h': float(max_prob_48 * 100),
            '72h': float(max_prob_72 * 100)
        }


# ============================================================================
# MAIN EXECUTION PIPELINE
# ============================================================================
def main():
    """
    Main execution pipeline: Load → Engineer → Train/Load → Predict → Output
    """
    print("\n" + "=" * 70)
    print("PRODUCTION SEIZURE FORECASTING SYSTEM v1.0")
    print("=" * 70)
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Load and harmonize data
    loader = DataLoader()
    df, seizures = loader.load_and_harmonize(include_feedback=True)
    
    # Step 2: Engineer features
    engineer = FeatureEngineer()
    df_features = engineer.create_features(df)
    
    # Step 3: Train or load models
    forecaster = SeizureForecaster()
    
    model_exists = all([
        os.path.exists(os.path.join(MODEL_DIR, 'model_24h.pkl')),
        os.path.exists(os.path.join(MODEL_DIR, 'model_48h.pkl')),
        os.path.exists(os.path.join(MODEL_DIR, 'model_72h.pkl'))
    ])
    
    if not model_exists:
        print("\n[INFO] No existing models found. Training new models...")
        metrics = forecaster.train(df_features)
        forecaster.save_models()
    else:
        print("\n[INFO] Loading existing models...")
        forecaster.load_models()
    
    # Step 4: Generate predictions
    print("\n" + "=" * 70)
    print("GENERATING PREDICTIONS")
    print("=" * 70)
    
    predictions = forecaster.predict(df_features)
    
    print(f"\n[RESULT] Maximum seizure probabilities:")
    print(f"         24-hour: {predictions['24h']:.1f}%")
    print(f"         48-hour: {predictions['48h']:.1f}%")
    print(f"         72-hour: {predictions['72h']:.1f}%")
    
    # Step 5: Write outputs
    write_outputs(predictions)
    
    print("\n" + "=" * 70)
    print("EXECUTION COMPLETE")
    print("=" * 70)
    

def write_outputs(predictions: Dict[str, float]):
    """Write prediction.txt and update longTermPredictions.json"""
    
    # Write prediction.txt (overwrite)
    prediction_txt = os.path.join(BASE_DATA_DIR, "prediction.txt")
    output_text = (
        f"{predictions['24h']:.1f}% chance of seizure in the next 24 hours.\n"
        f"{predictions['48h']:.1f}% chance of seizure in the next 48 hours.\n"
        f"{predictions['72h']:.1f}% chance of seizure in the next 72 hours."
    )
    
    with open(prediction_txt, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    print(f"\n[OUTPUT] Updated {prediction_txt}")
    
    # Append to longTermPredictions.json
    predictions_json = os.path.join(BASE_DATA_DIR, "longTermPredictions.json")
    
    try:
        with open(predictions_json, 'r', encoding='utf-8') as f:
            predictions_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        predictions_list = []
    
    new_entry = {
        "timestamp": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "predictions": {
            "24h": round(predictions['24h'], 1),
            "48h": round(predictions['48h'], 1),
            "72h": round(predictions['72h'], 1)
        }
    }
    
    predictions_list.append(new_entry)
    
    with open(predictions_json, 'w', encoding='utf-8') as f:
        json.dump(predictions_list, f, indent=2, ensure_ascii=False)
    
    print(f"[OUTPUT] Appended to {predictions_json}")


if __name__ == "__main__":
    main()
