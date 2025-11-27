from flask import Flask, render_template, jsonify, send_from_directory
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import numpy as np
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Flask
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Resolve CSV file paths with better error handling
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'Data')

# Set CSV file paths
SEIZURES_CSV = os.path.join(DATA_DIR, "seizures.csv")
PAIN_CSV = os.path.join(DATA_DIR, "pain.csv")
APPLE_WATCH_CSV = os.path.join(DATA_DIR, "appleWatchData.csv")

# Debug logging
logger.info(f"Using DATA_DIR: {DATA_DIR}")
logger.info(f"SEIZURES_CSV: {SEIZURES_CSV} (exists: {os.path.exists(SEIZURES_CSV)})")
logger.info(f"PAIN_CSV: {PAIN_CSV} (exists: {os.path.exists(PAIN_CSV)})")
logger.info(f"APPLE_WATCH_CSV: {APPLE_WATCH_CSV} (exists: {os.path.exists(APPLE_WATCH_CSV)})")

@lru_cache(maxsize=128)
def load_apple_watch_data():
    """Load and process Apple Watch data from CSV file with caching"""
    try:
        if not os.path.exists(APPLE_WATCH_CSV):
            logger.warning(f"Apple Watch data file not found: {APPLE_WATCH_CSV}")
            return pd.DataFrame()
            
        df = pd.read_csv(APPLE_WATCH_CSV)
        df.columns = df.columns.str.strip()
        
        # Parse timestamp with better error handling
        df['timestamp'] = pd.to_datetime(df['Date/Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df = df.sort_values('timestamp', ascending=True)
        
        # Extract date for daily aggregation
        df['date'] = df['timestamp'].dt.date
        
        # Clean and normalize data
        numeric_columns = ['Heart Rate [Min] (count/min)', 'Heart Rate [Max] (count/min)', 
                          'Heart Rate [Avg] (count/min)', 'Sleep Analysis [Total] (hr)',
                          'Sleep Analysis [Asleep] (hr)', 'Sleep Analysis [In Bed] (hr)',
                          'Sleep Analysis [Core] (hr)', 'Sleep Analysis [Deep] (hr)',
                          'Sleep Analysis [REM] (hr)', 'Sleep Analysis [Awake] (hr)',
                          'Walking + Running Distance (mi)']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        logger.error(f"Error loading Apple Watch data: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=128)
def load_pain_data():
    """Load and process pain data from CSV file with caching"""
    try:
        if not os.path.exists(PAIN_CSV):
            logger.warning(f"Pain data file not found: {PAIN_CSV}")
            return pd.DataFrame()
            
        df = pd.read_csv(PAIN_CSV)
        df.columns = df.columns.str.strip()
        
        # Handle different column naming conventions
        date_col = 'Date' if 'Date' in df.columns else df.columns[0]
        time_col = 'Time' if 'Time' in df.columns else df.columns[1]
        pain_col = 'Pain' if 'Pain' in df.columns else df.columns[2]
        
        df['timestamp'] = pd.to_datetime(df[date_col] + ' ' + df[time_col], 
                                       format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df = df.sort_values('timestamp', ascending=True)
        df = df[['timestamp', pain_col]].rename(columns={pain_col: 'Pain'})
        
        return df
    except Exception as e:
        logger.error(f"Error loading pain data: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=128)
def load_seizure_data():
    """Load and process seizure data from CSV file with caching"""
    try:
        if not os.path.exists(SEIZURES_CSV):
            logger.warning(f"Seizure data file not found: {SEIZURES_CSV}")
            return pd.DataFrame()
            
        df = pd.read_csv(SEIZURES_CSV)
        
        # Handle column mapping with fallback
        column_mapping = {
            'Date': 'Date',
            'Time': 'Time', 
            'Duration': 'Duration',
            'Peiod': 'Period',
            'Eaten': 'Eaten',
            'Food Eaten': 'Food_Eaten'
        }
        
        # Find actual column names
        actual_columns = {}
        for standard, fallback in column_mapping.items():
            matches = [col for col in df.columns if standard.lower() in col.lower()]
            actual_columns[standard] = matches[0] if matches else fallback
        
        df['timestamp'] = pd.to_datetime(df[actual_columns['Date']] + ' ' + df[actual_columns['Time']], 
                                       format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df['duration_seconds'] = pd.to_numeric(df[actual_columns['Duration']], errors='coerce')
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['date'] = df['timestamp'].dt.date
        df['month'] = df['timestamp'].dt.to_period('M')
        
        # Handle boolean fields with better error handling
        period_col = actual_columns['Period']
        eaten_col = actual_columns['Eaten']
        
        df['food_eaten'] = df[eaten_col].astype(str).str.lower().isin(['true', '1', 'yes'])
        df['period'] = df[period_col].astype(str).str.lower().isin(['true', '1', 'yes'])
        
        # Keep food description if available
        if actual_columns['Food_Eaten'] in df.columns:
            df['food_description'] = df[actual_columns['Food_Eaten']].fillna('')
        else:
            df['food_description'] = ''
        
        result_df = df[['timestamp', 'duration_seconds', 'hour_of_day', 'day_of_week', 
                       'date', 'food_eaten', 'period', 'food_description']].copy()
        result_df = result_df.dropna(subset=['timestamp'])
        result_df = result_df.sort_values('timestamp', ascending=False)
        
        return result_df
    except Exception as e:
        logger.error(f"Error loading seizure data: {e}")
        return pd.DataFrame()

def calculate_statistics(seizure_df):
    """Calculate comprehensive seizure statistics"""
    if seizure_df.empty:
        return {}
    
    total_seizures = len(seizure_df)
    first_record = seizure_df['timestamp'].min()
    last_record = seizure_df['timestamp'].max()
    date_range_days = (last_record - first_record).days
    
    # Recent statistics (last 7 and 30 days)
    seven_days_ago = datetime.now() - timedelta(days=7)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    recent_7_days = len(seizure_df[seizure_df['timestamp'] >= seven_days_ago])
    recent_30_days = len(seizure_df[seizure_df['timestamp'] >= thirty_days_ago])
    
    # Duration statistics
    avg_duration = seizure_df['duration_seconds'].mean()
    min_duration = seizure_df['duration_seconds'].min()
    max_duration = seizure_df['duration_seconds'].max()
    
    # Food and period statistics
    food_eaten_count = len(seizure_df[seizure_df['food_eaten'] == True])
    no_food_count = len(seizure_df[seizure_df['food_eaten'] == False])
    period_related_count = len(seizure_df[seizure_df['period'] == True])
    
    # Calculate averages
    avg_per_day = total_seizures / max(date_range_days, 1)
    avg_per_week = (total_seizures / max(date_range_days, 1)) * 7
    avg_per_month = (total_seizures / max(date_range_days, 1)) * 30.44
    
    return {
        'total_seizures': int(total_seizures),
        'first_record': first_record.strftime('%Y-%m-%d'),
        'last_record': last_record.strftime('%Y-%m-%d'),
        'date_range_days': int(date_range_days),
        'recent_seizures_7_days': int(recent_7_days),
        'recent_seizures_30_days': int(recent_30_days),
        'avg_duration': int(avg_duration) if not pd.isna(avg_duration) else 0,
        'min_duration': int(min_duration) if not pd.isna(min_duration) else 0,
        'max_duration': int(max_duration) if not pd.isna(max_duration) else 0,
        'food_eaten_count': int(food_eaten_count),
        'no_food_count': int(no_food_count),
        'period_related_count': int(period_related_count),
        'avg_per_day': round(avg_per_day, 2),
        'avg_per_week': round(avg_per_week, 2),
        'avg_per_month': round(avg_per_month, 2)
    }

def generate_chart_data(seizure_df, pain_df, watch_df):
    """Generate comprehensive chart data"""
    if seizure_df.empty:
        return {}
    
    charts = {}
    
    # Timeline data
    timeline_data = seizure_df[['timestamp', 'duration_seconds', 'food_eaten', 'period']].copy()
    timeline_data['timestamp'] = timeline_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    charts['timeline'] = timeline_data.to_dict('records')
    
    # Hour of day analysis
    hour_counts = seizure_df['hour_of_day'].value_counts().sort_index()
    charts['hourly'] = {
        'labels': [f"{h:02d}:00" for h in hour_counts.index],
        'data': hour_counts.values.tolist()
    }
    
    # Day of week analysis
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = seizure_df['day_of_week'].value_counts().reindex(day_order, fill_value=0)
    charts['daily'] = {
        'labels': day_counts.index.tolist(),
        'data': day_counts.values.tolist()
    }
    
    # Duration distribution
    duration_bins = [0, 30, 60, 90, 120, 180, 300]
    duration_labels = ['0-30s', '31-60s', '61-90s', '91-120s', '121-180s', '181-300s', '300s+']
    duration_counts = pd.cut(seizure_df['duration_seconds'], bins=duration_bins + [float('inf')], 
                           labels=duration_labels, include_lowest=True).value_counts()
    charts['duration'] = {
        'labels': duration_labels,
        'data': [duration_counts.get(label, 0) for label in duration_labels]
    }
    
    # Monthly trends
    monthly_counts = seizure_df.groupby('month').size()
    charts['monthly'] = {
        'labels': [str(month) for month in monthly_counts.index],
        'data': monthly_counts.values.tolist()
    }
    
    # Time between seizures
    seizure_df_sorted = seizure_df.sort_values('timestamp')
    time_intervals = seizure_df_sorted['timestamp'].diff().dt.total_seconds() / 3600  # hours
    time_intervals = time_intervals.dropna()
    
    if len(time_intervals) > 0:
        interval_bins = [0, 24, 48, 72, 168, 720]  # hours
        interval_labels = ['<24h', '24-48h', '48-72h', '3-7d', '1-30d', '>30d']
        interval_counts = pd.cut(time_intervals, bins=interval_bins + [float('inf')], 
                               labels=interval_labels, include_lowest=True).value_counts()
        charts['time_intervals'] = {
            'labels': interval_labels,
            'data': [interval_counts.get(label, 0) for label in interval_labels]
        }
    else:
        charts['time_intervals'] = {'labels': [], 'data': []}
    
    # Food correlation
    food_data = seizure_df['food_eaten'].value_counts()
    charts['food_correlation'] = {
        'labels': ['With Food', 'Without Food'],
        'data': [food_data.get(True, 0), food_data.get(False, 0)]
    }
    
    # Heatmap data (hour x day of week)
    heatmap_data = seizure_df.groupby(['day_of_week', 'hour_of_day']).size().reset_index(name='count')
    
    # Create matrix for heatmap
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_matrix = []
    for day in day_order:
        day_data = heatmap_data[heatmap_data['day_of_week'] == day]
        row = []
        for hour in range(24):
            count = day_data[day_data['hour_of_day'] == hour]['count'].sum()
            row.append(count)
        heatmap_matrix.append(row)
    
    charts['heatmap'] = {
        'matrix': heatmap_matrix,
        'days': day_order,
        'hours': list(range(24))
    }
    
    # Duration statistics
    charts['duration_stats'] = {
        'mean': int(seizure_df['duration_seconds'].mean()),
        'median': int(seizure_df['duration_seconds'].median()),
        'min': int(seizure_df['duration_seconds'].min()),
        'max': int(seizure_df['duration_seconds'].max()),
        'std': int(seizure_df['duration_seconds'].std())
    }
    
    return charts

def generate_health_insights(seizure_df, watch_df, pain_df):
    """Generate comprehensive health insights"""
    insights = {}
    
    if watch_df.empty:
        return insights
    
    try:
        # Sleep analysis
        sleep_analysis = {}
        
        # Get sleep data for 3 days before each seizure
        seizure_dates = seizure_df['date'].unique()
        sleep_before_seizure = []
        
        for seizure_date in seizure_dates:
            three_days_before = seizure_date - timedelta(days=3)
            sleep_data = watch_df[watch_df['date'] >= three_days_before][
                watch_df['date'] < seizure_date
            ]['Sleep Analysis [Total] (hr)'].dropna()
            
            if len(sleep_data) > 0:
                sleep_before_seizure.extend(sleep_data.tolist())
        
        if sleep_before_seizure:
            sleep_analysis['before_seizure_avg_total'] = np.mean(sleep_before_seizure)
            sleep_analysis['before_seizure_avg_deep'] = np.mean([
                watch_df[watch_df['date'] >= seizure_date - timedelta(days=3)][
                    watch_df['date'] < seizure_date
                ]['Sleep Analysis [Deep] (hr)'].dropna()
                for seizure_date in seizure_dates
            ])
        
        # Baseline sleep (all available data)
        baseline_sleep = watch_df['Sleep Analysis [Total] (hr)'].dropna()
        if len(baseline_sleep) > 0:
            sleep_analysis['baseline_avg_total'] = np.mean(baseline_sleep)
            sleep_analysis['baseline_avg_deep'] = np.mean(watch_df['Sleep Analysis [Deep] (hr)'].dropna())
            sleep_analysis['baseline_avg_rem'] = np.mean(watch_df['Sleep Analysis [REM] (hr)'].dropna())
        
        insights['sleep_analysis'] = sleep_analysis
        
        # Heart rate analysis
        hr_analysis = {}
        
        # Heart rate on seizure days
        seizure_day_hr = watch_df[watch_df['date'].isin(seizure_dates)]['Heart Rate [Min] (count/min)'].dropna()
        if len(seizure_day_hr) > 0:
            hr_analysis['seizure_day_min_hr'] = np.mean(seizure_day_hr)
        
        # Baseline heart rate
        baseline_hr = watch_df['Heart Rate [Min] (count/min)'].dropna()
        if len(baseline_hr) > 0:
            hr_analysis['baseline_min_hr'] = np.mean(baseline_hr)
        
        insights['heart_rate_analysis'] = hr_analysis
        
        # Activity analysis
        activity_analysis = {}
        
        # Activity before seizures
        activity_before_seizure = []
        for seizure_date in seizure_dates:
            three_days_before = seizure_date - timedelta(days=3)
            activity_data = watch_df[watch_df['date'] >= three_days_before][
                watch_df['date'] < seizure_date
            ]['Walking + Running Distance (mi)'].dropna()
            
            if len(activity_data) > 0:
                activity_before_seizure.extend(activity_data.tolist())
        
        if activity_before_seizure:
            activity_analysis['before_seizure_avg_distance'] = np.mean(activity_before_seizure)
        
        # Baseline activity
        baseline_activity = watch_df['Walking + Running Distance (mi)'].dropna()
        if len(baseline_activity) > 0:
            activity_analysis['baseline_avg_distance'] = np.mean(baseline_activity)
        
        insights['activity_analysis'] = activity_analysis
        
    except Exception as e:
        logger.error(f"Error generating health insights: {e}")
    
    return insights

def generate_health_charts(watch_df, seizure_df):
    """Generate health-related charts"""
    if watch_df.empty:
        return {}
    
    charts = {}
    
    try:
        # Sleep comparison chart
        sleep_data = watch_df[['date', 'Sleep Analysis [Total] (hr)', 'Sleep Analysis [Deep] (hr)', 
                              'Sleep Analysis [REM] (hr)']].dropna()
        
        if len(sleep_data) > 0:
            charts['sleep_trend'] = {
                'dates': [d.strftime('%Y-%m-%d') for d in sleep_data['date']],
                'total_sleep': sleep_data['Sleep Analysis [Total] (hr)'].tolist(),
                'deep_sleep': sleep_data['Sleep Analysis [Deep] (hr)'].tolist(),
                'rem_sleep': sleep_data['Sleep Analysis [REM] (hr)'].tolist()
            }
        
        # Heart rate trend
        hr_data = watch_df[['date', 'Heart Rate [Min] (count/min)', 'Heart Rate [Max] (count/min)', 
                           'Heart Rate [Avg] (count/min)']].dropna()
        
        if len(hr_data) > 0:
            charts['heart_rate_trend'] = {
                'dates': [d.strftime('%Y-%m-%d') for d in hr_data['date']],
                'min_hr': hr_data['Heart Rate [Min] (count/min)'].tolist(),
                'max_hr': hr_data['Heart Rate [Max] (count/min)'].tolist(),
                'avg_hr': hr_data['Heart Rate [Avg] (count/min)'].tolist()
            }
        
        # Activity trend
        activity_data = watch_df[['date', 'Walking + Running Distance (mi)']].dropna()
        
        if len(activity_data) > 0:
            charts['activity_trend'] = {
                'dates': [d.strftime('%Y-%m-%d') for d in activity_data['date']],
                'distance': activity_data['Walking + Running Distance (mi)'].tolist()
            }
        
    except Exception as e:
        logger.error(f"Error generating health charts: {e}")
    
    return charts

def generate_pain_charts(pain_df, seizure_df):
    """Generate pain tracking charts with seizure correlation"""
    if pain_df.empty:
        return {}
    
    charts = {}
    
    try:
        # Pain trend over time
        pain_data = pain_df.sort_values('timestamp')
        charts['pain_timeline'] = {
            'dates': [d.strftime('%Y-%m-%d %H:%M') for d in pain_data['timestamp']],
            'pain_levels': pain_data['Pain'].tolist()
        }
        
        # Pain distribution
        pain_counts = pain_data['Pain'].value_counts().sort_index()
        charts['pain_distribution'] = {
            'levels': pain_counts.index.tolist(),
            'counts': pain_counts.values.tolist()
        }
        
        # Correlation with seizures
        if not seizure_df.empty:
            # Find pain levels within 24 hours of seizures
            pain_near_seizures = []
            for _, seizure in seizure_df.iterrows():
                seizure_time = seizure['timestamp']
                nearby_pain = pain_df[
                    (pain_df['timestamp'] >= seizure_time - timedelta(hours=24)) &
                    (pain_df['timestamp'] <= seizure_time + timedelta(hours=24))
                ]['Pain'].tolist()
                pain_near_seizures.extend(nearby_pain)
            
            if pain_near_seizures:
                charts['pain_seizure_correlation'] = {
                    'pain_near_seizures': pain_near_seizures,
                    'avg_pain_near_seizures': np.mean(pain_near_seizures),
                    'overall_avg_pain': np.mean(pain_data['Pain'])
                }
        
    except Exception as e:
        logger.error(f"Error generating pain charts: {e}")
    
    return charts

@app.route('/')
def dashboard():
    """Render the main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/data')
def api_data():
    """API endpoint for dashboard data"""
    try:
        # Load all data (clear cache to get fresh data)
        seizure_df = load_seizure_data()
        pain_df = load_pain_data()
        watch_df = load_apple_watch_data()
        
        logger.info(f"Loaded seizure data: {len(seizure_df)} records")
        logger.info(f"Loaded pain data: {len(pain_df)} records")
        logger.info(f"Loaded watch data: {len(watch_df)} records")
        
        # Generate comprehensive data
        statistics = calculate_statistics(seizure_df)
        charts = generate_chart_data(seizure_df, pain_df, watch_df)
        health_insights = generate_health_insights(seizure_df, watch_df, pain_df)
        health_charts = generate_health_charts(watch_df, seizure_df)
        pain_charts = generate_pain_charts(pain_df, seizure_df)
        
        response_data = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': statistics,
            'charts': charts,
            'health_insights': health_insights,
            'health_charts': health_charts,
            'pain_charts': pain_charts,
            'data_summary': {
                'seizure_records': len(seizure_df),
                'pain_records': len(pain_df),
                'apple_watch_records': len(watch_df),
                'date_range': {
                    'start': seizure_df['timestamp'].min().strftime('%Y-%m-%d') if not seizure_df.empty else None,
                    'end': seizure_df['timestamp'].max().strftime('%Y-%m-%d') if not seizure_df.empty else None
                }
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in API endpoint: {e}")
        return jsonify({
            'error': str(e),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': {},
            'charts': {},
            'health_insights': {},
            'health_charts': {},
            'pain_charts': {},
            'data_summary': {}
        }), 500

@app.route('/api/export')
def export_data():
    """Export seizure data as CSV"""
    try:
        seizure_df = load_seizure_data()
        if seizure_df.empty:
            return jsonify({'error': 'No data to export'}), 404
        
        # Prepare export data
        export_df = seizure_df.copy()
        export_df['timestamp'] = export_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        export_df['date'] = export_df['date'].astype(str)
        
        # Convert to CSV
        csv_data = export_df.to_csv(index=False)
        
        response = app.response_class(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=seizure_data_export.csv',
                'Cache-Control': 'no-cache'
            }
        )
        return response
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_page():
    """Health insights page"""
    return render_template('health.html')

@app.route('/analytics')
def analytics_page():
    """Advanced analytics page"""
    return render_template('analytics.html')

@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, message="Internal server error"), 500

if __name__ == '__main__':
    # Create data directory and copy files if needed
    if not os.path.exists(SEIZURES_CSV) and os.path.exists('/mnt/okcomputer/upload/seizures.csv'):
        import shutil
        shutil.copy('/mnt/okcomputer/upload/seizures.csv', SEIZURES_CSV)
        shutil.copy('/mnt/okcomputer/upload/pain.csv', PAIN_CSV)
        shutil.copy('/mnt/okcomputer/upload/appleWatchData.csv', APPLE_WATCH_CSV)
        logger.info("Copied data files to output directory")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)