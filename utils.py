import pandas as pd
import numpy as np
from datetime import datetime

def define_covid_periods(df):
    """
    Add a column to the dataframe that defines the COVID period for each match:
    - Pre-COVID: Before March 2020
    - During-COVID: March 2020 to July 2021 (approximate)
    - Post-COVID: After July 2021
    
    Args:
        df (pandas.DataFrame): Match data with a 'date' column
        
    Returns:
        pandas.DataFrame: DataFrame with added 'period' column
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Ensure date is in datetime format
    if 'date' in result_df.columns:
        if not pd.api.types.is_datetime64_dtype(result_df['date']):
            result_df['date'] = pd.to_datetime(result_df['date'])
    else:
        # Create a date column from season information if possible
        if 'season' in result_df.columns:
            # Extract start year from season (assuming format like "2019/2020")
            result_df['start_year'] = result_df['season'].str.split('/').str[0]
            # Create approximate dates (middle of season)
            result_df['date'] = pd.to_datetime(result_df['start_year'].astype(int) + 0.5, format='%Y')
    
    # Process scoring data
    process_scoring_columns(result_df)
    
    # Add period column
    result_df['period'] = pd.cut(
        result_df['date'],
        bins=[
            pd.Timestamp.min,
            pd.Timestamp('2020-03-01'),
            pd.Timestamp('2021-07-31'),
            pd.Timestamp.max
        ],
        labels=['Pre-COVID', 'During-COVID', 'Post-COVID'],
        right=False
    )
    
    return result_df

def process_scoring_columns(df):
    """
    Process scoring columns to ensure they have consistent names and types
    
    Args:
        df (pandas.DataFrame): Match data
    """
    # List of possible column mappings
    column_mappings = {
        'score': ('home_goals', 'away_goals'),  # If score is in format "2-1"
        'fthg': 'home_goals',   # Full Time Home Goals
        'ftag': 'away_goals',   # Full Time Away Goals
        'hg': 'home_goals',     # Home Goals
        'ag': 'away_goals',     # Away Goals
        'xg': 'xg_home',        # Expected goals home
        'xg.1': 'xg_away',      # Expected goals away
        'hf': 'fouls_home',     # Home Fouls
        'af': 'fouls_away',     # Away Fouls
        'hy': 'yellow_home',    # Home Yellows
        'ay': 'yellow_away',    # Away Yellows
        'hr': 'red_home',       # Home Reds
        'ar': 'red_away',       # Away Reds
        'hs': 'shots_home',     # Home Shots
        'as': 'shots_away',     # Away Shots
        'hc': 'corners_home',   # Home Corners
        'ac': 'corners_away'    # Away Corners
    }
    
    # Process each column mapping
    for old_col, new_col in column_mappings.items():
        if old_col in df.columns:
            if old_col == 'score' and isinstance(new_col, tuple):
                # Handle score column (format like "2-1")
                if df[old_col].dtype == 'object':
                    try:
                        # Split score and create home_goals and away_goals columns
                        score_split = df[old_col].str.split('–|–|-', expand=True)
                        if len(score_split.columns) >= 2:
                            df['home_goals'] = pd.to_numeric(score_split[0], errors='coerce')
                            df['away_goals'] = pd.to_numeric(score_split[1], errors='coerce')
                    except:
                        # If split fails, keep existing columns
                        pass
            else:
                # Simply rename column
                df[new_col] = df[old_col]
    
    # Ensure core columns exist with correct types
    for col in ['home_goals', 'away_goals']:
        if col not in df.columns:
            df[col] = np.nan
        else:
            # Convert to numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Create derived columns
    df['home_win'] = df['home_goals'] > df['away_goals']
    df['draw'] = df['home_goals'] == df['away_goals']
    df['away_win'] = df['home_goals'] < df['away_goals']

def format_date(date_str):
    """
    Format date string in a consistent way
    
    Args:
        date_str (str): Date string in various formats
        
    Returns:
        str: Formatted date string
    """
    try:
        # Try to parse the date
        date_obj = pd.to_datetime(date_str)
        return date_obj.strftime('%Y-%m-%d')
    except:
        return date_str

def convert_attendance(value):
    """
    Convert attendance values to numeric
    
    Args:
        value: Attendance value that could be in different formats
        
    Returns:
        float: Numeric attendance value
    """
    if pd.isna(value):
        return np.nan
        
    if isinstance(value, (int, float)):
        return value
        
    try:
        # Remove commas and try to convert to number
        clean_value = str(value).replace(',', '')
        return float(clean_value)
    except:
        return np.nan

def team_name_standardizer(team_name):
    """
    Standardize team names to handle variations
    
    Args:
        team_name (str): Original team name
        
    Returns:
        str: Standardized team name
    """
    if not isinstance(team_name, str):
        return team_name
        
    # Dictionary of common variations and their standard forms
    variations = {
        'Man United': 'Manchester United',
        'Man Utd': 'Manchester United',
        'Man City': 'Manchester City',
        'Spurs': 'Tottenham',
        'Tottenham Hotspur': 'Tottenham',
        'Wolves': 'Wolverhampton',
        'Newcastle': 'Newcastle United',
        'Brighton': 'Brighton & Hove Albion',
        'Leeds': 'Leeds United'
    }
    
    return variations.get(team_name, team_name)

def get_season_year(season_str):
    """
    Extract the starting year from a season string
    
    Args:
        season_str (str): Season in format like "2019/2020"
        
    Returns:
        int: Starting year of the season
    """
    try:
        # Try to extract the first year
        return int(season_str.split('/')[0])
    except:
        # If it fails, try to extract a 4-digit year from the string
        import re
        matches = re.findall(r'\d{4}', str(season_str))
        if matches:
            return int(matches[0])
        return None

def calculate_team_strength(df, team_col='home_team', goals_for_col='home_goals', goals_against_col='away_goals'):
    """
    Calculate team strength based on goal difference
    
    Args:
        df (pandas.DataFrame): Match data
        team_col (str): Column name for team
        goals_for_col (str): Column name for goals scored
        goals_against_col (str): Column name for goals conceded
        
    Returns:
        pandas.DataFrame: DataFrame with team strength metrics
    """
    # Group by team and calculate metrics
    team_stats = df.groupby(team_col).agg(
        matches_played=(goals_for_col, 'count'),
        goals_for=(goals_for_col, 'sum'),
        goals_against=(goals_against_col, 'sum')
    ).reset_index()
    
    # Calculate goal difference and average
    team_stats['goal_difference'] = team_stats['goals_for'] - team_stats['goals_against']
    team_stats['avg_goal_difference'] = team_stats['goal_difference'] / team_stats['matches_played']
    
    return team_stats

def get_match_importance(df, matchday_col='matchday', total_matchdays=38):
    """
    Calculate match importance based on proximity to season end
    
    Args:
        df (pandas.DataFrame): Match data
        matchday_col (str): Column name for matchday
        total_matchdays (int): Total number of matchdays in a season
        
    Returns:
        pandas.Series: Series with importance score
    """
    if matchday_col not in df.columns:
        return pd.Series(index=df.index)
        
    # Calculate importance (higher as season progresses)
    importance = df[matchday_col] / total_matchdays
    
    # Make late-season matches even more important (non-linear importance)
    importance = importance ** 2
    
    return importance
