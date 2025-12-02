"""
Visualization tools for seizure data and predictions
Creates plots to understand patterns and model performance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

from data_preprocessing import DataLoader
from feature_engineering import FeatureEngineer

class SeizureVisualizer:
    def __init__(self, output_dir='visualizations'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_style('whitegrid')
        
    def create_all_visualizations(self):
        """Generate all visualization plots"""
        print("Creating visualizations...")
        
        # Load data
        loader = DataLoader()
        df, seizures = loader.create_hourly_dataset()
        engineer = FeatureEngineer()
        df_features = engineer.create_features(df)
        
        # Create plots
        self.plot_seizure_timeline(seizures)
        self.plot_temporal_patterns(seizures)
        self.plot_heart_rate_patterns(df_features, seizures)
        self.plot_pain_patterns(df_features, seizures)
        self.plot_sleep_patterns(df_features, seizures)
        self.plot_seizure_intervals(seizures)
        
        print(f"\nVisualizations saved to {self.output_dir}/")
        
    def plot_seizure_timeline(self, seizures):
        """Plot seizure occurrences over time"""
        fig, ax = plt.subplots(figsize=(15, 4))
        
        # Plot seizures as vertical lines
        for _, seizure in seizures.iterrows():
            ax.axvline(seizure['DateTime'], color='red', alpha=0.3, linewidth=2)
        
        # Add markers
        ax.scatter(seizures['DateTime'], [1]*len(seizures), 
                  s=100, color='red', alpha=0.6, zorder=5)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Seizure Events', fontsize=12)
        ax.set_title('Seizure Timeline', fontsize=14, fontweight='bold')
        ax.set_ylim([0, 2])
        ax.set_yticks([])
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/seizure_timeline.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_temporal_patterns(self, seizures):
        """Plot seizure patterns by time of day and day of week"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Hour of day
        seizures['hour'] = seizures['DateTime'].dt.hour
        hour_counts = seizures['hour'].value_counts().sort_index()
        
        axes[0].bar(hour_counts.index, hour_counts.values, color='steelblue', alpha=0.7)
        axes[0].set_xlabel('Hour of Day', fontsize=12)
        axes[0].set_ylabel('Number of Seizures', fontsize=12)
        axes[0].set_title('Seizures by Hour of Day', fontsize=13, fontweight='bold')
        axes[0].set_xticks(range(0, 24, 2))
        axes[0].grid(axis='y', alpha=0.3)
        
        # Day of week
        seizures['day_name'] = seizures['DateTime'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = seizures['day_name'].value_counts().reindex(day_order)
        
        axes[1].bar(range(len(day_counts)), day_counts.values, color='coral', alpha=0.7)
        axes[1].set_xlabel('Day of Week', fontsize=12)
        axes[1].set_ylabel('Number of Seizures', fontsize=12)
        axes[1].set_title('Seizures by Day of Week', fontsize=13, fontweight='bold')
        axes[1].set_xticks(range(7))
        axes[1].set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/temporal_patterns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_heart_rate_patterns(self, df, seizures):
        """Plot heart rate patterns before/during/after seizures"""
        hr_col = 'Heart Rate [Avg] (count/min)'
        
        if hr_col not in df.columns:
            return
            
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot background heart rate
        ax.plot(df['DateTime'], df[hr_col], alpha=0.3, color='gray', label='Heart Rate')
        
        # Add rolling average
        df['hr_rolling'] = df[hr_col].rolling(window=24, center=True).mean()
        ax.plot(df['DateTime'], df['hr_rolling'], color='blue', linewidth=2, 
               label='24h Rolling Average')
        
        # Mark seizures
        for _, seizure in seizures.iterrows():
            ax.axvline(seizure['DateTime'], color='red', alpha=0.5, linestyle='--', linewidth=2)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Heart Rate (bpm)', fontsize=12)
        ax.set_title('Heart Rate Over Time with Seizure Events', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/heart_rate_patterns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_pain_patterns(self, df, seizures):
        """Plot pain levels and seizure correlation"""
        if 'Pain' not in df.columns:
            return
            
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot pain levels
        pain_data = df[df['Pain'].notna()]
        ax.scatter(pain_data['DateTime'], pain_data['Pain'], 
                  alpha=0.5, s=50, color='purple', label='Pain Level')
        
        # Add trend line
        pain_data['pain_rolling'] = pain_data['Pain'].rolling(window=24, center=True).mean()
        ax.plot(pain_data['DateTime'], pain_data['pain_rolling'], 
               color='darkviolet', linewidth=2, label='24h Rolling Average')
        
        # Mark seizures
        for _, seizure in seizures.iterrows():
            ax.axvline(seizure['DateTime'], color='red', alpha=0.4, linestyle='--', linewidth=2)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Pain Level (0-10)', fontsize=12)
        ax.set_title('Pain Levels Over Time with Seizure Events', fontsize=14, fontweight='bold')
        ax.set_ylim([0, 10])
        ax.legend(loc='upper right')
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/pain_patterns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_sleep_patterns(self, df, seizures):
        """Plot sleep quality patterns"""
        sleep_col = 'Sleep Analysis [Total] (hr)'
        
        if sleep_col not in df.columns:
            return
            
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot sleep data
        sleep_data = df[df[sleep_col].notna()]
        ax.bar(sleep_data['DateTime'], sleep_data[sleep_col], 
              width=0.03, alpha=0.6, color='skyblue', label='Total Sleep')
        
        # Add average line
        avg_sleep = sleep_data[sleep_col].mean()
        ax.axhline(avg_sleep, color='blue', linestyle='--', linewidth=2, 
                  label=f'Average ({avg_sleep:.1f}h)')
        
        # Mark seizures
        for _, seizure in seizures.iterrows():
            ax.axvline(seizure['DateTime'], color='red', alpha=0.4, linestyle='--', linewidth=2)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Sleep Duration (hours)', fontsize=12)
        ax.set_title('Sleep Patterns Over Time with Seizure Events', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/sleep_patterns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
    def plot_seizure_intervals(self, seizures):
        """Plot time between seizures"""
        intervals = []
        for i in range(1, len(seizures)):
            interval = (seizures.iloc[i]['DateTime'] - seizures.iloc[i-1]['DateTime'])
            intervals.append(interval.total_seconds() / 3600)  # Convert to hours
        
        if len(intervals) == 0:
            return
            
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        axes[0].hist(intervals, bins=20, color='teal', alpha=0.7, edgecolor='black')
        axes[0].axvline(np.mean(intervals), color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {np.mean(intervals):.1f}h')
        axes[0].axvline(np.median(intervals), color='orange', linestyle='--', 
                       linewidth=2, label=f'Median: {np.median(intervals):.1f}h')
        axes[0].set_xlabel('Hours Between Seizures', fontsize=12)
        axes[0].set_ylabel('Frequency', fontsize=12)
        axes[0].set_title('Distribution of Inter-Seizure Intervals', 
                         fontsize=13, fontweight='bold')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        # Time series
        axes[1].plot(range(1, len(intervals)+1), intervals, marker='o', 
                    color='teal', linewidth=2, markersize=6)
        axes[1].axhline(np.mean(intervals), color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {np.mean(intervals):.1f}h')
        axes[1].set_xlabel('Seizure Pair Number', fontsize=12)
        axes[1].set_ylabel('Hours Between Seizures', fontsize=12)
        axes[1].set_title('Inter-Seizure Interval Over Time', 
                         fontsize=13, fontweight='bold')
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/seizure_intervals.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """Generate all visualizations"""
    visualizer = SeizureVisualizer()
    visualizer.create_all_visualizations()
    
    print("\n✅ Visualization complete!")
    print(f"   Check the '{visualizer.output_dir}/' folder for plots")
    
    return visualizer

if __name__ == "__main__":
    visualizer = main()