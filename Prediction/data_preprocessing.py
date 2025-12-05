"""
Data preprocessing module for seizure prediction
Loads and cleans data from CSV files
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Resolve data directory paths
SERVER_BASE_PATH = "/home/tristan/API/API_Repoed/THOR_API"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

# Determine which base path to use (check in priority order)
if os.path.exists(os.path.join(SERVER_BASE_PATH, "Data")):
    BASE_DATA_DIR = os.path.join(SERVER_BASE_PATH, "Data")
elif os.path.exists('/data/Data'):
    BASE_DATA_DIR = '/data/Data'
elif os.path.exists(os.path.join(PARENT_DIR, "Data")):
    BASE_DATA_DIR = os.path.join(PARENT_DIR, "Data")
else:
    BASE_DATA_DIR = os.path.join(PARENT_DIR, "Data")
    os.makedirs(BASE_DATA_DIR, exist_ok=True)

class DataLoader:
    def __init__(self, data_folder=None):
        if data_folder is None:
            self.data_folder = BASE_DATA_DIR
        else:
            self.data_folder = data_folder
        
    def load_seizures(self):
        """Load and preprocess seizure data"""
        df = pd.read_csv(os.path.join(self.data_folder, 'seizures.csv'))
        
        # Combine Date and Time
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        
        # Clean Duration column (remove non-numeric values)
        df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')
        
        # Convert boolean columns
        df['Period'] = df['Period'].map({'True': True, 'False': False, 'NULL': None})
        df['Eaten'] = df['Eaten'].map({'True': True, 'False': False, 'NULL': None})
        
        # Fill Food Eaten nulls
        df['Food Eaten'] = df['Food Eaten'].fillna('')
        
        df = df.sort_values('DateTime').reset_index(drop=True)
        return df
    
    def load_apple_watch_data(self):
        """Load and preprocess Apple Watch data"""
        df = pd.read_csv(os.path.join(self.data_folder, 'appleWatchData.csv'))
        
        # Parse datetime
        df['DateTime'] = pd.to_datetime(df['Date/Time'])
        
        # Drop original date column
        df = df.drop('Date/Time', axis=1)
        
        # Clean numeric columns
        numeric_cols = ['Heart Rate [Min] (count/min)', 'Heart Rate [Max] (count/min)', 
                       'Heart Rate [Avg] (count/min)', 'Sleep Analysis [Total] (hr)',
                       'Sleep Analysis [Asleep] (hr)', 'Sleep Analysis [In Bed] (hr)',
                       'Sleep Analysis [Core] (hr)', 'Sleep Analysis [Deep] (hr)',
                       'Sleep Analysis [REM] (hr)', 'Sleep Analysis [Awake] (hr)',
                       'Walking + Running Distance (mi)']
        
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.sort_values('DateTime').reset_index(drop=True)
        return df
    
    def load_pain_data(self):
        """Load and preprocess pain data"""
        df = pd.read_csv(os.path.join(self.data_folder, 'pain.csv'))
        
        # Strip whitespace from column names (handles CSV formatting issues)
        df.columns = df.columns.str.strip()
        
        # Combine Date and Time
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        
        # Clean pain column
        df['Pain'] = pd.to_numeric(df['Pain'], errors='coerce')
        
        df = df.sort_values('DateTime').reset_index(drop=True)
        return df
    
    def create_hourly_dataset(self, include_feedback_features=False):
        """
        Create a unified hourly dataset combining all data sources
        
        Args:
            include_feedback_features: If True, includes prediction feedback features
        """
        # Load all data
        seizures = self.load_seizures()
        apple_watch = self.load_apple_watch_data()
        pain = self.load_pain_data()
        
        # Determine date range
        min_date = min(seizures['DateTime'].min(), 
                      apple_watch['DateTime'].min(),
                      pain['DateTime'].min())
        max_date = max(seizures['DateTime'].max(), 
                      apple_watch['DateTime'].max(),
                      pain['DateTime'].max())
        
        # Create hourly range
        date_range = pd.date_range(start=min_date.floor('H'), 
                                   end=max_date.ceil('H'), 
                                   freq='H')
        
        # Create base dataframe
        df = pd.DataFrame({'DateTime': date_range})
        
        # Add seizure indicator (1 if seizure occurred in that hour)
        df['seizure'] = 0
        for _, seizure in seizures.iterrows():
            hour = seizure['DateTime'].floor('H')
            df.loc[df['DateTime'] == hour, 'seizure'] = 1
            
        # Add seizure duration
        df['seizure_duration'] = 0
        for _, seizure in seizures.iterrows():
            hour = seizure['DateTime'].floor('H')
            df.loc[df['DateTime'] == hour, 'seizure_duration'] = seizure['Duration']
        
        # Merge Apple Watch data
        df = df.merge(apple_watch, on='DateTime', how='left')
        
        # Add pain data (forward fill within 24 hours)
        pain_hourly = pain.copy()
        pain_hourly['DateTime'] = pain_hourly['DateTime'].dt.floor('H')
        df = df.merge(pain_hourly[['DateTime', 'Pain']], on='DateTime', how='left')
        
        # Forward fill pain data (last observation carried forward, max 24 hours)
        df['Pain'] = df['Pain'].fillna(method='ffill', limit=24)
        
        # Add prediction feedback features if requested
        if include_feedback_features:
            df = self._add_prediction_feedback_features(df, seizures)
        
        return df, seizures
    
    def _add_prediction_feedback_features(self, df, seizures):
        """
        Add features based on prediction history and accuracy
        This helps the model learn from its own past predictions
        """
        try:
            from prediction_feedback import PredictionFeedback
            
            feedback = PredictionFeedback(data_folder=self.data_folder)
            feedback.load_predictions()
            feedback.load_seizures()
            
            # Get prediction feedback features
            pred_features = feedback.create_prediction_features()
            
            if len(pred_features) > 0:
                # Merge feedback features on nearest timestamp
                pred_features = pred_features.rename(columns={'DateTime': 'PredDateTime'})
                
                # For each hour in df, find the nearest prediction
                for col in ['recent_pred_24h_avg', 'recent_pred_24h_std', 
                           'recent_pred_48h_avg', 'recent_pred_48h_std',
                           'prediction_trend_24h', 'recent_prediction_variance',
                           'hours_since_last_prediction', 'confidence_spike']:
                    df[col] = np.nan
                
                for idx, pred_row in pred_features.iterrows():
                    pred_time = pred_row['PredDateTime']
                    # Find closest hour in df
                    closest_idx = (df['DateTime'] - pred_time).abs().argmin()
                    
                    for col in pred_features.columns:
                        if col != 'PredDateTime' and pd.notna(pred_row[col]):
                            df.loc[closest_idx, col] = pred_row[col]
                
                # Forward fill these features (they apply to all hours following the prediction)
                for col in ['recent_pred_24h_avg', 'recent_pred_24h_std', 
                           'recent_pred_48h_avg', 'recent_pred_48h_std']:
                    df[col] = df[col].fillna(method='ffill', limit=24)
                
                print("[OK] Added prediction feedback features")
        
        except ImportError:
            print("[WARNING] Could not import prediction_feedback (this is optional)")
        except Exception as e:
            print(f"[WARNING] Error adding feedback features: {e}")
        
        return df

if __name__ == "__main__":
    # Test the data loader
    loader = DataLoader()
    df, seizures = loader.create_hourly_dataset()
    print("Hourly dataset shape:", df.shape)
    print("\nFirst few rows:")
    print(df.head())
    print("\nSeizure statistics:")
    print(f"Total seizures: {seizures.shape[0]}")
    print(f"Hours with seizures: {df['seizure'].sum()}")