"""
Feature engineering for seizure prediction
Creates temporal, physiological, and historical features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FeatureEngineer:
    def __init__(self):
        pass
    
    def create_features(self, df):
        """
        Create comprehensive features for seizure prediction
        """
        df = df.copy()
        
        # Temporal features
        df = self._add_temporal_features(df)
        
        # Historical seizure features
        df = self._add_seizure_history_features(df)
        
        # Physiological features
        df = self._add_physiological_features(df)
        
        # Pain features
        df = self._add_pain_features(df)
        
        # Activity features
        df = self._add_activity_features(df)
        
        # Sleep features
        df = self._add_sleep_features(df)
        
        return df
    
    def _add_temporal_features(self, df):
        """Add time-based features"""
        df['hour'] = df['DateTime'].dt.hour
        df['day_of_week'] = df['DateTime'].dt.dayofweek
        df['day_of_month'] = df['DateTime'].dt.day
        df['month'] = df['DateTime'].dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Cyclical encoding for time of day
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Cyclical encoding for day of week
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def _add_seizure_history_features(self, df):
        """Add features based on seizure history"""
        # Hours since last seizure
        df['hours_since_last_seizure'] = 0
        last_seizure_idx = None
        
        for idx, row in df.iterrows():
            if last_seizure_idx is not None:
                hours_diff = (idx - last_seizure_idx)
                df.loc[idx, 'hours_since_last_seizure'] = hours_diff
            else:
                df.loc[idx, 'hours_since_last_seizure'] = -1
                
            if row['seizure'] == 1:
                last_seizure_idx = idx
        
        # Number of seizures in past N hours
        for window in [24, 48, 72, 168]:  # 1 day, 2 days, 3 days, 1 week
            df[f'seizures_past_{window}h'] = df['seizure'].rolling(
                window=window, min_periods=1).sum()
        
        # Average time between seizures (rolling window)
        df['avg_time_between_seizures'] = df['hours_since_last_seizure'].rolling(
            window=168, min_periods=1).mean()
        
        return df
    
    def _add_physiological_features(self, df):
        """Add heart rate and physiological features"""
        hr_cols = ['Heart Rate [Min] (count/min)', 
                   'Heart Rate [Max] (count/min)', 
                   'Heart Rate [Avg] (count/min)']
        
        for col in hr_cols:
            if col in df.columns:
                # Rolling statistics
                for window in [6, 12, 24]:  # 6h, 12h, 24h
                    df[f'{col}_rolling_mean_{window}h'] = df[col].rolling(
                        window=window, min_periods=1).mean()
                    df[f'{col}_rolling_std_{window}h'] = df[col].rolling(
                        window=window, min_periods=1).std()
        
        # Heart rate variability proxy
        if 'Heart Rate [Max] (count/min)' in df.columns and 'Heart Rate [Min] (count/min)' in df.columns:
            df['hr_range'] = df['Heart Rate [Max] (count/min)'] - df['Heart Rate [Min] (count/min)']
            df['hr_range_rolling_mean_12h'] = df['hr_range'].rolling(
                window=12, min_periods=1).mean()
        
        return df
    
    def _add_pain_features(self, df):
        """Add pain-related features"""
        if 'Pain' in df.columns:
            # Rolling pain statistics
            for window in [6, 12, 24, 48]:
                df[f'pain_rolling_mean_{window}h'] = df['Pain'].rolling(
                    window=window, min_periods=1).mean()
                df[f'pain_rolling_max_{window}h'] = df['Pain'].rolling(
                    window=window, min_periods=1).max()
            
            # Pain change rate
            df['pain_change'] = df['Pain'].diff()
            df['pain_increasing'] = (df['pain_change'] > 0).astype(int)
        
        return df
    
    def _add_activity_features(self, df):
        """Add activity/movement features"""
        if 'Walking + Running Distance (mi)' in df.columns:
            dist_col = 'Walking + Running Distance (mi)'
            
            # Rolling activity statistics
            for window in [6, 12, 24]:
                df[f'activity_sum_{window}h'] = df[dist_col].rolling(
                    window=window, min_periods=1).sum()
                df[f'activity_mean_{window}h'] = df[dist_col].rolling(
                    window=window, min_periods=1).mean()
            
            # Activity change
            df['activity_change'] = df[dist_col].diff()
        
        return df
    
    def _add_sleep_features(self, df):
        """Add sleep-related features"""
        sleep_cols = ['Sleep Analysis [Total] (hr)', 
                     'Sleep Analysis [Deep] (hr)',
                     'Sleep Analysis [REM] (hr)',
                     'Sleep Analysis [Awake] (hr)']
        
        for col in sleep_cols:
            if col in df.columns:
                # Most recent sleep data (forward fill up to 24 hours)
                df[f'{col}_recent'] = df[col].fillna(method='ffill', limit=24)
                
                # Rolling average of sleep
                df[f'{col}_7day_avg'] = df[col].rolling(
                    window=168, min_periods=1).mean()
        
        # Sleep quality indicators
        if 'Sleep Analysis [Total] (hr)' in df.columns and 'Sleep Analysis [Deep] (hr)' in df.columns:
            df['deep_sleep_ratio'] = df['Sleep Analysis [Deep] (hr)'] / (
                df['Sleep Analysis [Total] (hr)'] + 0.01)  # Avoid division by zero
        
        return df
    
    def prepare_training_data(self, df, prediction_horizon=6):
        """
        Prepare data for model training
        
        Args:
            df: DataFrame with features
            prediction_horizon: Hours ahead to predict (default 6)
        
        Returns:
            X: Feature matrix
            y_classification: Binary target (seizure in next N hours)
            y_regression: Hours until next seizure
        """
        df = df.copy()
        
        # Create target variables
        # Classification: Will there be a seizure in the next prediction_horizon hours?
        df['target_seizure'] = 0
        for i in range(len(df)):
            future_seizures = df.iloc[i:i+prediction_horizon]['seizure'].sum()
            df.loc[df.index[i], 'target_seizure'] = 1 if future_seizures > 0 else 0
        
        # Regression: Hours until next seizure
        df['target_hours_to_seizure'] = prediction_horizon + 1
        for i in range(len(df)):
            for j in range(i+1, min(i+prediction_horizon+1, len(df))):
                if df.iloc[j]['seizure'] == 1:
                    df.loc[df.index[i], 'target_hours_to_seizure'] = j - i
                    break
        
        # Remove rows where we can't predict (too close to end of data)
        df = df.iloc[:-prediction_horizon]
        
        # Select features (exclude targets, datetime, and raw identifiers)
        exclude_cols = ['DateTime', 'seizure', 'seizure_duration', 
                       'target_seizure', 'target_hours_to_seizure']
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols]
        y_classification = df['target_seizure']
        y_regression = df['target_hours_to_seizure']
        
        return X, y_classification, y_regression, feature_cols

if __name__ == "__main__":
    from data_preprocessing import DataLoader
    
    # Test feature engineering
    loader = DataLoader()
    df, _ = loader.create_hourly_dataset()
    
    engineer = FeatureEngineer()
    df_features = engineer.create_features(df)
    
    print("Features created:", df_features.shape[1])
    print("\nFeature columns:")
    print(df_features.columns.tolist())
    
    X, y_class, y_reg, feature_cols = engineer.prepare_training_data(df_features)
    print(f"\nTraining data shape: {X.shape}")
    print(f"Seizure events to predict: {y_class.sum()}")