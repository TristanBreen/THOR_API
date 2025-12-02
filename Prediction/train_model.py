"""
Model training for seizure prediction
Trains classification and regression models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, mean_absolute_error, mean_squared_error
import joblib
import json
import os
from datetime import datetime

from data_preprocessing import DataLoader
from feature_engineering import FeatureEngineer

class SeizurePredictor:
    def __init__(self, prediction_horizon=6):
        self.prediction_horizon = prediction_horizon
        self.scaler = StandardScaler()
        self.classification_model = None
        self.regression_model = None
        self.feature_cols = None
        
    def train(self, X, y_classification, y_regression):
        """
        Train both classification and regression models
        """
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        # Split data
        X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
            X_scaled, y_classification, y_regression, 
            test_size=0.2, random_state=42, stratify=y_classification
        )
        
        print("Training classification model...")
        self.classification_model = self._train_classification(
            X_train, X_test, y_class_train, y_class_test
        )
        
        print("\nTraining regression model...")
        self.regression_model = self._train_regression(
            X_train, X_test, y_reg_train, y_reg_test
        )
        
        return {
            'classification_metrics': self._evaluate_classification(
                self.classification_model, X_test, y_class_test
            ),
            'regression_metrics': self._evaluate_regression(
                self.regression_model, X_test, y_reg_test
            ),
            'feature_importance': self._get_feature_importance(X.columns)
        }
    
    def _train_classification(self, X_train, X_test, y_train, y_test):
        """Train seizure occurrence classifier"""
        # Try multiple models
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=200, 
                max_depth=10,
                min_samples_split=10,
                class_weight='balanced',
                random_state=42
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        best_model = None
        best_score = 0
        
        for name, model in models.items():
            print(f"  Training {name}...")
            model.fit(X_train, y_train)
            score = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
            print(f"  {name} ROC-AUC: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_model = model
        
        return best_model
    
    def _train_regression(self, X_train, X_test, y_train, y_test):
        """Train time-to-next-seizure regressor"""
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=10,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        return model
    
    def _evaluate_classification(self, model, X_test, y_test):
        """Evaluate classification model"""
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        print("\nClassification Results:")
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        print(f"\nROC-AUC Score: {roc_auc:.4f}")
        
        return {
            'roc_auc': roc_auc,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def _evaluate_regression(self, model, X_test, y_test):
        """Evaluate regression model"""
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print("\nRegression Results:")
        print(f"Mean Absolute Error: {mae:.2f} hours")
        print(f"Root Mean Squared Error: {rmse:.2f} hours")
        
        return {
            'mae': mae,
            'rmse': rmse
        }
    
    def _get_feature_importance(self, feature_names):
        """Get feature importance from both models"""
        importance_dict = {}
        
        if hasattr(self.classification_model, 'feature_importances_'):
            class_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': self.classification_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            importance_dict['classification'] = class_importance.head(20).to_dict('records')
        
        if hasattr(self.regression_model, 'feature_importances_'):
            reg_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': self.regression_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            importance_dict['regression'] = reg_importance.head(20).to_dict('records')
        
        return importance_dict
    
    def save_model(self, filepath='models'):
        """Save trained models and scaler"""
        os.makedirs(filepath, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        joblib.dump(self.classification_model, 
                   os.path.join(filepath, f'classification_model_{timestamp}.pkl'))
        joblib.dump(self.regression_model, 
                   os.path.join(filepath, f'regression_model_{timestamp}.pkl'))
        joblib.dump(self.scaler, 
                   os.path.join(filepath, f'scaler_{timestamp}.pkl'))
        
        # Save latest versions
        joblib.dump(self.classification_model, 
                   os.path.join(filepath, 'classification_model_latest.pkl'))
        joblib.dump(self.regression_model, 
                   os.path.join(filepath, 'regression_model_latest.pkl'))
        joblib.dump(self.scaler, 
                   os.path.join(filepath, 'scaler_latest.pkl'))
        
        print(f"\nModels saved to {filepath}/")
    
    def load_model(self, filepath='models'):
        """Load trained models and scaler"""
        self.classification_model = joblib.load(
            os.path.join(filepath, 'classification_model_latest.pkl'))
        self.regression_model = joblib.load(
            os.path.join(filepath, 'regression_model_latest.pkl'))
        self.scaler = joblib.load(
            os.path.join(filepath, 'scaler_latest.pkl'))
        
        print("Models loaded successfully")
    
    def predict(self, X):
        """Make predictions on new data"""
        X = X.copy()
        # Fill NaN values with column means, then forward fill for any remaining NaNs
        X = X.fillna(X.mean())
        X = X.fillna(0)  # Fill any remaining NaNs with 0
        
        X_scaled = self.scaler.transform(X)
        
        seizure_prob = self.classification_model.predict_proba(X_scaled)[:, 1]
        hours_to_seizure = self.regression_model.predict(X_scaled)
        
        return {
            'seizure_probability': seizure_prob,
            'predicted_hours_to_seizure': hours_to_seizure
        }

def main():
    """Main training pipeline"""
    print("=" * 60)
    print("SEIZURE PREDICTION MODEL TRAINING")
    print("=" * 60)
    
    # Load and prepare data
    print("\n1. Loading data...")
    loader = DataLoader()
    df, seizures = loader.create_hourly_dataset()
    print(f"   Loaded {len(df)} hours of data")
    print(f"   Total seizures: {len(seizures)}")
    
    # Create features
    print("\n2. Engineering features...")
    engineer = FeatureEngineer()
    df_features = engineer.create_features(df)
    print(f"   Created {df_features.shape[1]} features")
    
    # Prepare training data
    print("\n3. Preparing training data...")
    X, y_class, y_reg, feature_cols = engineer.prepare_training_data(
        df_features, prediction_horizon=6
    )
    print(f"   Training samples: {len(X)}")
    print(f"   Positive samples (seizures): {y_class.sum()} ({y_class.sum()/len(y_class)*100:.1f}%)")
    
    # Train models
    print("\n4. Training models...")
    predictor = SeizurePredictor(prediction_horizon=6)
    metrics = predictor.train(X, y_class, y_reg)
    
    # Save models
    print("\n5. Saving models...")
    predictor.save_model()
    
    # Save feature importance
    with open('models/feature_importance.json', 'w') as f:
        json.dump(metrics['feature_importance'], f, indent=2)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print("\nTop 10 Important Features (Classification):")
    for i, feat in enumerate(metrics['feature_importance']['classification'][:10], 1):
        print(f"  {i}. {feat['feature']}: {feat['importance']:.4f}")
    
    return predictor, metrics

if __name__ == "__main__":
    predictor, metrics = main()