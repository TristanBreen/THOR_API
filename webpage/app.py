from flask import Flask, render_template, jsonify
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import numpy as np

app = Flask(__name__)

# Resolve CSV file paths: check server absolute path first, then Docker mount, then local Data folder
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

# Set CSV file paths
SEIZURES_CSV = os.path.join(BASE_DATA_DIR, "seizures.csv")
PAIN_CSV = os.path.join(BASE_DATA_DIR, "pain.csv")
APPLE_WATCH_CSV = os.path.join(BASE_DATA_DIR, "appleWatchData.csv")

# Debug: Print which path is being used
print(f"[WEBPAGE] Using BASE_DATA_DIR: {BASE_DATA_DIR}")
print(f"[WEBPAGE] SEIZURES_CSV: {SEIZURES_CSV} (exists: {os.path.exists(SEIZURES_CSV)})")
print(f"[WEBPAGE] PAIN_CSV: {PAIN_CSV} (exists: {os.path.exists(PAIN_CSV)})")
print(f"[WEBPAGE] APPLE_WATCH_CSV: {APPLE_WATCH_CSV} (exists: {os.path.exists(APPLE_WATCH_CSV)})")

def safe_float(value, default=0.0):
    """Safely convert value to float, handling NaN and empty strings"""
    try:
        if pd.isna(value) or value == '' or value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def load_apple_watch_data():
    """Load and process Apple Watch data from CSV file with robust error handling"""
    try:
        if not os.path.exists(APPLE_WATCH_CSV):
            print(f"[WATCH] Apple Watch CSV not found at {APPLE_WATCH_CSV}")
            return pd.DataFrame()
            
        # Read CSV with proper handling of empty values
        df = pd.read_csv(APPLE_WATCH_CSV, na_values=['', ' ', 'NA', 'N/A'])
        df.columns = df.columns.str.strip()
        
        print(f"[WATCH] Loaded {len(df)} rows from Apple Watch CSV")
        print(f"[WATCH] Columns: {df.columns.tolist()}")
        
        # Parse timestamp
        df['timestamp'] = pd.to_datetime(df['Date/Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        
        # Drop rows with invalid timestamps
        initial_count = len(df)
        df = df.dropna(subset=['timestamp'])
        dropped_count = initial_count - len(df)
        if dropped_count > 0:
            print(f"[WATCH] Dropped {dropped_count} rows with invalid timestamps")
        
        df = df.sort_values('timestamp', ascending=True)
        
        # Extract date for daily aggregation
        df['date'] = df['timestamp'].dt.date
        
        # Convert numeric columns, replacing empty strings with NaN first
        numeric_columns = [
            'Heart Rate [Min] (count/min)',
            'Heart Rate [Max] (count/min)',
            'Heart Rate [Avg] (count/min)',
            'Sleep Analysis [Total] (hr)',
            'Sleep Analysis [Asleep] (hr)',
            'Sleep Analysis [In Bed] (hr)',
            'Sleep Analysis [Core] (hr)',
            'Sleep Analysis [Deep] (hr)',
            'Sleep Analysis [REM] (hr)',
            'Sleep Analysis [Awake] (hr)',
            'Walking + Running Distance (mi)'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"[WATCH] Successfully processed {len(df)} rows")
        
        # Debug: Check sleep data availability
        sleep_col = 'Sleep Analysis [Total] (hr)'
        if sleep_col in df.columns:
            non_null_sleep = df[sleep_col].notna().sum()
            print(f"[WATCH] Non-null sleep records: {non_null_sleep}")
            if non_null_sleep > 0:
                print(f"[WATCH] Sample sleep values: {df[df[sleep_col].notna()][sleep_col].head().tolist()}")
        
        return df
        
    except Exception as e:
        print(f"[WATCH] Error loading Apple Watch data: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def load_pain_data():
    """Load and process pain data from CSV file"""
    try:
        if not os.path.exists(PAIN_CSV):
            print(f"[PAIN] Pain CSV not found at {PAIN_CSV}")
            return pd.DataFrame()
            
        df = pd.read_csv(PAIN_CSV)
        df.columns = df.columns.str.strip()
        
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df = df.sort_values('timestamp', ascending=True)
        df = df[['timestamp', 'Pain']]
        
        # Convert pain to numeric
        df['Pain'] = pd.to_numeric(df['Pain'], errors='coerce')
        df = df.dropna(subset=['Pain'])
        
        print(f"[PAIN] Loaded {len(df)} pain records")
        return df
        
    except Exception as e:
        print(f"[PAIN] Error loading pain data: {e}")
        return pd.DataFrame()

def load_seizure_data():
    """Load and process seizure data from CSV file"""
    try:
        if not os.path.exists(SEIZURES_CSV):
            print(f"[SEIZURE] Seizure CSV not found at {SEIZURES_CSV}")
            return pd.DataFrame()
            
        df = pd.read_csv(SEIZURES_CSV)
        
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df['duration_seconds'] = pd.to_numeric(df['Duration'], errors='coerce')
        df['hour_of_day'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()
        df['date'] = df['timestamp'].dt.date
        df['food_eaten'] = df['Eaten'].astype(str).str.lower() == 'true'
        df['period'] = df['Peiod'].astype(str).str.lower() == 'true'
        
        df = df[['timestamp', 'duration_seconds', 'hour_of_day', 'day_of_week', 'date', 'food_eaten', 'period']]
        df = df.dropna(subset=['timestamp', 'duration_seconds'])
        df = df.sort_values('timestamp', ascending=False)
        
        print(f"[SEIZURE] Loaded {len(df)} seizure records")
        return df
        
    except Exception as e:
        print(f"[SEIZURE] Error loading seizure data: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def get_daily_sleep_metrics(watch_df):
    """Aggregate sleep metrics by date from hourly Apple Watch data"""
    if watch_df.empty:
        print("[SLEEP] No watch data available")
        return pd.DataFrame()
    
    # Sleep data appears at midnight (00:00:00) each day
    sleep_data = watch_df[watch_df['timestamp'].dt.hour == 0].copy()
    
    if sleep_data.empty:
        print("[SLEEP] No midnight sleep records found")
        return pd.DataFrame()
    
    print(f"[SLEEP] Found {len(sleep_data)} midnight records")
    
    # Check if required columns exist
    required_cols = [
        'Sleep Analysis [Total] (hr)',
        'Sleep Analysis [Deep] (hr)',
        'Sleep Analysis [REM] (hr)',
        'Sleep Analysis [Core] (hr)',
        'Sleep Analysis [Awake] (hr)'
    ]
    
    missing_cols = [col for col in required_cols if col not in sleep_data.columns]
    if missing_cols:
        print(f"[SLEEP] Missing columns: {missing_cols}")
        return pd.DataFrame()
    
    sleep_metrics = []
    for _, row in sleep_data.iterrows():
        # Only include rows with valid sleep data
        total_sleep = safe_float(row.get('Sleep Analysis [Total] (hr)'))
        
        # Skip rows with no sleep data
        if total_sleep <= 0:
            continue
            
        metrics = {
            'date': row['date'],
            'total_sleep': total_sleep,
            'deep_sleep': safe_float(row.get('Sleep Analysis [Deep] (hr)')),
            'rem_sleep': safe_float(row.get('Sleep Analysis [REM] (hr)')),
            'core_sleep': safe_float(row.get('Sleep Analysis [Core] (hr)')),
            'awake_time': safe_float(row.get('Sleep Analysis [Awake] (hr)'))
        }
        sleep_metrics.append(metrics)
    
    result_df = pd.DataFrame(sleep_metrics)
    print(f"[SLEEP] Extracted {len(result_df)} valid sleep records")
    
    if not result_df.empty:
        print(f"[SLEEP] Date range: {result_df['date'].min()} to {result_df['date'].max()}")
        print(f"[SLEEP] Avg total sleep: {result_df['total_sleep'].mean():.2f}h")
    
    return result_df

def get_daily_heart_rate_metrics(watch_df):
    """Aggregate heart rate metrics by date"""
    if watch_df.empty:
        return pd.DataFrame()
    
    # Filter out rows where all HR values are NaN
    hr_cols = ['Heart Rate [Min] (count/min)', 'Heart Rate [Max] (count/min)', 'Heart Rate [Avg] (count/min)']
    watch_df_hr = watch_df.dropna(subset=hr_cols, how='all')
    
    if watch_df_hr.empty:
        print("[HR] No heart rate data available")
        return pd.DataFrame()
    
    daily_hr = watch_df_hr.groupby('date').agg({
        'Heart Rate [Min] (count/min)': 'min',
        'Heart Rate [Max] (count/min)': 'max',
        'Heart Rate [Avg] (count/min)': 'mean'
    }).reset_index()
    
    daily_hr.columns = ['date', 'min_hr', 'max_hr', 'avg_hr']
    
    # Remove rows where all values are still NaN
    daily_hr = daily_hr.dropna(subset=['min_hr', 'max_hr', 'avg_hr'], how='all')
    
    print(f"[HR] Extracted {len(daily_hr)} days of heart rate data")
    return daily_hr

def get_daily_activity_metrics(watch_df):
    """Aggregate activity metrics by date"""
    if watch_df.empty:
        return pd.DataFrame()
    
    activity_col = 'Walking + Running Distance (mi)'
    if activity_col not in watch_df.columns:
        print("[ACTIVITY] Walking distance column not found")
        return pd.DataFrame()
    
    # Filter out rows where activity is NaN
    watch_df_activity = watch_df.dropna(subset=[activity_col])
    
    if watch_df_activity.empty:
        print("[ACTIVITY] No activity data available")
        return pd.DataFrame()
    
    daily_activity = watch_df_activity.groupby('date').agg({
        activity_col: 'sum'
    }).reset_index()
    
    daily_activity.columns = ['date', 'walking_distance']
    
    print(f"[ACTIVITY] Extracted {len(daily_activity)} days of activity data")
    return daily_activity

def analyze_sleep_before_seizures(seizure_df, watch_df):
    """Compare sleep metrics on days before seizures vs baseline"""
    if seizure_df.empty or watch_df.empty:
        print("[ANALYSIS] Missing seizure or watch data")
        return {}
    
    sleep_df = get_daily_sleep_metrics(watch_df)
    if sleep_df.empty:
        print("[ANALYSIS] No sleep data available for analysis")
        return {}
    
    # Get unique seizure dates
    seizure_dates = set(seizure_df['date'].unique())
    print(f"[ANALYSIS] Analyzing sleep before {len(seizure_dates)} seizure days")
    
    # Analyze sleep 1-3 days before seizures
    sleep_before_seizures = []
    baseline_sleep = []
    
    for _, sleep_row in sleep_df.iterrows():
        sleep_date = sleep_row['date']
        
        # Check if any seizure occurred 1-3 days after this sleep date
        is_before_seizure = any(
            (seizure_date - sleep_date).days in [1, 2, 3]
            for seizure_date in seizure_dates
        )
        
        if is_before_seizure:
            sleep_before_seizures.append(sleep_row)
        else:
            baseline_sleep.append(sleep_row)
    
    if not sleep_before_seizures:
        print("[ANALYSIS] No sleep data found 1-3 days before seizures")
        return {}
    
    # Calculate averages
    before_df = pd.DataFrame(sleep_before_seizures)
    baseline_df = pd.DataFrame(baseline_sleep) if baseline_sleep else pd.DataFrame()
    
    result = {
        'before_seizure_avg_total': float(before_df['total_sleep'].mean()),
        'before_seizure_avg_deep': float(before_df['deep_sleep'].mean()),
        'before_seizure_avg_rem': float(before_df['rem_sleep'].mean()),
        'before_seizure_count': len(before_df)
    }
    
    if not baseline_df.empty:
        result.update({
            'baseline_avg_total': float(baseline_df['total_sleep'].mean()),
            'baseline_avg_deep': float(baseline_df['deep_sleep'].mean()),
            'baseline_avg_rem': float(baseline_df['rem_sleep'].mean()),
            'baseline_count': len(baseline_df)
        })
    
    print(f"[ANALYSIS] Sleep before seizures: {result['before_seizure_avg_total']:.2f}h")
    if 'baseline_avg_total' in result:
        print(f"[ANALYSIS] Baseline sleep: {result['baseline_avg_total']:.2f}h")
    
    return result

def calculate_sleep_debt(watch_df, target_hours=7.5):
    """Calculate cumulative sleep debt over time"""
    if watch_df.empty:
        return []
    
    sleep_df = get_daily_sleep_metrics(watch_df)
    if sleep_df.empty:
        return []
    
    sleep_df = sleep_df.sort_values('date')
    sleep_df['sleep_deficit'] = target_hours - sleep_df['total_sleep']
    
    # Calculate rolling debt with minimum periods
    sleep_df['cumulative_debt_3day'] = sleep_df['sleep_deficit'].rolling(window=3, min_periods=1).sum()
    sleep_df['cumulative_debt_7day'] = sleep_df['sleep_deficit'].rolling(window=7, min_periods=1).sum()
    
    # Convert date to string for JSON serialization
    sleep_df['date'] = sleep_df['date'].astype(str)
    
    result = sleep_df[['date', 'total_sleep', 'sleep_deficit', 'cumulative_debt_3day', 'cumulative_debt_7day']].to_dict('records')
    print(f"[SLEEP DEBT] Calculated debt for {len(result)} days")
    
    return result

def analyze_heart_rate_trends(seizure_df, watch_df):
    """Analyze heart rate patterns around seizure days"""
    if seizure_df.empty or watch_df.empty:
        return {}
    
    hr_df = get_daily_heart_rate_metrics(watch_df)
    if hr_df.empty:
        print("[HR ANALYSIS] No heart rate data for analysis")
        return {}
    
    seizure_dates = set(seizure_df['date'].unique())
    
    # Separate seizure days from non-seizure days
    hr_df['is_seizure_day'] = hr_df['date'].apply(lambda d: d in seizure_dates)
    
    seizure_hr = hr_df[hr_df['is_seizure_day']]
    baseline_hr = hr_df[~hr_df['is_seizure_day']]
    
    result = {}
    
    if not seizure_hr.empty:
        result['seizure_day_min_hr'] = float(seizure_hr['min_hr'].mean())
        result['seizure_day_avg_hr'] = float(seizure_hr['avg_hr'].mean())
        result['seizure_day_max_hr'] = float(seizure_hr['max_hr'].mean())
        print(f"[HR ANALYSIS] Seizure day avg HR: {result['seizure_day_avg_hr']:.1f} bpm")
    
    if not baseline_hr.empty:
        result['baseline_min_hr'] = float(baseline_hr['min_hr'].mean())
        result['baseline_avg_hr'] = float(baseline_hr['avg_hr'].mean())
        result['baseline_max_hr'] = float(baseline_hr['max_hr'].mean())
        print(f"[HR ANALYSIS] Baseline avg HR: {result['baseline_avg_hr']:.1f} bpm")
    
    return result

def analyze_activity_correlation(seizure_df, watch_df):
    """Analyze activity levels 1-2 days before seizures"""
    if seizure_df.empty or watch_df.empty:
        return {}
    
    activity_df = get_daily_activity_metrics(watch_df)
    if activity_df.empty:
        print("[ACTIVITY ANALYSIS] No activity data for analysis")
        return {}
    
    seizure_dates = set(seizure_df['date'].unique())
    
    # Activity 1-2 days before seizures
    activity_before_seizures = []
    baseline_activity = []
    
    for _, activity_row in activity_df.iterrows():
        activity_date = activity_row['date']
        
        is_before_seizure = any(
            (seizure_date - activity_date).days in [1, 2]
            for seizure_date in seizure_dates
        )
        
        if is_before_seizure:
            activity_before_seizures.append(activity_row['walking_distance'])
        else:
            baseline_activity.append(activity_row['walking_distance'])
    
    result = {}
    
    if activity_before_seizures:
        result['before_seizure_avg_distance'] = float(np.mean(activity_before_seizures))
        print(f"[ACTIVITY ANALYSIS] Activity before seizures: {result['before_seizure_avg_distance']:.2f} mi")
    
    if baseline_activity:
        result['baseline_avg_distance'] = float(np.mean(baseline_activity))
        print(f"[ACTIVITY ANALYSIS] Baseline activity: {result['baseline_avg_distance']:.2f} mi")
    
    return result

def prepare_health_chart_data(seizure_df, watch_df):
    """Prepare chart data for new health metrics"""
    if watch_df.empty:
        print("[HEALTH CHARTS] No watch data available")
        return {}
    
    sleep_df = get_daily_sleep_metrics(watch_df)
    hr_df = get_daily_heart_rate_metrics(watch_df)
    activity_df = get_daily_activity_metrics(watch_df)
    
    # Start with the dataframe that has the most data
    combined = pd.DataFrame()
    
    if not sleep_df.empty:
        combined = sleep_df.copy()
        print(f"[HEALTH CHARTS] Starting with {len(combined)} sleep records")
    
    if not hr_df.empty:
        if combined.empty:
            combined = hr_df.copy()
            print(f"[HEALTH CHARTS] Starting with {len(combined)} HR records")
        else:
            combined = combined.merge(hr_df, on='date', how='outer')
            print(f"[HEALTH CHARTS] After HR merge: {len(combined)} records")
    
    if not activity_df.empty:
        if combined.empty:
            combined = activity_df.copy()
            print(f"[HEALTH CHARTS] Starting with {len(combined)} activity records")
        else:
            combined = combined.merge(activity_df, on='date', how='outer')
            print(f"[HEALTH CHARTS] After activity merge: {len(combined)} records")
    
    if combined.empty:
        print("[HEALTH CHARTS] No combined data available")
        return {}
    
    combined = combined.sort_values('date')
    combined['date_str'] = combined['date'].astype(str)
    
    # Mark seizure days
    seizure_markers = []
    if not seizure_df.empty:
        seizure_dates = set(seizure_df['date'].unique())
        combined['has_seizure'] = combined['date'].apply(lambda d: d in seizure_dates)
        seizure_markers = combined[combined['has_seizure']]['date_str'].tolist()
        print(f"[HEALTH CHARTS] Marked {len(seizure_markers)} seizure days")
    
    # Sleep debt calculation
    sleep_debt = calculate_sleep_debt(watch_df)
    
    # Prepare result with safe data extraction
    result = {
        'seizure_markers': seizure_markers
    }
    
    # Sleep timeline
    if not sleep_df.empty and all(col in combined.columns for col in ['total_sleep', 'deep_sleep', 'rem_sleep']):
        sleep_timeline = combined[['date_str', 'total_sleep', 'deep_sleep', 'rem_sleep']].dropna(
            subset=['total_sleep']
        ).fillna(0).to_dict('records')
        result['sleep_timeline'] = sleep_timeline
        print(f"[HEALTH CHARTS] Sleep timeline: {len(sleep_timeline)} records")
    else:
        result['sleep_timeline'] = []
        print("[HEALTH CHARTS] No sleep timeline data")
    
    # HR timeline
    if not hr_df.empty and all(col in combined.columns for col in ['min_hr', 'avg_hr', 'max_hr']):
        hr_timeline = combined[['date_str', 'min_hr', 'avg_hr', 'max_hr']].dropna(
            subset=['avg_hr']
        ).fillna(0).to_dict('records')
        result['hr_timeline'] = hr_timeline
        print(f"[HEALTH CHARTS] HR timeline: {len(hr_timeline)} records")
    else:
        result['hr_timeline'] = []
        print("[HEALTH CHARTS] No HR timeline data")
    
    # Activity timeline
    if not activity_df.empty and 'walking_distance' in combined.columns:
        activity_timeline = combined[['date_str', 'walking_distance']].dropna(
            subset=['walking_distance']
        ).fillna(0).to_dict('records')
        result['activity_timeline'] = activity_timeline
        print(f"[HEALTH CHARTS] Activity timeline: {len(activity_timeline)} records")
    else:
        result['activity_timeline'] = []
        print("[HEALTH CHARTS] No activity timeline data")
    
    # Sleep debt
    result['sleep_debt'] = sleep_debt
    
    # Sleep stage ratios
    if not sleep_df.empty:
        sleep_ratios_df = sleep_df.copy()
        # Only calculate ratios where total_sleep > 0
        valid_sleep = sleep_ratios_df['total_sleep'] > 0
        sleep_ratios_df.loc[valid_sleep, 'deep_ratio'] = (
            sleep_ratios_df.loc[valid_sleep, 'deep_sleep'] / 
            sleep_ratios_df.loc[valid_sleep, 'total_sleep'] * 100
        )
        sleep_ratios_df.loc[valid_sleep, 'rem_ratio'] = (
            sleep_ratios_df.loc[valid_sleep, 'rem_sleep'] / 
            sleep_ratios_df.loc[valid_sleep, 'total_sleep'] * 100
        )
        sleep_ratios_df.loc[valid_sleep, 'core_ratio'] = (
            sleep_ratios_df.loc[valid_sleep, 'core_sleep'] / 
            sleep_ratios_df.loc[valid_sleep, 'total_sleep'] * 100
        )
        
        sleep_ratios_df['date_str'] = sleep_ratios_df['date'].astype(str)
        sleep_ratios = sleep_ratios_df[['date_str', 'deep_ratio', 'rem_ratio', 'core_ratio']].dropna().fillna(0).to_dict('records')
        result['sleep_ratios'] = sleep_ratios
        print(f"[HEALTH CHARTS] Sleep ratios: {len(sleep_ratios)} records")
    else:
        result['sleep_ratios'] = []
        print("[HEALTH CHARTS] No sleep ratio data")
    
    return result

def calculate_statistics(df):
    """Calculate summary statistics"""
    if df.empty:
        return {}
    
    df_sorted = df.sort_values('timestamp')
    
    total_seizures = len(df)
    date_range_days = (df_sorted['timestamp'].max() - df_sorted['timestamp'].min()).days + 1
    avg_per_day = total_seizures / date_range_days if date_range_days > 0 else 0
    avg_per_week = avg_per_day * 7
    
    avg_duration = df['duration_seconds'].mean()
    min_duration = df['duration_seconds'].min()
    max_duration = df['duration_seconds'].max()
    
    food_eaten_count = df[df['food_eaten'] == True].shape[0]
    no_food_count = df[df['food_eaten'] == False].shape[0]
    
    period_count = df[df['period'] == True].shape[0]
    non_period_count = df[df['period'] == False].shape[0]
    
    period_avg_duration = df[df['period'] == True]['duration_seconds'].mean() if period_count > 0 else 0
    non_period_avg_duration = df[df['period'] == False]['duration_seconds'].mean() if non_period_count > 0 else 0
    
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
    
    df = df.sort_values('timestamp')
    
    daily_freq = df.groupby(df['timestamp'].dt.date).size().reset_index()
    daily_freq.columns = ['date', 'count']
    daily_freq['date'] = daily_freq['date'].astype(str)
    
    hour_freq = df['hour_of_day'].value_counts().sort_index().reset_index()
    hour_freq.columns = ['hour', 'count']
    hour_freq['hour'] = hour_freq['hour'].astype(int)
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_freq = df['day_of_week'].value_counts().reindex(day_order, fill_value=0).reset_index()
    day_freq.columns = ['day', 'count']
    
    df['month'] = df['timestamp'].dt.to_period('M').astype(str)
    monthly_freq = df.groupby('month').size().reset_index()
    monthly_freq.columns = ['month', 'count']
    
    heatmap_data = df.groupby(['hour_of_day', 'day_of_week']).size().reset_index(name='count')
    heatmap_pivot = pd.DataFrame(0, index=range(24), columns=day_order)
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
    
    duration_buckets = {
        '45-75s': len(df[(df['duration_seconds'] >= 45) & (df['duration_seconds'] < 75)]),
        '75-100s': len(df[(df['duration_seconds'] >= 75) & (df['duration_seconds'] < 100)]),
        '100-125s': len(df[(df['duration_seconds'] >= 100) & (df['duration_seconds'] < 125)]),
        '125-150s': len(df[(df['duration_seconds'] >= 125) & (df['duration_seconds'] < 150)]),
        '150-200s': len(df[(df['duration_seconds'] >= 150) & (df['duration_seconds'] < 200)]),
        '200+s': len(df[df['duration_seconds'] >= 200])
    }
    duration_distribution = [{'range': k, 'count': v} for k, v in duration_buckets.items()]
    
    df_sorted = df.sort_values('timestamp', ascending=True)
    df_sorted['date_only'] = df_sorted['timestamp'].dt.date
    seizure_dates = df_sorted['date_only'].unique()
    
    intervals = []
    for i in range(1, len(seizure_dates)):
        interval_days = (seizure_dates[i] - seizure_dates[i-1]).days
        intervals.append(interval_days)
    
    time_between = []
    for i, interval in enumerate(intervals):
        time_between.append({
            'seizure_number': i + 2,
            'days_since_previous': interval,
            'date': seizure_dates[i+1].strftime('%Y-%m-%d') if i+1 < len(seizure_dates) else ''
        })
    
    duration_stats = {
        'mean': round(df['duration_seconds'].mean(), 1),
        'median': round(df['duration_seconds'].median(), 1),
        'std': round(df['duration_seconds'].std(), 1),
        'min': int(df['duration_seconds'].min()),
        'max': int(df['duration_seconds'].max())
    }
    
    food_eaten_durations = df[df['food_eaten'] == True]['duration_seconds'].mean()
    no_food_durations = df[df['food_eaten'] == False]['duration_seconds'].mean()
    
    food_analysis = {
        'food_eaten_avg': round(food_eaten_durations, 1) if not pd.isna(food_eaten_durations) else 0,
        'no_food_avg': round(no_food_durations, 1) if not pd.isna(no_food_durations) else 0,
        'food_eaten_count': int(df[df['food_eaten'] == True].shape[0]),
        'no_food_count': int(df[df['food_eaten'] == False].shape[0])
    }
    
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
        return {'pain_timeline': [], 'seizure_markers': []}
    
    pain_df = pain_df.sort_values('timestamp')
    first_pain_timestamp = pain_df['timestamp'].min()
    seizures_after_pain = seizure_df[seizure_df['timestamp'] >= first_pain_timestamp].copy()
    
    pain_timeline = []
    for _, row in pain_df.iterrows():
        pain_timeline.append({
            'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'pain': int(row['Pain'])
        })
    
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
    print("\n[API] ===== Starting data load =====")
    
    try:
        seizure_df = load_seizure_data()
        pain_df = load_pain_data()
        watch_df = load_apple_watch_data()
        
        print(f"[API] Data loaded - Seizures: {len(seizure_df)}, Pain: {len(pain_df)}, Watch: {len(watch_df)}")
        
        stats = calculate_statistics(seizure_df)
        charts = prepare_chart_data(seizure_df)
        pain_charts = prepare_pain_chart_data(pain_df, seizure_df)
        
        # New health insights
        health_insights = {}
        health_charts = {}
        
        if not watch_df.empty:
            print("[API] Calculating health insights...")
            health_insights['sleep_analysis'] = analyze_sleep_before_seizures(seizure_df, watch_df)
            health_insights['heart_rate_analysis'] = analyze_heart_rate_trends(seizure_df, watch_df)
            health_insights['activity_analysis'] = analyze_activity_correlation(seizure_df, watch_df)
            health_charts = prepare_health_chart_data(seizure_df, watch_df)
            print(f"[API] Health insights generated: {list(health_insights.keys())}")
        else:
            print("[API] No watch data - skipping health insights")
        
        response_data = {
            'statistics': stats,
            'charts': charts,
            'pain_charts': pain_charts,
            'health_insights': health_insights,
            'health_charts': health_charts,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print("[API] ===== Data load complete =====\n")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"[API] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'statistics': {},
            'charts': {},
            'pain_charts': {'pain_timeline': [], 'seizure_markers': []},
            'health_insights': {},
            'health_charts': {},
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 500

@app.route('/api/export')
def export_data():
    """Export seizure data as CSV"""
    try:
        df = load_seizure_data()
        if df.empty:
            return jsonify({'error': 'No data to export'}), 400
        
        df = df.sort_values('timestamp', ascending=True)
        export_df = df[['timestamp', 'duration_seconds', 'hour_of_day', 'day_of_week', 'food_eaten', 'period']].copy()
        export_df.columns = ['DateTime', 'Duration (seconds)', 'Hour of Day', 'Day of Week', 'Food Eaten', 'During Period']
        csv_string = export_df.to_csv(index=False)
        
        return csv_string, 200, {
            'Content-Disposition': 'attachment; filename="kylie_seizure_data.csv"',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)