"""
Data preprocessing module for seizure prediction
Loads and cleans data from CSV files
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class DataLoader:
    def __init__(self, data_folder='../Data'):
        self.data_folder = data_folder
        
    def load_seizures(self):
        """Load and preprocess seizure data"""
        df = pd.read_csv(os.path.join(self.data_folder, 'seizures.csv'))
        
        # Combine Date and Time
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        
        # Clean Duration column (remove non-numeric values)
        df['Duration'] = pd.to_numeric(df['Duration'], errors='coerce')
        
        # Convert boolean columns
        df['Peiod'] = df['Peiod'].map({'True': True, 'False': False, 'NULL': None})
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
    
    def create_hourly_dataset(self):
        """
        Create a unified hourly dataset combining all data sources
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
        
        return df, seizures

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