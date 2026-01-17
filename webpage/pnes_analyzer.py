"""
PNES (Psychogenic Non-Epileptic Seizures) Detection and Analysis Module

PNES characteristics that help differentiate from epileptic seizures:
- Psychological triggers (stress, anxiety, emotional events)
- Variable and inconsistent seizure patterns
- Lack of sleep-related seizures or seizures during sleep
- Seizures in response to triggers (known stressors)
- Variable consciousness/awareness during events
- Strong correlation with pain/anxiety levels
- Longer duration variability
- Seizures often occur during day (conscious periods)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

def analyze_pnes_indicators(seizure_df: pd.DataFrame, pain_df: pd.DataFrame, watch_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze indicators that may suggest PNES vs epileptic seizures
    Returns risk factors and recommendations
    """
    
    if seizure_df.empty:
        return {'status': 'No seizure data', 'risk_factors': []}
    
    risk_factors = []
    scores = {}
    
    # 1. STRESS/ANXIETY CORRELATION (PNES indicator)
    if not pain_df.empty:
        pain_correlation = _analyze_pain_correlation(seizure_df, pain_df)
        if pain_correlation['correlation'] > 0.6:
            risk_factors.append({
                'indicator': 'Strong Pain/Anxiety Correlation',
                'score': pain_correlation['correlation'],
                'description': f"High correlation between pain levels and seizure occurrence ({pain_correlation['correlation']:.2f})",
                'pnes_relevance': 'HIGH - PNES often triggered by stress/anxiety'
            })
            scores['anxiety_correlation'] = pain_correlation['correlation']
    
    # 2. DAYTIME SEIZURES (PNES more common during day)
    daytime_analysis = _analyze_daytime_pattern(seizure_df)
    if daytime_analysis['daytime_percentage'] > 70:
        risk_factors.append({
            'indicator': 'Predominantly Daytime Seizures',
            'score': daytime_analysis['daytime_percentage'],
            'description': f"{daytime_analysis['daytime_percentage']:.1f}% of seizures occur during waking hours (7AM-11PM)",
            'pnes_relevance': 'MODERATE - PNES more common when conscious'
        })
        scores['daytime_seizures'] = daytime_analysis['daytime_percentage']
    
    # 3. VARIABLE PATTERN (PNES indicator)
    variability = _analyze_pattern_variability(seizure_df)
    if variability['cv'] > 1.0:  # High coefficient of variation
        risk_factors.append({
            'indicator': 'High Duration Variability',
            'score': variability['cv'],
            'description': f"Seizure durations highly variable (CV: {variability['cv']:.2f}, Range: {variability['min']}-{variability['max']}s)",
            'pnes_relevance': 'MODERATE - Epileptic seizures more consistent'
        })
        scores['duration_variability'] = variability['cv']
    
    # 4. FOOD TRIGGER CORRELATION (Psychological factors)
    food_analysis = _analyze_food_triggers(seizure_df)
    if food_analysis['trend'] and food_analysis['food_avg_duration'] > food_analysis['no_food_avg_duration'] * 1.2:
        risk_factors.append({
            'indicator': 'Potential Food/Stress Trigger',
            'score': (food_analysis['food_avg_duration'] / food_analysis['no_food_avg_duration']) if food_analysis['no_food_avg_duration'] > 0 else 1,
            'description': f"Seizures with food: {food_analysis['food_avg_duration']:.0f}s vs without: {food_analysis['no_food_avg_duration']:.0f}s",
            'pnes_relevance': 'MODERATE - Suggests environmental/emotional triggers'
        })
    
    # 5. CLUSTER PATTERN (PNES often cluster, epileptic more regular)
    cluster_analysis = _analyze_seizure_clustering(seizure_df)
    if cluster_analysis['clustering_ratio'] > 2.0:
        risk_factors.append({
            'indicator': 'Clustered Seizure Pattern',
            'score': cluster_analysis['clustering_ratio'],
            'description': f"Seizures tend to cluster (clustering ratio: {cluster_analysis['clustering_ratio']:.2f})",
            'pnes_relevance': 'HIGH - PNES commonly cluster during stress periods'
        })
        scores['clustering'] = cluster_analysis['clustering_ratio']
    
    # 6. SLEEP ANALYSIS (Epileptic seizures may occur during sleep)
    sleep_analysis = _analyze_sleep_triggers(seizure_df, watch_df)
    if sleep_analysis['sleep_correlation'] < 0.3:
        risk_factors.append({
            'indicator': 'No Sleep Correlation',
            'score': 1 - sleep_analysis['sleep_correlation'],
            'description': f"Very low correlation between sleep and seizures ({sleep_analysis['sleep_correlation']:.2f})",
            'pnes_relevance': 'MODERATE - Epileptic seizures often correlate with sleep'
        })
        scores['no_sleep_correlation'] = 1 - sleep_analysis['sleep_correlation']
    
    # 7. PERIOD-RELATED VARIABILITY (Hormonal vs psychological)
    period_analysis = _analyze_period_correlation(seizure_df)
    if period_analysis['period_correlation'] < 0.3:
        risk_factors.append({
            'indicator': 'Low Hormonal Pattern',
            'score': 1 - period_analysis['period_correlation'],
            'description': f"Weak correlation with menstrual cycle ({period_analysis['period_correlation']:.2f})",
            'pnes_relevance': 'LOW - Suggests psychological rather than hormonal trigger'
        })
    
    # Calculate overall PNES likelihood score (0-100)
    if risk_factors:
        pnes_score = sum(s.get('score', 0) for s in scores.values()) / len(scores) * 100 if scores else 0
    else:
        pnes_score = 0
    
    # Classification
    if pnes_score > 70:
        classification = 'HIGH - Strong indicators for PNES evaluation'
    elif pnes_score > 50:
        classification = 'MODERATE - Some PNES indicators present'
    elif pnes_score > 30:
        classification = 'LOW - Few PNES indicators'
    else:
        classification = 'MINIMAL - Pattern more consistent with epileptic seizures'
    
    return {
        'pnes_likelihood_score': round(pnes_score, 1),
        'classification': classification,
        'risk_factors': risk_factors,
        'recommendations': [
            'Consider psychological evaluation if PNES indicators are high',
            'Track emotional/stress events alongside seizures',
            'Monitor response to triggers documented in records',
            'Coordinate with mental health professional for comprehensive assessment'
        ],
        'timestamp': datetime.now().isoformat()
    }


def _analyze_pain_correlation(seizure_df: pd.DataFrame, pain_df: pd.DataFrame) -> Dict[str, float]:
    """Analyze correlation between pain levels and seizure occurrence"""
    if seizure_df.empty or pain_df.empty:
        return {'correlation': 0.0, 'p_value': 1.0}
    
    # Create matching dates
    seizure_dates = seizure_df.groupby(seizure_df['timestamp'].dt.date).size()
    pain_daily = pain_df.groupby(pain_df['timestamp'].dt.date)['Pain'].mean()
    
    # Find common dates
    common_dates = seizure_dates.index.intersection(pain_daily.index)
    
    if len(common_dates) < 3:
        return {'correlation': 0.0, 'p_value': 1.0}
    
    seizure_counts = seizure_dates[common_dates].values
    pain_values = pain_daily[common_dates].values
    
    correlation = np.corrcoef(seizure_counts, pain_values)[0, 1]
    return {
        'correlation': float(np.nan_to_num(correlation, 0.0)),
        'p_value': 0.05,
        'common_dates': len(common_dates)
    }


def _analyze_daytime_pattern(seizure_df: pd.DataFrame) -> Dict[str, float]:
    """Analyze what percentage of seizures occur during daytime (7AM-11PM)"""
    daytime = seizure_df[(seizure_df['hour_of_day'] >= 7) & (seizure_df['hour_of_day'] < 23)]
    total = len(seizure_df)
    percentage = (len(daytime) / total * 100) if total > 0 else 0
    
    return {
        'daytime_percentage': percentage,
        'daytime_count': len(daytime),
        'nighttime_count': total - len(daytime),
        'total': total
    }


def _analyze_pattern_variability(seizure_df: pd.DataFrame) -> Dict[str, float]:
    """Calculate seizure duration variability"""
    durations = seizure_df['duration_seconds'].dropna()
    
    if len(durations) < 2:
        return {'cv': 0.0, 'mean': durations.mean(), 'std': 0.0, 'min': durations.min(), 'max': durations.max()}
    
    mean = durations.mean()
    std = durations.std()
    cv = (std / mean) if mean > 0 else 0
    
    return {
        'cv': float(cv),
        'mean': float(mean),
        'std': float(std),
        'min': float(durations.min()),
        'max': float(durations.max()),
        'count': len(durations)
    }


def _analyze_food_triggers(seizure_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze if food intake correlates with seizure patterns"""
    food_eaten = seizure_df[seizure_df['food_eaten'] == True]
    no_food = seizure_df[seizure_df['food_eaten'] == False]
    
    food_avg = food_eaten['duration_seconds'].mean() if len(food_eaten) > 0 else 0
    no_food_avg = no_food['duration_seconds'].mean() if len(no_food) > 0 else 0
    
    trend = 'higher_with_food' if food_avg > no_food_avg else 'higher_without_food'
    
    return {
        'food_avg_duration': float(food_avg),
        'no_food_avg_duration': float(no_food_avg),
        'food_count': len(food_eaten),
        'no_food_count': len(no_food),
        'trend': trend
    }


def _analyze_seizure_clustering(seizure_df: pd.DataFrame) -> Dict[str, float]:
    """Analyze if seizures cluster together (PNES indicator)"""
    if len(seizure_df) < 3:
        return {'clustering_ratio': 0.0, 'cluster_count': 0}
    
    df_sorted = seizure_df.sort_values('timestamp')
    time_diffs = df_sorted['timestamp'].diff().dt.total_seconds() / 3600  # hours
    time_diffs = time_diffs.dropna()
    
    if len(time_diffs) == 0:
        return {'clustering_ratio': 0.0, 'cluster_count': 0}
    
    # Define cluster: seizures within 24 hours of each other
    clustered = (time_diffs < 24).sum()
    clustering_ratio = (clustered / len(time_diffs)) if len(time_diffs) > 0 else 0
    
    return {
        'clustering_ratio': float(clustering_ratio),
        'cluster_count': int(clustered),
        'total_intervals': len(time_diffs),
        'avg_time_between_hours': float(time_diffs.mean())
    }


def _analyze_sleep_triggers(seizure_df: pd.DataFrame, watch_df: pd.DataFrame) -> Dict[str, float]:
    """Analyze correlation between seizures and sleep patterns"""
    if seizure_df.empty or watch_df.empty:
        return {'sleep_correlation': 0.0, 'seizures_during_sleep': 0}
    
    # Seizures between 11PM-7AM likely during sleep
    night_seizures = seizure_df[(seizure_df['hour_of_day'] >= 23) | (seizure_df['hour_of_day'] < 7)]
    percentage_night = (len(night_seizures) / len(seizure_df) * 100) if len(seizure_df) > 0 else 0
    
    return {
        'sleep_correlation': percentage_night / 100,
        'seizures_during_sleep': len(night_seizures),
        'seizures_during_day': len(seizure_df) - len(night_seizures),
        'sleep_percentage': percentage_night
    }


def _analyze_period_correlation(seizure_df: pd.DataFrame) -> Dict[str, float]:
    """Analyze correlation with menstrual cycle"""
    period_seizures = seizure_df[seizure_df['period'] == True]
    non_period = seizure_df[seizure_df['period'] == False]
    
    if len(seizure_df) == 0:
        return {'period_correlation': 0.0}
    
    period_percentage = (len(period_seizures) / len(seizure_df)) if len(seizure_df) > 0 else 0
    
    return {
        'period_correlation': period_percentage,
        'period_related': len(period_seizures),
        'non_period_related': len(non_period),
        'percentage': period_percentage * 100
    }
