"""
Seizure trigger analysis
Identifies patterns and potential triggers for seizures
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

from data_preprocessing import DataLoader
from feature_engineering import FeatureEngineer

class TriggerAnalyzer:
    def __init__(self):
        self.results = {}
        
    def analyze_all_triggers(self, df, seizures):
        """
        Comprehensive analysis of potential seizure triggers
        """
        print("=" * 60)
        print("SEIZURE TRIGGER ANALYSIS")
        print("=" * 60)
        
        # Temporal patterns
        self.results['temporal'] = self._analyze_temporal_patterns(seizures)
        
        # Physiological patterns
        self.results['physiological'] = self._analyze_physiological_patterns(df, seizures)
        
        # Sleep patterns
        self.results['sleep'] = self._analyze_sleep_patterns(df, seizures)
        
        # Pain patterns
        self.results['pain'] = self._analyze_pain_patterns(df, seizures)
        
        # Activity patterns
        self.results['activity'] = self._analyze_activity_patterns(df, seizures)
        
        # Food patterns
        self.results['food'] = self._analyze_food_patterns(seizures)
        
        # Inter-seizure intervals
        self.results['intervals'] = self._analyze_intervals(seizures)
        
        return self.results
    
    def _analyze_temporal_patterns(self, seizures):
        """Analyze time-based patterns"""
        print("\n1. TEMPORAL PATTERNS")
        print("-" * 60)
        
        seizures['hour'] = seizures['DateTime'].dt.hour
        seizures['day_of_week'] = seizures['DateTime'].dt.dayofweek
        seizures['day_name'] = seizures['DateTime'].dt.day_name()
        
        # Hour of day distribution
        hour_dist = seizures['hour'].value_counts().sort_index()
        print("\nSeizures by hour of day:")
        print(hour_dist)
        
        # Most common hours
        top_hours = hour_dist.nlargest(3)
        print(f"\nMost common hours: {list(top_hours.index)} "
              f"({top_hours.sum()} seizures, {top_hours.sum()/len(seizures)*100:.1f}%)")
        
        # Day of week distribution
        day_dist = seizures['day_name'].value_counts()
        print("\nSeizures by day of week:")
        print(day_dist)
        
        return {
            'hour_distribution': hour_dist.to_dict(),
            'day_distribution': day_dist.to_dict(),
            'peak_hours': list(top_hours.index),
            'peak_days': list(day_dist.nlargest(2).index)
        }
    
    def _analyze_physiological_patterns(self, df, seizures):
        """Analyze heart rate and physiological patterns"""
        print("\n2. PHYSIOLOGICAL PATTERNS")
        print("-" * 60)
        
        results = {}
        
        # Compare heart rate before seizures vs normal
        hr_avg_col = 'Heart Rate [Avg] (count/min)'
        if hr_avg_col in df.columns:
            # Get hours before seizures
            pre_seizure_hrs = []
            for _, seizure in seizures.iterrows():
                hour = seizure['DateTime'].floor('h')
                # Get 6 hours before seizure
                pre_hours = df[
                    (df['DateTime'] >= hour - pd.Timedelta(hours=6)) & 
                    (df['DateTime'] < hour)
                ]
                pre_seizure_hrs.extend(pre_hours[hr_avg_col].dropna().tolist())
            
            # Get normal hours (no seizure within 24 hours)
            normal_hrs = df[df['seizure'] == 0][hr_avg_col].dropna()
            
            if len(pre_seizure_hrs) > 0:
                t_stat, p_value = stats.ttest_ind(pre_seizure_hrs, normal_hrs, equal_var=False)
                
                print(f"\nAverage heart rate before seizures: {np.mean(pre_seizure_hrs):.1f} bpm")
                print(f"Average heart rate (normal): {normal_hrs.mean():.1f} bpm")
                print(f"Statistical significance: p={p_value:.4f}")
                
                if p_value < 0.05:
                    print("⚠️  SIGNIFICANT DIFFERENCE DETECTED")
                
                results['heart_rate'] = {
                    'pre_seizure_avg': float(np.mean(pre_seizure_hrs)),
                    'normal_avg': float(normal_hrs.mean()),
                    'p_value': float(p_value),
                    'significant': bool(p_value < 0.05)
                }
        
        return results
    
    def _analyze_sleep_patterns(self, df, seizures):
        """Analyze sleep patterns before seizures"""
        print("\n3. SLEEP PATTERNS")
        print("-" * 60)
        
        results = {}
        sleep_col = 'Sleep Analysis [Total] (hr)'
        
        if sleep_col in df.columns:
            # Get sleep data before seizures
            sleep_before_seizure = []
            for _, seizure in seizures.iterrows():
                hour = seizure['DateTime'].floor('h')
                # Get most recent sleep data (within 24 hours before)
                recent_sleep = df[
                    (df['DateTime'] >= hour - pd.Timedelta(hours=24)) & 
                    (df['DateTime'] < hour)
                ][sleep_col].dropna()
                
                if len(recent_sleep) > 0:
                    sleep_before_seizure.append(recent_sleep.iloc[-1])
            
            # Compare to average sleep
            avg_sleep = df[sleep_col].dropna().mean()
            
            if len(sleep_before_seizure) > 0:
                print(f"\nAverage sleep before seizures: {np.mean(sleep_before_seizure):.2f} hours")
                print(f"Overall average sleep: {avg_sleep:.2f} hours")
                
                # Test if poor sleep is associated with seizures
                poor_sleep_threshold = avg_sleep - df[sleep_col].std()
                seizures_with_poor_sleep = sum(1 for s in sleep_before_seizure if s < poor_sleep_threshold)
                
                print(f"Seizures preceded by poor sleep (<{poor_sleep_threshold:.1f}h): "
                      f"{seizures_with_poor_sleep}/{len(sleep_before_seizure)} "
                      f"({seizures_with_poor_sleep/len(sleep_before_seizure)*100:.1f}%)")
                
                results['sleep'] = {
                    'avg_before_seizure': float(np.mean(sleep_before_seizure)),
                    'overall_avg': float(avg_sleep),
                    'poor_sleep_count': int(seizures_with_poor_sleep),
                    'total_seizures': len(sleep_before_seizure)
                }
        
        return results
    
    def _analyze_pain_patterns(self, df, seizures):
        """Analyze pain levels before seizures"""
        print("\n4. PAIN PATTERNS")
        print("-" * 60)
        
        results = {}
        
        if 'Pain' in df.columns:
            pain_before_seizure = []
            for _, seizure in seizures.iterrows():
                hour = seizure['DateTime'].floor('h')
                # Get pain data 6 hours before
                recent_pain = df[
                    (df['DateTime'] >= hour - pd.Timedelta(hours=6)) & 
                    (df['DateTime'] < hour)
                ]['Pain'].dropna()
                
                if len(recent_pain) > 0:
                    pain_before_seizure.append(recent_pain.mean())
            
            avg_pain = df['Pain'].dropna().mean()
            
            if len(pain_before_seizure) > 0:
                print(f"\nAverage pain before seizures: {np.mean(pain_before_seizure):.2f}")
                print(f"Overall average pain: {avg_pain:.2f}")
                
                # High pain threshold
                high_pain_threshold = avg_pain + df['Pain'].std()
                seizures_with_high_pain = sum(1 for p in pain_before_seizure if p > high_pain_threshold)
                
                print(f"Seizures preceded by high pain (>{high_pain_threshold:.1f}): "
                      f"{seizures_with_high_pain}/{len(pain_before_seizure)} "
                      f"({seizures_with_high_pain/len(pain_before_seizure)*100:.1f}%)")
                
                results['pain'] = {
                    'avg_before_seizure': float(np.mean(pain_before_seizure)),
                    'overall_avg': float(avg_pain),
                    'high_pain_count': int(seizures_with_high_pain),
                    'total_seizures': len(pain_before_seizure)
                }
        
        return results
    
    def _analyze_activity_patterns(self, df, seizures):
        """Analyze activity levels before seizures"""
        print("\n5. ACTIVITY PATTERNS")
        print("-" * 60)
        
        results = {}
        activity_col = 'Walking + Running Distance (mi)'
        
        if activity_col in df.columns:
            activity_before_seizure = []
            for _, seizure in seizures.iterrows():
                hour = seizure['DateTime'].floor('h')
                # Get activity in 6 hours before
                recent_activity = df[
                    (df['DateTime'] >= hour - pd.Timedelta(hours=6)) & 
                    (df['DateTime'] < hour)
                ][activity_col].dropna().sum()
                
                activity_before_seizure.append(recent_activity)
            
            avg_activity = df[activity_col].dropna().mean() * 6  # 6 hour average
            
            if len(activity_before_seizure) > 0:
                print(f"\nAverage activity 6h before seizures: {np.mean(activity_before_seizure):.3f} miles")
                print(f"Average 6h activity: {avg_activity:.3f} miles")
                
                results['activity'] = {
                    'avg_before_seizure': float(np.mean(activity_before_seizure)),
                    'overall_avg': float(avg_activity)
                }
        
        return results
    
    def _analyze_food_patterns(self, seizures):
        """Analyze food consumption patterns"""
        print("\n6. FOOD PATTERNS")
        print("-" * 60)
        
        # Seizures with food eaten
        eaten_data = seizures[seizures['Eaten'] == True]
        
        print(f"\nSeizures with food eaten before: {len(eaten_data)}/{len(seizures)} "
              f"({len(eaten_data)/len(seizures)*100:.1f}%)")
        
        # Food items mentioned
        if len(eaten_data) > 0:
            foods = eaten_data['Food Eaten'].dropna()
            print(f"\nFood items mentioned: {len(foods)}")
            if len(foods) > 0:
                print("Foods consumed:")
                for food in foods:
                    print(f"  - {food}")
        
        return {
            'seizures_with_food': len(eaten_data),
            'total_seizures': len(seizures),
            'percentage': float(len(eaten_data)/len(seizures)*100) if len(seizures) > 0 else 0
        }
    
    def _analyze_intervals(self, seizures):
        """Analyze time between seizures"""
        print("\n7. INTER-SEIZURE INTERVALS")
        print("-" * 60)
        
        intervals = []
        for i in range(1, len(seizures)):
            interval = (seizures.iloc[i]['DateTime'] - seizures.iloc[i-1]['DateTime'])
            intervals.append(interval.total_seconds() / 3600)  # Convert to hours
        
        if len(intervals) > 0:
            print(f"\nAverage time between seizures: {np.mean(intervals):.1f} hours ({np.mean(intervals)/24:.1f} days)")
            print(f"Median time between seizures: {np.median(intervals):.1f} hours ({np.median(intervals)/24:.1f} days)")
            print(f"Shortest interval: {np.min(intervals):.1f} hours")
            print(f"Longest interval: {np.max(intervals):.1f} hours ({np.max(intervals)/24:.1f} days)")
            
            return {
                'mean_hours': float(np.mean(intervals)),
                'median_hours': float(np.median(intervals)),
                'min_hours': float(np.min(intervals)),
                'max_hours': float(np.max(intervals))
            }
        
        return {}
    
    def save_results(self, filepath='models/trigger_analysis.json'):
        """Save analysis results"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nAnalysis results saved to {filepath}")

def main():
    """Run trigger analysis"""
    # Load data
    loader = DataLoader()
    df, seizures = loader.create_hourly_dataset()
    
    # Create features
    engineer = FeatureEngineer()
    df_features = engineer.create_features(df)
    
    # Analyze triggers
    analyzer = TriggerAnalyzer()
    results = analyzer.analyze_all_triggers(df_features, seizures)
    
    # Save results
    analyzer.save_results()
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    return analyzer

if __name__ == "__main__":
    analyzer = main()