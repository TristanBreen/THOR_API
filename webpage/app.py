from flask import Flask, render_template, jsonify
import pandas as pd
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

def load_seizure_data():
    """Load and process seizure data from CSV file"""
    try:
        # Read CSV file from parent directory
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'seizures.csv'))
        
        df = pd.read_csv(csv_path)
        
        # Combine Date and Time columns into a timestamp
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # Rename Duration to duration_seconds
        df['duration_seconds'] = df['Duration']
        
        # Extract hour of day for "time of day" analysis
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['date'] = df['timestamp'].dt.date
        
        # Extract whether food was eaten
        df['food_eaten'] = df['Eaten'].astype(str).str.lower() == 'true'
        
        # Extract period data - True if 'Peiod' column is True (note: typo in CSV)
        df['period'] = df['Peiod'].astype(str).str.lower() == 'true'
        
        # Select only the columns we need
        df = df[['timestamp', 'duration_seconds', 'hour_of_day', 'day_of_week', 'date', 'food_eaten', 'period']]
        
        # Remove rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])
        
        # Sort by timestamp descending (most recent first for display)
        df = df.sort_values('timestamp', ascending=False)
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def calculate_statistics(df):
    """Calculate summary statistics"""
    if df.empty:
        return {}
    
    # Sort by timestamp ascending for calculations
    df_sorted = df.sort_values('timestamp')
    
    total_seizures = len(df)
    
    # Date range
    date_range_days = (df_sorted['timestamp'].max() - df_sorted['timestamp'].min()).days + 1
    
    # Average seizures per day and week
    avg_per_day = total_seizures / date_range_days if date_range_days > 0 else 0
    avg_per_week = avg_per_day * 7
    
    # Duration statistics
    avg_duration = df['duration_seconds'].mean()
    min_duration = df['duration_seconds'].min()
    max_duration = df['duration_seconds'].max()
    
    # Food correlation
    food_eaten_count = df[df['food_eaten'] == True].shape[0]
    no_food_count = df[df['food_eaten'] == False].shape[0]
    
    # Period correlation
    period_count = df[df['period'] == True].shape[0]
    non_period_count = df[df['period'] == False].shape[0]
    
    # Average duration during period vs outside period
    period_avg_duration = df[df['period'] == True]['duration_seconds'].mean() if period_count > 0 else 0
    non_period_avg_duration = df[df['period'] == False]['duration_seconds'].mean() if non_period_count > 0 else 0
    
    # Recent activity (last 7 days)
    last_7_days = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]
    recent_seizures = len(last_7_days)
    
    return {
        'total_seizures': total_seizures,
        'date_range_days': date_range_days,
        'avg_per_day': round(avg_per_day, 2),
        'avg_per_week': round(avg_per_week, 2),
        'avg_duration': round(avg_duration, 1),
        'min_duration': int(min_duration),
        'max_duration': int(max_duration),
        'food_eaten_count': food_eaten_count,
        'no_food_count': no_food_count,
        'period_related_count': period_count,
        'non_period_count': non_period_count,
        'period_avg_duration': round(period_avg_duration, 1),
        'non_period_avg_duration': round(non_period_avg_duration, 1),
        'recent_seizures_7_days': recent_seizures,
        'first_record': df_sorted['timestamp'].min().strftime('%Y-%m-%d'),
        'last_record': df_sorted['timestamp'].max().strftime('%Y-%m-%d')
    }

def prepare_chart_data(df):
    """Prepare data for charts"""
    if df.empty:
        return {}
    
    # Sort by timestamp for consistent ordering
    df = df.sort_values('timestamp')
    
    # Daily seizure frequency (chronological)
    daily_freq = df.groupby(df['timestamp'].dt.date).size().reset_index()
    daily_freq.columns = ['date', 'count']
    daily_freq['date'] = daily_freq['date'].astype(str)
    
    # Hour of day analysis - when seizures are most likely
    hour_freq = df['hour_of_day'].value_counts().sort_index().reset_index()
    hour_freq.columns = ['hour', 'count']
    hour_freq['hour'] = hour_freq['hour'].astype(int)
    
    # Day of week analysis
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_freq = df['day_of_week'].value_counts().reindex(day_order, fill_value=0).reset_index()
    day_freq.columns = ['day', 'count']
    
    # Duration statistics
    duration_stats = {
        'mean': round(df['duration_seconds'].mean(), 1),
        'median': round(df['duration_seconds'].median(), 1),
        'std': round(df['duration_seconds'].std(), 1),
        'min': int(df['duration_seconds'].min()),
        'max': int(df['duration_seconds'].max())
    }
    
    # Food correlation analysis
    food_eaten_durations = df[df['food_eaten'] == True]['duration_seconds'].mean()
    no_food_durations = df[df['food_eaten'] == False]['duration_seconds'].mean()
    
    food_analysis = {
        'food_eaten_avg': round(food_eaten_durations, 1) if not pd.isna(food_eaten_durations) else 0,
        'no_food_avg': round(no_food_durations, 1) if not pd.isna(no_food_durations) else 0,
        'food_eaten_count': int(df[df['food_eaten'] == True].shape[0]),
        'no_food_count': int(df[df['food_eaten'] == False].shape[0])
    }
    
    # Time series data (most recent first for display)
    timeline_data = df.sort_values('timestamp', ascending=False)[['timestamp', 'duration_seconds', 'hour_of_day', 'day_of_week', 'food_eaten', 'period']].copy()
    timeline_data['timestamp'] = timeline_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    timeline_data['food_eaten'] = timeline_data['food_eaten'].astype(bool)
    timeline_data['period'] = timeline_data['period'].astype(bool)
    
    return {
        'daily_frequency': daily_freq.to_dict('records'),
        'hour_frequency': hour_freq.to_dict('records'),
        'day_frequency': day_freq.to_dict('records'),
        'duration_stats': duration_stats,
        'food_analysis': food_analysis,
        'timeline': timeline_data.to_dict('records')
    }

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    df = load_seizure_data()
    stats = calculate_statistics(df)
    charts = prepare_chart_data(df)
    
    return jsonify({
        'statistics': stats,
        'charts': charts,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)