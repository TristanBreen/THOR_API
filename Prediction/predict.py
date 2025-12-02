"""
Prediction script for seizure forecasting
Uses trained models to predict seizure risk
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

from data_preprocessing import DataLoader
from feature_engineering import FeatureEngineer
from train_model import SeizurePredictor

class SeizureForecaster:
    def __init__(self, model_path='models'):
        self.predictor = SeizurePredictor()
        self.predictor.load_model(model_path)
        self.engineer = FeatureEngineer()
        self.loader = DataLoader()
        
    def get_current_prediction(self):
        """
        Get prediction for current time
        """
        # Load latest data
        df, seizures = self.loader.create_hourly_dataset()
        
        # Create features
        df_features = self.engineer.create_features(df)
        
        # Get the most recent hour
        latest_data = df_features.iloc[-1:]
        
        # Prepare features (same columns as training)
        exclude_cols = ['DateTime', 'seizure', 'seizure_duration']
        feature_cols = [col for col in latest_data.columns if col not in exclude_cols]
        X = latest_data[feature_cols]
        
        # Make prediction
        predictions = self.predictor.predict(X)
        
        result = {
            'timestamp': latest_data['DateTime'].iloc[0].strftime('%Y-%m-%d %H:%M:%S'),
            'seizure_probability': float(predictions['seizure_probability'][0]),
            'predicted_hours_to_seizure': float(predictions['predicted_hours_to_seizure'][0]),
            'risk_level': self._get_risk_level(predictions['seizure_probability'][0])
        }
        
        return result
    
    def get_forecast(self, hours_ahead=24):
        """
        Get forecast for next N hours
        """
        # Load latest data to get baseline features
        df, seizures = self.loader.create_hourly_dataset()
        df_features = self.engineer.create_features(df)
        
        # Create future datetime range starting from now
        now = pd.Timestamp.now().floor('H')
        future_datetimes = pd.date_range(start=now, periods=hours_ahead, freq='H')
        
        # Create a dataframe with future datetimes
        forecast_df = pd.DataFrame({'DateTime': future_datetimes})
        
        # Get the most recent hour's data as a template
        latest_data = df_features.iloc[-1:].copy()
        
        # For each future hour, we'll create a row based on the pattern
        # We'll use the average of the last 24 hours for physiological features
        last_24_data = df_features.iloc[-24:]
        
        forecast_rows = []
        for future_dt in future_datetimes:
            # Start with the latest row and update DateTime
            row = latest_data.iloc[0].copy()
            row['DateTime'] = future_dt
            
            # Update temporal features
            row['hour'] = future_dt.hour
            row['day_of_week'] = future_dt.dayofweek
            row['day_of_month'] = future_dt.day
            row['month'] = future_dt.month
            row['is_weekend'] = 1 if future_dt.dayofweek >= 5 else 0
            row['hour_sin'] = np.sin(2 * np.pi * future_dt.hour / 24)
            row['hour_cos'] = np.cos(2 * np.pi * future_dt.hour / 24)
            row['dow_sin'] = np.sin(2 * np.pi * future_dt.dayofweek / 7)
            row['dow_cos'] = np.cos(2 * np.pi * future_dt.dayofweek / 7)
            
            # Update seizure history features
            if len(seizures) > 0:
                last_seizure_time = seizures.iloc[-1]['DateTime']
                row['hours_since_last_seizure'] = (future_dt - last_seizure_time).total_seconds() / 3600
            
            # Seizure counts remain constant for the forecast
            for col in row.index:
                if 'seizures_past_' in col:
                    # These stay the same from the last known data
                    row[col] = latest_data.iloc[0][col]
            
            forecast_rows.append(row)
        
        forecast_df = pd.DataFrame(forecast_rows)
        
        # Select only the feature columns used in training
        exclude_cols = ['DateTime', 'seizure', 'seizure_duration']
        feature_cols = [col for col in df_features.columns if col not in exclude_cols and col in forecast_df.columns]
        
        X = forecast_df[feature_cols].copy()
        
        # Fill any remaining NaN values
        X = X.fillna(X.mean())
        X = X.fillna(0)
        
        # Make predictions
        predictions = self.predictor.predict(X)
        
        # Create forecast dataframe
        forecast = pd.DataFrame({
            'timestamp': forecast_df['DateTime'],
            'seizure_probability': predictions['seizure_probability'],
            'predicted_hours_to_seizure': predictions['predicted_hours_to_seizure'],
            'risk_level': [self._get_risk_level(p) for p in predictions['seizure_probability']]
        })
        
        return forecast
    
    def _get_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability < 0.2:
            return 'Low'
        elif probability < 0.4:
            return 'Moderate'
        elif probability < 0.6:
            return 'Elevated'
        elif probability < 0.8:
            return 'High'
        else:
            return 'Very High'
    
    def get_summary(self):
        """
        Get comprehensive summary including recent history and predictions
        """
        # Load data
        df, seizures = self.loader.create_hourly_dataset()
        
        # Get current prediction
        current_pred = self.get_current_prediction()
        
        # Get recent seizures
        recent_seizures = seizures.tail(5).copy()
        recent_seizures['DateTime'] = recent_seizures['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate time since last seizure
        if len(seizures) > 0:
            last_seizure = seizures.iloc[-1]['DateTime']
            now = pd.Timestamp.now()
            hours_since = (now - last_seizure).total_seconds() / 3600
        else:
            hours_since = None
        
        summary = {
            'current_prediction': current_pred,
            'hours_since_last_seizure': hours_since,
            'total_seizures_recorded': len(seizures),
            'recent_seizures': recent_seizures[['DateTime', 'Duration']].to_dict('records'),
            'data_range': {
                'start': df['DateTime'].min().strftime('%Y-%m-%d'),
                'end': df['DateTime'].max().strftime('%Y-%m-%d'),
                'total_hours': len(df)
            }
        }
        
        return summary
    
    def print_summary(self):
        """Print formatted summary"""
        summary = self.get_summary()
        
        print("=" * 70)
        print("SEIZURE PREDICTION SUMMARY")
        print("=" * 70)
        
        print("\n📊 CURRENT PREDICTION")
        print("-" * 70)
        pred = summary['current_prediction']
        print(f"Timestamp: {pred['timestamp']}")
        print(f"Seizure Probability: {pred['seizure_probability']:.1%}")
        print(f"Predicted Time to Next Seizure: {pred['predicted_hours_to_seizure']:.1f} hours")
        print(f"Risk Level: {pred['risk_level']}")
        
        if pred['seizure_probability'] > 0.6:
            print("\n⚠️  HIGH RISK ALERT - Consider taking precautions")
        
        print("\n📈 RECENT HISTORY")
        print("-" * 70)
        if summary['hours_since_last_seizure']:
            days = summary['hours_since_last_seizure'] / 24
            print(f"Time Since Last Seizure: {summary['hours_since_last_seizure']:.1f} hours ({days:.1f} days)")
        print(f"Total Seizures Recorded: {summary['total_seizures_recorded']}")
        
        print("\n🕐 LAST 5 SEIZURES")
        print("-" * 70)
        for i, seizure in enumerate(summary['recent_seizures'][-5:], 1):
            print(f"{i}. {seizure['DateTime']} - Duration: {seizure['Duration']} seconds")
        
        print("\n📁 DATA COVERAGE")
        print("-" * 70)
        print(f"Date Range: {summary['data_range']['start']} to {summary['data_range']['end']}")
        print(f"Total Hours: {summary['data_range']['total_hours']}")
        
        print("\n" + "=" * 70)

def main():
    """Example usage"""
    forecaster = SeizureForecaster()
    
    # Print summary
    forecaster.print_summary()
    
    # Get 24-hour forecast
    print("\n📅 24-HOUR FORECAST")
    print("-" * 70)
    forecast = forecaster.get_forecast(hours_ahead=24)
    
    # Show high-risk periods
    high_risk = forecast[forecast['seizure_probability'] > 0.5]
    if len(high_risk) > 0:
        print("\n⚠️  High Risk Periods (>50% probability):")
        for _, row in high_risk.iterrows():
            print(f"  {row['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
                  f"Risk: {row['seizure_probability']:.1%} ({row['risk_level']})")
    else:
        print("\n✅ No high-risk periods detected in next 24 hours")
    
    return forecaster

if __name__ == "__main__":
    forecaster = main()