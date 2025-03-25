import pandas as pd
from datetime import datetime

def analyze_driving_data(df):
    """
    Analyze raw driving data and calculate scores for different metrics
    Returns a dictionary with processed trip data
    """
    # Convert timestamp columns to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate trip metrics
    start_time = df['timestamp'].min()
    end_time = df['timestamp'].max()
    duration_hours = (end_time - start_time).total_seconds() / 3600
    
    # Calculate distance (assuming data has latitude/longitude)
    # Simplified calculation - in real app use proper geodetic calculation
    df['distance'] = df['speed_mph'] / 3600  # Approximate miles per second
    distance_miles = df['distance'].sum()
    
    # Basic metrics
    average_speed = df['speed_mph'].mean()
    max_speed = df['speed_mph'].max()
    
    # Detect hard brakes (deceleration > 0.3g)
    df['acceleration'] = df['speed_mph'].diff() / (df['timestamp'].diff().dt.total_seconds() / 3600)
    hard_brakes = (df['acceleration'] < -0.3 * 22.5).sum()  # 0.3g ≈ 22.5 mph/s
    
    # Detect rapid accelerations (acceleration > 0.3g)
    rapid_accelerations = (df['acceleration'] > 0.3 * 22.5).sum()
    
    # Check for night driving (10pm to 6am)
    night_hours = df[(df['timestamp'].dt.hour >= 22) | (df['timestamp'].dt.hour < 6)]
    night_driving = len(night_hours) > 0
    
    # Calculate scores (0-100)
    speed_score = max(0, 100 - (max(0, max_speed - 70)) * 2)  # Penalize speeds over 70mph 
    braking_score = max(0, 100 - hard_brakes * 5)  # 5 points per hard brake
    acceleration_score = max(0, 100 - rapid_accelerations * 5)  # 5 points per rapid acceleration
    
    return {
        'start_time': start_time,
        'end_time': end_time,
        'distance_miles': distance_miles,
        'average_speed': average_speed,
        'max_speed': max_speed,
        'hard_brakes': hard_brakes,
        'rapid_accelerations': rapid_accelerations,
        'night_driving': night_driving,
        'speed_score': speed_score,
        'braking_score': braking_score,
        'acceleration_score': acceleration_score,
    }