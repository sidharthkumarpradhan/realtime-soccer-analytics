import pandas as pd
import numpy as np
from datetime import datetime

def define_covid_periods(df, pre_covid_end=None, during_covid_end=None):
    """
    Add a column to the dataframe that defines the COVID period for each match:
    - Pre-COVID: Before March 2020 (or custom date)
    - During-COVID: March 2020 to July 2021 (or custom date range)
    - Post-COVID: After July 2021 (or custom date)
    
    Args:
        df (pandas.DataFrame): Match data with a 'date' column
        pre_covid_end (datetime.date, optional): End date for pre-COVID period
        during_covid_end (datetime.date, optional): End date for during-COVID period
        
    Returns:
        pandas.DataFrame: DataFrame with added 'period' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Ensure date is in datetime format
    if not pd.api.types.is_datetime64_dtype(result_df['date']):
        result_df['date'] = pd.to_datetime(result_df['date'])
    
    # Set default dates if not provided
    if pre_covid_end is None:
        pre_covid_end = pd.Timestamp('2020-03-01')
    else:
        pre_covid_end = pd.Timestamp(pre_covid_end)
        
    if during_covid_end is None:
        during_covid_end = pd.Timestamp('2021-07-31')
    else:
        during_covid_end = pd.Timestamp(during_covid_end)
    
    # Add period column
    result_df['period'] = pd.cut(
        result_df['date'],
        bins=[
            pd.Timestamp.min,
            pre_covid_end,
            during_covid_end,
            pd.Timestamp.max
        ],
        labels=['Pre-COVID', 'During-COVID', 'Post-COVID'],
        right=False
    )
    
    return result_df

def calculate_home_advantage_metrics(df):
    """
    Calculate metrics related to home field advantage
    
    Args:
        df (pandas.DataFrame): Match data with period classification
        
    Returns:
        pandas.DataFrame: Aggregated metrics by period
    """
    # Group by period and calculate win percentages
    result = df.groupby('period').agg(
        total_matches=('home_team', 'count'),
        home_wins=('home_win', 'sum'),
        draws=('draw', 'sum'),
        away_wins=('away_win', 'sum'),
        home_goals_avg=('home_goals', 'mean'),
        away_goals_avg=('away_goals', 'mean')
    ).reset_index()
    
    # Calculate percentages
    result['home_win_pct'] = result['home_wins'] / result['total_matches'] * 100
    result['draw_pct'] = result['draws'] / result['total_matches'] * 100
    result['away_win_pct'] = result['away_wins'] / result['total_matches'] * 100
    
    # Calculate points (3 for win, 1 for draw)
    result['home_points_avg'] = (result['home_wins'] * 3 + result['draws']) / result['total_matches']
    result['away_points_avg'] = (result['away_wins'] * 3 + result['draws']) / result['total_matches']
    
    # Calculate home advantage (difference between home and away win %)
    result['home_advantage'] = result['home_win_pct'] - result['away_win_pct']
    
    return result

def analyze_foul_data(df):
    """
    Analyze fouls committed by home and away teams across periods
    
    Args:
        df (pandas.DataFrame): Match data with fouls and period classification
        
    Returns:
        pandas.DataFrame: Aggregated foul statistics by period
    """
    # Check if foul data is available
    if 'fouls_home' not in df.columns or 'fouls_away' not in df.columns:
        # Create empty DataFrame with appropriate columns
        return pd.DataFrame(columns=[
            'period', 'fouls_home_avg', 'fouls_away_avg', 'foul_differential', 
            'yellow_home_avg', 'yellow_away_avg', 'yellow_differential'
        ])
    
    # Group by period and calculate averages
    result = df.groupby('period').agg(
        fouls_home_avg=('fouls_home', 'mean'),
        fouls_away_avg=('fouls_away', 'mean')
    ).reset_index()
    
    # Calculate differentials
    result['foul_differential'] = result['fouls_home_avg'] - result['fouls_away_avg']
    
    # Add card data if available
    if 'yellow_home' in df.columns and 'yellow_away' in df.columns:
        yellow_data = df.groupby('period').agg(
            yellow_home_avg=('yellow_home', 'mean'),
            yellow_away_avg=('yellow_away', 'mean')
        ).reset_index()
        
        # Merge with result
        result = pd.merge(result, yellow_data, on='period')
        
        # Calculate yellow card differential
        result['yellow_differential'] = result['yellow_home_avg'] - result['yellow_away_avg']
    
    return result

def calculate_win_percentages(df):
    """
    Calculate win percentages for home and away teams by period
    
    Args:
        df (pandas.DataFrame): Match data with period classification
        
    Returns:
        tuple: Two DataFrames (home_results, away_results) with win percentages
    """
    # Calculate home results
    home_results = df.groupby('period').agg(
        total_matches=('home_team', 'count'),
        home_wins=('home_win', 'sum'),
        home_draws=('draw', 'sum'),
        home_losses=('away_win', 'sum')
    ).reset_index()
    
    # Calculate percentages
    home_results['win_pct'] = home_results['home_wins'] / home_results['total_matches'] * 100
    home_results['draw_pct'] = home_results['home_draws'] / home_results['total_matches'] * 100
    home_results['loss_pct'] = home_results['home_losses'] / home_results['total_matches'] * 100
    
    # Calculate away results
    away_results = df.groupby('period').agg(
        total_matches=('away_team', 'count'),
        away_wins=('away_win', 'sum'),
        away_draws=('draw', 'sum'),
        away_losses=('home_win', 'sum')
    ).reset_index()
    
    # Calculate percentages
    away_results['win_pct'] = away_results['away_wins'] / away_results['total_matches'] * 100
    away_results['draw_pct'] = away_results['away_draws'] / away_results['total_matches'] * 100
    away_results['loss_pct'] = away_results['away_losses'] / away_results['total_matches'] * 100
    
    return home_results, away_results

def get_attendance_stats(df):
    """
    Calculate attendance statistics by period
    
    Args:
        df (pandas.DataFrame): Match data with attendance and period classification
        
    Returns:
        pandas.DataFrame: Aggregated attendance statistics by period
    """
    # Check if attendance data is available
    if 'attendance' not in df.columns:
        # Create empty DataFrame with appropriate columns
        return pd.DataFrame(columns=[
            'period', 'avg_attendance', 'min_attendance', 'max_attendance', 'std_attendance'
        ])
    
    # Group by period and calculate statistics
    result = df.groupby('period').agg(
        avg_attendance=('attendance', 'mean'),
        min_attendance=('attendance', 'min'),
        max_attendance=('attendance', 'max'),
        std_attendance=('attendance', 'std')
    ).reset_index()
    
    return result

def calculate_team_performance(df, team):
    """
    Calculate performance metrics for a specific team
    
    Args:
        df (pandas.DataFrame): Match data with period classification
        team (str): Team name
        
    Returns:
        tuple: Two DataFrames (home_performance, away_performance)
    """
    # Filter for matches where the team played at home
    home_matches = df[df['home_team'] == team]
    
    # Calculate home performance
    home_performance = home_matches.groupby('period').agg(
        matches_played=('home_team', 'count'),
        goals_scored=('home_goals', 'sum'),
        goals_conceded=('away_goals', 'sum'),
        wins=('home_win', 'sum'),
        draws=('draw', 'sum'),
        losses=('away_win', 'sum')
    ).reset_index()
    
    # Calculate percentages
    home_performance['win_pct'] = home_performance['wins'] / home_performance['matches_played'] * 100
    home_performance['draw_pct'] = home_performance['draws'] / home_performance['matches_played'] * 100
    home_performance['loss_pct'] = home_performance['losses'] / home_performance['matches_played'] * 100
    
    # Calculate points
    home_performance['points'] = home_performance['wins'] * 3 + home_performance['draws']
    home_performance['ppg'] = home_performance['points'] / home_performance['matches_played']
    
    # Calculate goal metrics
    home_performance['goals_per_game'] = home_performance['goals_scored'] / home_performance['matches_played']
    home_performance['conceded_per_game'] = home_performance['goals_conceded'] / home_performance['matches_played']
    home_performance['goal_diff'] = home_performance['goals_per_game'] - home_performance['conceded_per_game']
    
    # Filter for matches where the team played away
    away_matches = df[df['away_team'] == team]
    
    # Calculate away performance
    away_performance = away_matches.groupby('period').agg(
        matches_played=('away_team', 'count'),
        goals_scored=('away_goals', 'sum'),
        goals_conceded=('home_goals', 'sum'),
        wins=('away_win', 'sum'),
        draws=('draw', 'sum'),
        losses=('home_win', 'sum')
    ).reset_index()
    
    # Calculate percentages
    away_performance['win_pct'] = away_performance['wins'] / away_performance['matches_played'] * 100
    away_performance['draw_pct'] = away_performance['draws'] / away_performance['matches_played'] * 100
    away_performance['loss_pct'] = away_performance['losses'] / away_performance['matches_played'] * 100
    
    # Calculate points
    away_performance['points'] = away_performance['wins'] * 3 + away_performance['draws']
    away_performance['ppg'] = away_performance['points'] / away_performance['matches_played']
    
    # Calculate goal metrics
    away_performance['goals_per_game'] = away_performance['goals_scored'] / away_performance['matches_played']
    away_performance['conceded_per_game'] = away_performance['goals_conceded'] / away_performance['matches_played']
    away_performance['goal_diff'] = away_performance['goals_per_game'] - away_performance['conceded_per_game']
    
    return home_performance, away_performance
