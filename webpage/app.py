from flask import Flask, render_template, jsonify
import pandas as pd
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
SEIZURES_CSV = '/data/seizures.csv' if os.path.exists('/data/seizures.csv') else 'seizures.csv'
PAIN_CSV = '/data/pain.csv' if os.path.exists('/data/pain.csv') else 'pain.csv'

def load_pain_data():
    """Load and process pain data from CSV file"""
    try:
        df = pd.read_csv(PAIN_CSV)
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # Combine Date and Time columns into a timestamp
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # Remove rows with invalid timestamps
        df = df.dropna(subset=['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp', ascending=True)
        
        # Select only the columns we need
        df = df[['timestamp', 'Pain']]
        
        return df
    except Exception as e:
        print(f"Error loading pain data: {e}")
        return pd.DataFrame()

def load_seizure_data():
    """Load and process seizure data from CSV file"""
    try:
        # Read CSV file from /data directory (mounted volume)
        #csv_path = '/data/seizures.csv'
        
        df = pd.read_csv(SEIZURES_CSV)
        
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
    
    # Monthly seizure frequency
    df['month'] = df['timestamp'].dt.to_period('M').astype(str)
    monthly_freq = df.groupby('month').size().reset_index()
    monthly_freq.columns = ['month', 'count']
    
    # Hour × Day of Week Heatmap
    heatmap_data = df.groupby(['hour_of_day', 'day_of_week']).size().reset_index(name='count')
    # Reindex to include all hours and days
    heatmap_pivot = pd.DataFrame(0, 
                                  index=range(24), 
                                  columns=day_order)
    for _, row in heatmap_data.iterrows():
        heatmap_pivot.loc[row['hour_of_day'], row['day_of_week']] = row['count']
    
    heatmap_formatted = []
    for hour in range(24):
        for day in day_order:
            count = int(heatmap_pivot.loc[hour, day])
            heatmap_formatted.append({
                'hour': hour,
                'day': day,
                'count': count,
                'day_index': day_order.index(day)
            })
    
    # Duration Distribution - bucketed by ranges
    duration_buckets = {
        '45-75s': len(df[(df['duration_seconds'] >= 45) & (df['duration_seconds'] < 75)]),
        '75-100s': len(df[(df['duration_seconds'] >= 75) & (df['duration_seconds'] < 100)]),
        '100-125s': len(df[(df['duration_seconds'] >= 100) & (df['duration_seconds'] < 125)]),
        '125-150s': len(df[(df['duration_seconds'] >= 125) & (df['duration_seconds'] < 150)]),
        '150-200s': len(df[(df['duration_seconds'] >= 150) & (df['duration_seconds'] < 200)]),
        '200+s': len(df[df['duration_seconds'] >= 200])
    }
    duration_distribution = [{'range': k, 'count': v} for k, v in duration_buckets.items()]
    
    # Time Between Seizures (intervals in days)
    df_sorted = df.sort_values('timestamp', ascending=True)
    df_sorted['date_only'] = df_sorted['timestamp'].dt.date
    seizure_dates = df_sorted['date_only'].unique()
    
    intervals = []
    for i in range(1, len(seizure_dates)):
        interval_days = (seizure_dates[i] - seizure_dates[i-1]).days
        intervals.append(interval_days)
    
    # Create time between seizures data for chart
    time_between = []
    for i, interval in enumerate(intervals):
        time_between.append({
            'seizure_number': i + 2,  # Start from 2nd seizure
            'days_since_previous': interval,
            'date': seizure_dates[i+1].strftime('%Y-%m-%d') if i+1 < len(seizure_dates) else ''
        })
    
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
        'monthly_frequency': monthly_freq.to_dict('records'),
        'heatmap': heatmap_formatted,
        'duration_distribution': duration_distribution,
        'time_between_seizures': time_between,
        'duration_stats': duration_stats,
        'food_analysis': food_analysis,
        'timeline': timeline_data.to_dict('records')
    }

def prepare_pain_chart_data(pain_df, seizure_df):
    """Prepare pain tracking data with seizure markers"""
    if pain_df.empty:
        return {
            'pain_timeline': [],
            'seizure_markers': []
        }
    
    # Sort pain data by timestamp
    pain_df = pain_df.sort_values('timestamp')
    
    # Get first pain timestamp
    first_pain_timestamp = pain_df['timestamp'].min()
    
    # Filter seizures to only those after first pain recording
    seizures_after_pain = seizure_df[seizure_df['timestamp'] >= first_pain_timestamp].copy()
    
    # Prepare pain timeline
    pain_timeline = []
    for _, row in pain_df.iterrows():
        pain_timeline.append({
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'pain': int(row['Pain'])
        })
    
    # Prepare seizure markers (timestamps where seizures occurred)
    seizure_markers = []
    for _, row in seizures_after_pain.iterrows():
        seizure_markers.append({
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return {
        'pain_timeline': pain_timeline,
        'seizure_markers': seizure_markers
    }

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    df = load_seizure_data()
    pain_df = load_pain_data()
    stats = calculate_statistics(df)
    charts = prepare_chart_data(df)
    pain_charts = prepare_pain_chart_data(pain_df, df)
    
    return jsonify({
        'statistics': stats,
        'charts': charts,
        'pain_charts': pain_charts,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/export')
def export_data():
    """Export seizure data as CSV"""
    try:
        df = load_seizure_data()
        if df.empty:
            return jsonify({'error': 'No data to export'}), 400
        
        # Sort chronologically for export
        df = df.sort_values('timestamp', ascending=True)
        
        # Format the dataframe for export
        export_df = df[['timestamp', 'duration_seconds', 'hour_of_day', 'day_of_week', 'food_eaten', 'period']].copy()
        export_df.columns = ['DateTime', 'Duration (seconds)', 'Hour of Day', 'Day of Week', 'Food Eaten', 'During Period']
        
        # Convert to CSV string
        csv_string = export_df.to_csv(index=False)
        
        return csv_string, 200, {
            'Content-Disposition': 'attachment; filename="kylie_seizure_data.csv"',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)