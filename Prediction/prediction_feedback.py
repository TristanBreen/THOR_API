"""
Prediction feedback and validation module
Integrates historical predictions with actual seizure outcomes
Creates feedback features for model retraining
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from data_preprocessing import DataLoader

class PredictionFeedback:
    def __init__(self, predictions_file=None, data_folder=None):
        """
        Initialize prediction feedback system
        
        Args:
            predictions_file: Path to longTermPredictions.json
            data_folder: Path to Data folder
        """
        if predictions_file is None:
            SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
            PARENT_DIR = os.path.dirname(SCRIPT_DIR)
            predictions_file = os.path.join(PARENT_DIR, 'Data', 'longTermPredictions.json')
        
        self.predictions_file = predictions_file
        self.loader = DataLoader(data_folder)
        self.predictions_df = None
        self.seizures_df = None
        self.validation_results = {}
        
    def load_predictions(self):
        """Load prediction history from JSON"""
        try:
            with open(self.predictions_file, 'r') as f:
                predictions_list = json.load(f)
            
            # Convert to dataframe
            self.predictions_df = pd.DataFrame(predictions_list)
            self.predictions_df['timestamp'] = pd.to_datetime(self.predictions_df['timestamp'])
            
            # Expand predictions columns
            predictions_expanded = pd.json_normalize(self.predictions_df['predictions'])
            self.predictions_df = pd.concat([
                self.predictions_df[['timestamp']], 
                predictions_expanded
            ], axis=1)
            
            self.predictions_df = self.predictions_df.sort_values('timestamp').reset_index(drop=True)
            print(f"[OK] Loaded {len(self.predictions_df)} predictions")
            return self.predictions_df
        
        except FileNotFoundError:
            print(f"[WARNING] Predictions file not found: {self.predictions_file}")
            return None
        except Exception as e:
            print(f"[ERROR] Error loading predictions: {e}")
            return None
    
    def load_seizures(self):
        """Load actual seizure data"""
        try:
            self.seizures_df = self.loader.load_seizures()
            print(f"[OK] Loaded {len(self.seizures_df)} seizure records")
            return self.seizures_df
        except Exception as e:
            print(f"[ERROR] Error loading seizures: {e}")
            return None
    
    def validate_predictions(self):
        """
        Validate predictions against actual seizure outcomes
        For each prediction, check if a seizure actually occurred in the predicted window
        """
        if self.predictions_df is None:
            self.load_predictions()
        if self.seizures_df is None:
            self.load_seizures()
        
        if self.predictions_df is None or self.seizures_df is None:
            print("[ERROR] Cannot validate: missing predictions or seizure data")
            return None
        
        validation_results = []
        
        for idx, pred_row in self.predictions_df.iterrows():
            pred_time = pred_row['timestamp']
            
            # Check each prediction window
            result = {
                'prediction_timestamp': pred_time,
                'pred_24h_prob': pred_row['24h'],
                'pred_48h_prob': pred_row['48h'],
                'pred_72h_prob': pred_row['72h'],
            }
            
            # Check for seizures in each window
            for hours, col in [(24, '24h'), (48, '48h'), (72, '72h')]:
                window_start = pred_time
                window_end = pred_time + timedelta(hours=hours)
                
                seizures_in_window = self.seizures_df[
                    (self.seizures_df['DateTime'] >= window_start) & 
                    (self.seizures_df['DateTime'] < window_end)
                ]
                
                occurred = len(seizures_in_window) > 0
                result[f'seizure_occurred_{col}'] = occurred
                
                # Calculate prediction accuracy (binary)
                pred_prob = result[f'pred_{col}_prob'] / 100.0
                # If prob > 0.5, model predicted "yes", else "no"
                pred_binary = 1 if pred_prob > 0.5 else 0
                actual_binary = 1 if occurred else 0
                
                result[f'correct_{col}'] = (pred_binary == actual_binary)
                result[f'error_{col}'] = abs(pred_prob - actual_binary)
            
            validation_results.append(result)
        
        self.validation_results = pd.DataFrame(validation_results)
        return self.validation_results
    
    def get_validation_metrics(self):
        """Calculate validation metrics from prediction history"""
        if self.validation_results.empty:
            self.validate_predictions()
        
        if self.validation_results.empty:
            return None
        
        metrics = {}
        
        for window in ['24h', '48h', '72h']:
            correct_col = f'correct_{window}'
            error_col = f'error_{window}'
            
            if correct_col in self.validation_results.columns:
                metrics[window] = {
                    'accuracy': self.validation_results[correct_col].mean(),
                    'mean_absolute_error': self.validation_results[error_col].mean(),
                    'total_predictions': len(self.validation_results),
                    'correct_predictions': self.validation_results[correct_col].sum()
                }
        
        return metrics
    
    def create_prediction_features(self):
        """
        Create features based on prediction history for training
        These features help the model learn from its own past performance
        """
        if self.predictions_df is None:
            self.load_predictions()
        if self.seizures_df is None:
            self.load_seizures()
        
        features_list = []
        
        for idx, pred_row in self.predictions_df.iterrows():
            pred_time = pred_row['timestamp']
            
            features = {
                'DateTime': pred_time,
                'recent_pred_24h_avg': None,
                'recent_pred_24h_std': None,
                'recent_pred_48h_avg': None,
                'recent_pred_48h_std': None,
                'hours_since_last_prediction': None,
                'prediction_trend_24h': None,
                'recent_prediction_variance': None,
                'confidence_spike': None,
            }
            
            # Get recent predictions (last 7 days)
            recent_window = pred_time - timedelta(days=7)
            recent_preds = self.predictions_df[
                (self.predictions_df['timestamp'] >= recent_window) & 
                (self.predictions_df['timestamp'] < pred_time)
            ]
            
            if len(recent_preds) > 0:
                features['recent_pred_24h_avg'] = recent_preds['24h'].mean()
                features['recent_pred_24h_std'] = recent_preds['24h'].std()
                features['recent_pred_48h_avg'] = recent_preds['48h'].mean()
                features['recent_pred_48h_std'] = recent_preds['48h'].std()
                
                # Trend: is probability increasing or decreasing?
                if len(recent_preds) >= 2:
                    features['prediction_trend_24h'] = (
                        recent_preds['24h'].iloc[-1] - recent_preds['24h'].iloc[0]
                    ) / (len(recent_preds) - 1)
                
                # Variance in recent predictions
                features['recent_prediction_variance'] = recent_preds['24h'].var()
            
            # Hours since last prediction
            if idx > 0:
                time_diff = (pred_time - self.predictions_df.iloc[idx-1]['timestamp']).total_seconds() / 3600
                features['hours_since_last_prediction'] = time_diff
            
            # Confidence spike: did prediction jump significantly?
            if idx > 0:
                prev_pred = self.predictions_df.iloc[idx-1]['24h']
                curr_pred = pred_row['24h']
                features['confidence_spike'] = abs(curr_pred - prev_pred)
            
            features_list.append(features)
        
        return pd.DataFrame(features_list)
    
    def create_recency_weights(self):
        """
        Create sample weights based on recency and accuracy
        More recent predictions and accurate predictions get higher weight
        """
        if self.validation_results.empty:
            self.validate_predictions()
        
        weights = []
        now = pd.Timestamp.now()
        
        for idx, row in self.validation_results.iterrows():
            # Recency weight (exponential decay, 30 day half-life)
            days_old = (now - row['prediction_timestamp']).days
            recency_weight = np.exp(-days_old / 30)
            
            # Accuracy weight (predictions that were correct get boosted)
            accuracy_24h = 1.0 if row['correct_24h'] else 0.5
            accuracy_48h = 1.0 if row['correct_48h'] else 0.5
            accuracy_72h = 1.0 if row['correct_72h'] else 0.5
            accuracy_weight = np.mean([accuracy_24h, accuracy_48h, accuracy_72h])
            
            # Combine weights
            final_weight = recency_weight * accuracy_weight
            weights.append(final_weight)
        
        return np.array(weights)
    
    def print_validation_report(self):
        """Print formatted validation report"""
        if self.validation_results.empty:
            self.validate_predictions()
        
        metrics = self.get_validation_metrics()
        
        print("\n" + "=" * 70)
        print("PREDICTION VALIDATION REPORT")
        print("=" * 70)
        
        if metrics is None:
            print("No validation data available")
            return
        
        for window, metric in metrics.items():
            print(f"\n{window} Predictions:")
            print(f"  Accuracy: {metric['accuracy']:.1%}")
            print(f"  Mean Absolute Error: {metric['mean_absolute_error']:.4f}")
            print(f"  Correct Predictions: {metric['correct_predictions']}/{metric['total_predictions']}")
        
        # Overall stats
        total_preds = len(self.validation_results)
        if total_preds > 0:
            overall_correct = (
                self.validation_results['correct_24h'].sum() +
                self.validation_results['correct_48h'].sum() +
                self.validation_results['correct_72h'].sum()
            ) / (total_preds * 3)
            
            print(f"\n[STATS] Overall Accuracy: {overall_correct:.1%}")
            print(f"[INFO] Total Predictions Analyzed: {total_preds}")
        
        print("=" * 70 + "\n")

def main():
    """Test prediction feedback system"""
    feedback = PredictionFeedback()
    
    feedback.load_predictions()
    feedback.load_seizures()
    feedback.validate_predictions()
    feedback.print_validation_report()
    
    # Create features for training
    pred_features = feedback.create_prediction_features()
    print(f"\nCreated {len(pred_features)} prediction feedback records")
    print(f"Features: {pred_features.columns.tolist()}")
    
    # Create weights
    weights = feedback.create_recency_weights()
    print(f"\nRecency & accuracy weights range: [{weights.min():.4f}, {weights.max():.4f}]")

if __name__ == "__main__":
    main()
