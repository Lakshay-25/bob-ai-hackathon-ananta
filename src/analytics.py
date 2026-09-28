"""
analytics.py — Drishti Crime Intelligence Analytics Engine
Handles risk scoring, zone explanations, and patrol suggestions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def compute_risk_scores(df):
    """
    Compute risk scores for all areas based on:
    - Total incident count (normalized)
    - Recency-weighted incident count (recent months count more)
    - Trend analysis (rising/falling in last 30 days vs prior 30 days)
    
    Returns DataFrame with columns:
    [area, total_incidents, recent_incidents, trend_direction, recency_score, risk_score]
    sorted by risk_score descending.
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    max_date = df['date'].max()
    min_date = df['date'].min()
    
    # Time boundaries
    last_30 = max_date - timedelta(days=30)
    prev_30 = last_30 - timedelta(days=30)
    
    results = []
    
    for area in df['area'].unique():
        area_df = df[df['area'] == area]
        total = len(area_df)
        
        # Recent incidents (last 30 days)
        recent = len(area_df[area_df['date'] >= last_30])
        
        # Previous 30-day period
        prev_period = len(area_df[(area_df['date'] >= prev_30) & (area_df['date'] < last_30)])
        
        # Trend: compare recent vs previous
        if prev_period > 0:
            trend_ratio = (recent - prev_period) / prev_period
        elif recent > 0:
            trend_ratio = 1.0
        else:
            trend_ratio = 0.0
        
        if trend_ratio > 0.15:
            trend_direction = "Rising"
        elif trend_ratio < -0.15:
            trend_direction = "Declining"
        else:
            trend_direction = "Stable"
        
        # Recency-weighted score: assign weights by month
        # Most recent month = 6x, oldest month = 1x
        recency_score = 0
        total_days = (max_date - min_date).days
        if total_days > 0:
            for _, row in area_df.iterrows():
                days_ago = (max_date - row['date']).days
                weight = max(1, 6 - (days_ago / (total_days / 6)))
                recency_score += weight
        else:
            recency_score = total
        
        results.append({
            'area': area,
            'total_incidents': total,
            'recent_incidents': recent,
            'trend_direction': trend_direction,
            'trend_ratio': round(trend_ratio, 3),
            'recency_score': round(recency_score, 2)
        })
    
    result_df = pd.DataFrame(results)
    
    # Normalize components to 0-100 scale
    max_total = result_df['total_incidents'].max() if result_df['total_incidents'].max() > 0 else 1
    max_recency = result_df['recency_score'].max() if result_df['recency_score'].max() > 0 else 1
    
    result_df['total_norm'] = (result_df['total_incidents'] / max_total) * 100
    result_df['recency_norm'] = (result_df['recency_score'] / max_recency) * 100
    result_df['trend_norm'] = result_df['trend_ratio'].clip(-1, 1) * 50 + 50  # center at 50
    
    # Combined risk score: weighted combination
    result_df['risk_score'] = (
        0.40 * result_df['recency_norm'] +
        0.30 * result_df['trend_norm'] +
        0.30 * result_df['total_norm']
    ).round(1)
    
    # Sort by risk score
    result_df = result_df.sort_values('risk_score', ascending=False).reset_index(drop=True)
    
    # Clean up intermediate columns
    result_df = result_df[['area', 'total_incidents', 'recent_incidents', 
                           'trend_direction', 'trend_ratio', 'recency_score', 'risk_score']]
    
    return result_df


def get_top5_zones(df):
    """Returns only the top 5 highest-risk zones."""
    scores = compute_risk_scores(df)
    return scores.head(5)


def explain_zone(df, area_name):
    """
    Generate a plain-language explanation for why a specific zone is flagged.
    Returns a dict with structured data and a human-readable explanation.
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['hour'] = df['time'].apply(lambda t: int(t.split(':')[0]))
    
    area_df = df[df['area'] == area_name]
    all_areas_avg = len(df) / df['area'].nunique()
    
    if len(area_df) == 0:
        return {
            'area': area_name,
            'total_incidents': 0,
            'most_common_crime': 'N/A',
            'crime_percentage': 0,
            'peak_hours': 'N/A',
            'peak_days': 'N/A',
            'trend': 'No data',
            'recent_vs_average': 'No data',
            'explanation': f'{area_name} has no recorded incidents in the dataset.'
        }
    
    total = len(area_df)
    
    # Most common crime type
    crime_counts = area_df['crime_type'].value_counts()
    most_common = crime_counts.index[0]
    crime_pct = round(crime_counts.iloc[0] / total * 100)
    
    # Peak hours - find the 3-hour window with most incidents
    hour_counts = area_df['hour'].value_counts().sort_index()
    best_start = 0
    best_count = 0
    for h in range(0, 22):
        window_count = sum(hour_counts.get(h + i, 0) for i in range(3))
        if window_count > best_count:
            best_count = window_count
            best_start = h
    
    def format_hour(h):
        if h == 0:
            return "12 AM"
        elif h < 12:
            return f"{h} AM"
        elif h == 12:
            return "12 PM"
        else:
            return f"{h - 12} PM"
    
    peak_hours = f"{format_hour(best_start)} – {format_hour(best_start + 3)}"
    peak_hours_coverage = round(best_count / total * 100)
    
    # Peak days
    day_counts = area_df['day_of_week'].value_counts()
    top_days = day_counts.head(2).index.tolist()
    peak_days = ", ".join(top_days)
    
    # Trend
    max_date = df['date'].max()
    last_30 = max_date - timedelta(days=30)
    prev_30 = last_30 - timedelta(days=30)
    recent = len(area_df[area_df['date'] >= last_30])
    prev = len(area_df[(area_df['date'] >= prev_30) & (area_df['date'] < last_30)])
    
    if prev > 0:
        trend_pct = round((recent - prev) / prev * 100)
    elif recent > 0:
        trend_pct = 100
    else:
        trend_pct = 0
    
    if trend_pct > 15:
        trend = "Rising"
    elif trend_pct < -15:
        trend = "Declining"
    else:
        trend = "Stable"
    
    # vs station average
    diff_pct = round((total - all_areas_avg) / all_areas_avg * 100)
    if diff_pct > 0:
        vs_avg = f"+{diff_pct}% above station average"
    else:
        vs_avg = f"{diff_pct}% below station average"
    
    # Build explanation
    explanation = (
        f"{area_name} has {total} recorded incidents, predominantly {most_common} ({crime_pct}%). "
        f"Most incidents occur between {peak_hours}, covering {peak_hours_coverage}% of all incidents in this zone. "
        f"{peak_days} show the highest concentration of activity. "
        f"The trend over the last 30 days is {trend.upper()}"
    )
    
    if trend == "Rising":
        explanation += f" with {trend_pct}% more incidents than the prior period. "
    elif trend == "Declining":
        explanation += f" with {abs(trend_pct)}% fewer incidents than the prior period. "
    else:
        explanation += ". "
    
    explanation += f"This zone is {vs_avg}."
    
    return {
        'area': area_name,
        'total_incidents': total,
        'most_common_crime': most_common,
        'crime_percentage': crime_pct,
        'peak_hours': peak_hours,
        'peak_hours_coverage': peak_hours_coverage,
        'peak_days': peak_days,
        'trend': trend,
        'trend_pct': trend_pct,
        'recent_vs_average': vs_avg,
        'explanation': explanation
    }


def suggest_patrol(df, area_name):
    """
    Generate patrol deployment suggestions for a specific zone
    based on temporal crime patterns.
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['hour'] = df['time'].apply(lambda t: int(t.split(':')[0]))
    
    area_df = df[df['area'] == area_name]
    
    if len(area_df) == 0:
        return {
            'area': area_name,
            'suggested_days': [],
            'suggested_time_start': 'N/A',
            'suggested_time_end': 'N/A',
            'priority': 'LOW',
            'coverage_pct': 0,
            'recommendation': f'No incidents recorded in {area_name}. Standard patrol coverage recommended.'
        }
    
    total = len(area_df)
    
    # Find top 2 days
    day_counts = area_df['day_of_week'].value_counts()
    top_days = day_counts.head(2).index.tolist()
    top_days_count = day_counts.head(2).sum()
    
    # Find best 3-hour patrol window
    hour_counts = area_df['hour'].value_counts().sort_index()
    best_start = 19  # default
    best_count = 0
    for h in range(0, 22):
        window_count = sum(hour_counts.get(h + i, 0) for i in range(3))
        if window_count > best_count:
            best_count = window_count
            best_start = h
    
    coverage = round(best_count / total * 100)
    
    def format_time(h):
        return f"{h:02d}:00"
    
    # Priority based on risk
    scores = compute_risk_scores(df)
    area_score = scores[scores['area'] == area_name]['risk_score'].values
    if len(area_score) > 0:
        score = area_score[0]
        if score >= 70:
            priority = "HIGH"
        elif score >= 45:
            priority = "MEDIUM"
        else:
            priority = "LOW"
    else:
        priority = "LOW"
    
    def format_hour_readable(h):
        if h == 0:
            return "12:00 AM"
        elif h < 12:
            return f"{h}:00 AM"
        elif h == 12:
            return "12:00 PM"
        else:
            return f"{h - 12}:00 PM"
    
    start_readable = format_hour_readable(best_start)
    end_readable = format_hour_readable(best_start + 3)
    
    recommendation = (
        f"Deploy additional patrol unit to {area_name} from {start_readable} to "
        f"{end_readable} on {' and '.join(top_days)}. "
        f"This window covers {coverage}% of recorded incidents in this zone. "
        f"Priority: {priority}."
    )
    
    return {
        'area': area_name,
        'suggested_days': top_days,
        'suggested_time_start': format_time(best_start),
        'suggested_time_end': format_time(best_start + 3),
        'priority': priority,
        'coverage_pct': coverage,
        'recommendation': recommendation
    }


def get_summary_stats(df):
    """Get overall dataset summary statistics for dashboard metrics."""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    total_incidents = len(df)
    total_areas = df['area'].nunique()
    most_common_crime = df['crime_type'].value_counts().index[0]
    date_range_start = df['date'].min().strftime('%d %b %Y')
    date_range_end = df['date'].max().strftime('%d %b %Y')
    
    # High-risk zones (risk_score >= 60)
    scores = compute_risk_scores(df)
    high_risk_count = len(scores[scores['risk_score'] >= 60])
    
    return {
        'total_incidents': total_incidents,
        'total_areas': total_areas,
        'most_common_crime': most_common_crime,
        'date_range': f"{date_range_start} – {date_range_end}",
        'high_risk_zones': high_risk_count
    }
