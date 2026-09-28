"""
simulator.py — Drishti What-If Event Simulator
Models how upcoming events could shift crime risk across zones.
"""

import pandas as pd
import numpy as np
from analytics import compute_risk_scores


# Event impact multipliers derived from historical data analysis
EVENT_MULTIPLIERS = {
    "Festival": {"base": 1.40, "label": "Festival", "icon": "🎉"},
    "Market Day": {"base": 1.25, "label": "Market Day", "icon": "🏪"},
    "Cricket Match": {"base": 1.30, "label": "Cricket Match", "icon": "🏏"},
    "Political Rally": {"base": 1.35, "label": "Political Rally", "icon": "📢"},
}


def calculate_event_multiplier(df, event_type):
    """
    Calculate the actual event impact multiplier from historical data.
    Compares incident rates on event days vs non-event days.
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    event_days = df[df['nearby_event'] == event_type]
    # 'None' string is read back as NaN by pandas — treat both as no-event days
    non_event_days = df[df['nearby_event'].isna() | (df['nearby_event'] == 'None') | (df['nearby_event'] == 'No Event')]
    
    if len(non_event_days) == 0 or len(event_days) == 0:
        return EVENT_MULTIPLIERS.get(event_type, {"base": 1.2})["base"]
    
    # Calculate average daily incident rate for event vs non-event
    event_dates = event_days['date'].nunique()
    non_event_dates = non_event_days['date'].nunique()
    
    if event_dates == 0 or non_event_dates == 0:
        return EVENT_MULTIPLIERS.get(event_type, {"base": 1.2})["base"]
    
    event_rate = len(event_days) / event_dates
    non_event_rate = len(non_event_days) / non_event_dates
    
    if non_event_rate > 0:
        multiplier = event_rate / non_event_rate
        # Clamp between 1.0 and 2.0 for reasonable bounds
        multiplier = max(1.0, min(2.0, multiplier))
        return round(multiplier, 2)
    
    return EVENT_MULTIPLIERS.get(event_type, {"base": 1.2})["base"]


def simulate_event(df, area_name, event_type):
    """
    Simulate the impact of an upcoming event on a specific zone's risk score.
    
    Args:
        df: Full crime DataFrame
        area_name: Target area (e.g., "Area-12")
        event_type: Event type ("Festival", "Market Day", "Cricket Match", "Political Rally")
    
    Returns:
        dict with simulation results and explanation
    """
    scores = compute_risk_scores(df)
    area_row = scores[scores['area'] == area_name]
    
    if len(area_row) == 0:
        return {
            'area': area_name,
            'event': event_type,
            'original_score': 0,
            'adjusted_score': 0,
            'change_percent': "0%",
            'multiplier': 1.0,
            'explanation': f"No data available for {area_name}.",
            'label': "⚠️ HYPOTHETICAL SCENARIO — not a validated forecast"
        }
    
    original_score = area_row['risk_score'].values[0]
    
    # Get multiplier from historical data
    multiplier = calculate_event_multiplier(df, event_type)
    
    # Apply multiplier
    adjusted_score = round(original_score * multiplier, 1)
    change_pct = round((multiplier - 1) * 100)
    
    event_info = EVENT_MULTIPLIERS.get(event_type, {"label": event_type, "icon": "📌"})
    
    explanation = (
        f"Historical data shows incidents increase by approximately {change_pct}% "
        f"on days with {event_info['label']} events. If a {event_info['label']} is expected "
        f"near {area_name} next week, the demo risk score could rise from {original_score} "
        f"to {adjusted_score}. This is a hypothetical scenario for planning purposes only."
    )
    
    return {
        'area': area_name,
        'event': event_type,
        'event_icon': event_info['icon'],
        'original_score': original_score,
        'adjusted_score': adjusted_score,
        'change_percent': f"+{change_pct}%",
        'multiplier': multiplier,
        'explanation': explanation,
        'label': "⚠️ HYPOTHETICAL SCENARIO — not a validated forecast"
    }


def simulate_all_zones(df, event_type):
    """
    Run What-If simulation across all top zones for a given event type.
    Returns a list of simulation results.
    """
    from analytics import get_top5_zones
    top5 = get_top5_zones(df)
    
    results = []
    for _, row in top5.iterrows():
        result = simulate_event(df, row['area'], event_type)
        results.append(result)
    
    return results
