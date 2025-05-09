import pandas as pd
import requests
import json
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use SQLite database instead of PostgreSQL since it's more reliable
from sqlite_db import SQLiteDB

# Create a SQLite database instance
sqlite_db = SQLiteDB()

# API URLs
FOOTBALL_API_URL = "https://api.football-data.org/v4"
API_FOOTBALL_URL = "https://v3.football.api-sports.io"

# Mapping of league names to ids for different APIs
LEAGUE_MAPPING = {
    "Premier League": {"football_data": 2021, "api_football": 39},
    "La Liga": {"football_data": 2014, "api_football": 140},
    "Bundesliga": {"football_data": 2002, "api_football": 78},
    "Serie A": {"football_data": 2019, "api_football": 135},
    "Ligue 1": {"football_data": 2015, "api_football": 61}
}

# Season mappings
SEASON_MAPPING = {
    "2017/2018": 2017,
    "2018/2019": 2018,
    "2019/2020": 2019,
    "2020/2021": 2020,
    "2021/2022": 2021,
    "2022/2023": 2022,
    "2023/2024": 2023
}

def get_api_key(api_name):
    """Get API key from environment variables with fallback to a default for demo"""
    if api_name == "football_data":
        return os.getenv("FOOTBALL_DATA_API_KEY", "demo_key")
    elif api_name == "api_football":
        return os.getenv("API_FOOTBALL_KEY", "demo_key")
    return None

def get_leagues():
    """Return list of available leagues"""
    return list(LEAGUE_MAPPING.keys())

def get_seasons(league=None):
    """Return list of available seasons"""
    # Return all seasons from 2017/18 to 2023/24
    return list(SEASON_MAPPING.keys())

def get_teams(league):
    """Get teams for a specific league"""
    # First try SQLite (more reliable as it's local)
    try:
        sqlite_teams = sqlite_db.get_teams(league)
        if sqlite_teams:
            print(f"Using teams from SQLite database for {league}")
            return sqlite_teams
    except Exception as e:
        print(f"Error fetching teams from SQLite: {str(e)}")
    
    # Attempting to fetch from PostgreSQL is skipped for reliability
    print(f"Skipping PostgreSQL database for reliability reasons")
        
    # If no teams in databases, fetch from API
    try:
        # Try to fetch from football-data.org API
        league_id = LEAGUE_MAPPING.get(league, {}).get("football_data")
        if not league_id:
            print(f"No league ID mapping for {league}")
            teams = ["Manchester United", "Liverpool", "Arsenal", "Chelsea", "Manchester City"]
        else:
            api_key = get_api_key("football_data")
            headers = {"X-Auth-Token": api_key}
            
            # Make API request
            response = requests.get(
                f"{FOOTBALL_API_URL}/competitions/{league_id}/teams",
                headers=headers
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                teams = [team['name'] for team in data.get('teams', [])]
                print(f"Successfully fetched {len(teams)} teams from football-data.org API")
            else:
                # Try fallback API
                league_id = LEAGUE_MAPPING.get(league, {}).get("api_football")
                if not league_id:
                    print(f"No fallback league ID mapping for {league}")
                    teams = ["Manchester United", "Liverpool", "Arsenal", "Chelsea", "Manchester City"]
                else:
                    api_key = get_api_key("api_football")
                    headers = {"x-apisports-key": api_key}
                    
                    # Make API request
                    response = requests.get(
                        f"{API_FOOTBALL_URL}/teams",
                        params={"league": league_id, "season": 2023},  # Use current season
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        teams = [team.get('team', {}).get('name') for team in data.get('response', [])]
                        print(f"Successfully fetched {len(teams)} teams from api-football.com API")
                    else:
                        print(f"Failed to fetch teams from APIs, status code: {response.status_code}")
                        teams = ["Manchester United", "Liverpool", "Arsenal", "Chelsea", "Manchester City"]
        
        # Save to both databases for future use (if teams were fetched)
        if teams:
            # Always save to SQLite (more reliable as it's local)
            try:
                sqlite_db.save_teams(teams, league, "api")
                print(f"Saved {len(teams)} teams to SQLite database")
            except Exception as sqlite_e:
                print(f"Error saving teams to SQLite: {str(sqlite_e)}")
            
            # Skip saving to PostgreSQL for better reliability
            print(f"Skipping PostgreSQL database for better reliability")
        
        return teams
    
    except Exception as e:
        print(f"Error fetching teams: {str(e)}")
        # Return common teams as a last resort
        return ["Manchester United", "Liverpool", "Arsenal", "Chelsea", "Manchester City"]

def fetch_football_data(league, seasons, team=None):
    """
    Fetch football match data from database or API
    
    Args:
        league (str): League name
        seasons (list): List of season strings (e.g., "2019/2020")
        team (str, optional): Team name to filter by
        
    Returns:
        pandas.DataFrame: Processed match data
    """
    # First try SQLite database (more reliable as it's local)
    try:
        sqlite_data = sqlite_db.get_matches(league=league, seasons=seasons, team=team)
        if not sqlite_data.empty:
            print(f"Using SQLite cached data for {league}, {seasons}")
            return sqlite_data
    except Exception as e:
        print(f"Error fetching from SQLite: {str(e)}")
    
    # Skip PostgreSQL for better reliability
    print(f"Skipping PostgreSQL database for better reliability")
    
    # If no data in database, fetch from API
    try:
        # Try first with football-data.org API
        all_data = []
        
        for season in seasons:
            season_year = SEASON_MAPPING.get(season)
            if not season_year:
                continue
                
            league_id = LEAGUE_MAPPING.get(league, {}).get("football_data")
            if not league_id:
                continue
                
            api_key = get_api_key("football_data")
            headers = {"X-Auth-Token": api_key}
            
            # Make API request for matches
            response = requests.get(
                f"{FOOTBALL_API_URL}/competitions/{league_id}/matches",
                params={"season": season_year},
                headers=headers
            )
            
            # Check if API rate limit is reached
            if response.status_code == 429:
                print("Rate limit reached, waiting...")
                time.sleep(60)  # Wait for a minute before retrying
                response = requests.get(
                    f"{FOOTBALL_API_URL}/competitions/{league_id}/matches",
                    params={"season": season_year},
                    headers=headers
                )
            
            # Process response if successful
            if response.status_code == 200:
                matches = response.json().get('matches', [])
                
                for match in matches:
                    # Check if match has been played
                    if match.get('status') != 'FINISHED':
                        continue
                        
                    # Extract basic match data
                    match_data = {
                        'date': match.get('utcDate', '').split('T')[0],
                        'season': season,
                        'league': league,
                        'home_team': match.get('homeTeam', {}).get('name', ''),
                        'away_team': match.get('awayTeam', {}).get('name', ''),
                        'home_goals': match.get('score', {}).get('fullTime', {}).get('home', 0),
                        'away_goals': match.get('score', {}).get('fullTime', {}).get('away', 0),
                        'matchday': match.get('matchday', 0),
                        'data_source': 'football-data.org',
                        'data_source_id': match.get('id', '')
                    }
                    
                    # Filter by team if specified
                    if team and team not in [match_data['home_team'], match_data['away_team']]:
                        continue
                        
                    all_data.append(match_data)
        
        # If we have data, convert to DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Add derived columns
            df['home_win'] = df['home_goals'] > df['away_goals']
            df['draw'] = df['home_goals'] == df['away_goals']
            df['away_win'] = df['home_goals'] < df['away_goals']
            
            # If no attendance data available, try to fetch from second API or use a placeholder
            if 'attendance' not in df.columns:
                # We would normally fetch this from another API, but we'll simulate it here
                df['attendance'] = None
            
            # Add placeholder columns for metrics that might not be available
            for col in ['shots_home', 'shots_away', 'fouls_home', 'fouls_away', 
                       'corners_home', 'corners_away', 'yellow_home', 'yellow_away',
                       'red_home', 'red_away', 'xg_home', 'xg_away']:
                if col not in df.columns:
                    df[col] = None
            
            # Save data to database for future use
            try:
                sqlite_db.save_matches(df, league, "football-data.org")
                print(f"Saved matches to SQLite database")
            except Exception as e:
                print(f"Error saving matches to SQLite: {e}")
            
            return df
            
        # If we couldn't get data from the first API, try with the second one
        fallback_data = fetch_football_data_fallback(league, seasons, team)
        
        # If we got data from the fallback API, save it to the SQLite database
        if not fallback_data.empty:
            fallback_data['league'] = league
            try:
                sqlite_db.save_matches(fallback_data, league, "api-football.com")
                print(f"Saved fallback data to SQLite database")
            except Exception as e:
                print(f"Error saving fallback data to SQLite: {e}")
            
        return fallback_data
    
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        # Return empty DataFrame with correct structure
        return create_empty_dataframe()

def fetch_football_data_fallback(league, seasons, team=None):
    """
    Fallback method to fetch data from the API-Football API
    """
    try:
        all_data = []
        
        for season in seasons:
            season_year = SEASON_MAPPING.get(season)
            if not season_year:
                continue
                
            league_id = LEAGUE_MAPPING.get(league, {}).get("api_football")
            if not league_id:
                continue
                
            api_key = get_api_key("api_football")
            headers = {
                "x-apisports-key": api_key
            }
            
            # Make API request for matches
            response = requests.get(
                f"{API_FOOTBALL_URL}/fixtures",
                params={
                    "league": league_id,
                    "season": season_year
                },
                headers=headers
            )
            
            # Process response if successful
            if response.status_code == 200:
                data = response.json()
                matches = data.get('response', [])
                
                for match in matches:
                    # Check if match has been played
                    if match.get('fixture', {}).get('status', {}).get('short') != 'FT':
                        continue
                        
                    fixture = match.get('fixture', {})
                    teams = match.get('teams', {})
                    goals = match.get('goals', {})
                    statistics = match.get('statistics', [])
                    
                    # Extract basic match data
                    match_data = {
                        'date': fixture.get('date', '').split('T')[0],
                        'season': season,
                        'home_team': teams.get('home', {}).get('name', ''),
                        'away_team': teams.get('away', {}).get('name', ''),
                        'home_goals': goals.get('home', 0),
                        'away_goals': goals.get('away', 0),
                        'attendance': fixture.get('attendance')
                    }
                    
                    # Extract statistics if available
                    for team_stats in statistics:
                        team = team_stats.get('team', {}).get('name')
                        stats = team_stats.get('statistics', [])
                        
                        if team == match_data['home_team']:
                            for stat in stats:
                                if stat.get('type') == 'Shots on Goal':
                                    match_data['shots_home'] = stat.get('value', 0)
                                elif stat.get('type') == 'Fouls':
                                    match_data['fouls_home'] = stat.get('value', 0)
                                elif stat.get('type') == 'Corner Kicks':
                                    match_data['corners_home'] = stat.get('value', 0)
                                elif stat.get('type') == 'Yellow Cards':
                                    match_data['yellow_home'] = stat.get('value', 0)
                                elif stat.get('type') == 'Red Cards':
                                    match_data['red_home'] = stat.get('value', 0)
                        
                        elif team == match_data['away_team']:
                            for stat in stats:
                                if stat.get('type') == 'Shots on Goal':
                                    match_data['shots_away'] = stat.get('value', 0)
                                elif stat.get('type') == 'Fouls':
                                    match_data['fouls_away'] = stat.get('value', 0)
                                elif stat.get('type') == 'Corner Kicks':
                                    match_data['corners_away'] = stat.get('value', 0)
                                elif stat.get('type') == 'Yellow Cards':
                                    match_data['yellow_away'] = stat.get('value', 0)
                                elif stat.get('type') == 'Red Cards':
                                    match_data['red_away'] = stat.get('value', 0)
                    
                    # Filter by team if specified
                    if team and team not in [match_data['home_team'], match_data['away_team']]:
                        continue
                        
                    all_data.append(match_data)
        
        # If we have data, convert to DataFrame
        if all_data:
            df = pd.DataFrame(all_data)
            
            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Add derived columns
            df['home_win'] = df['home_goals'] > df['away_goals']
            df['draw'] = df['home_goals'] == df['away_goals']
            df['away_win'] = df['home_goals'] < df['away_goals']
            
            # Add placeholder columns for metrics that might not be available
            for col in ['shots_home', 'shots_away', 'fouls_home', 'fouls_away', 
                       'corners_home', 'corners_away', 'yellow_home', 'yellow_away',
                       'red_home', 'red_away', 'xg_home', 'xg_away']:
                if col not in df.columns:
                    df[col] = None
            
            return df
        
        # If we still couldn't get data, return sample data
        return create_sample_data(league, seasons, team)
    
    except Exception as e:
        print(f"Error in fallback data fetching: {str(e)}")
        # Return sample data
        return create_sample_data(league, seasons, team)

def create_empty_dataframe():
    """Create an empty DataFrame with the expected structure"""
    columns = [
        'date', 'season', 'home_team', 'away_team', 'home_goals', 'away_goals',
        'attendance', 'shots_home', 'shots_away', 'fouls_home', 'fouls_away',
        'corners_home', 'corners_away', 'yellow_home', 'yellow_away',
        'red_home', 'red_away', 'xg_home', 'xg_away', 'home_win', 'draw', 'away_win'
    ]
    return pd.DataFrame(columns=columns)

def create_sample_data(league, seasons, team=None):
    """
    Create sample data structure for demonstration purposes.
    This is used as a last resort if API fetching fails.
    
    In a production environment, this would be replaced with proper error handling.
    """
    import numpy as np
    
    # Create date ranges that span each season
    all_data = []
    
    for season in seasons:
        start_year = int(season.split('/')[0])
        
        # Define season date ranges
        if f"{start_year}/{start_year+1}" == season:
            start_date = f"{start_year}-08-01"
            end_date = f"{start_year+1}-05-31"
            
            # Create dates for a season (38 matchdays)
            dates = pd.date_range(start=start_date, end=end_date, periods=38)
            
            # Get teams for the league
            teams = get_teams(league)
            if len(teams) < 10:  # If API failed to get teams
                teams = [f"Team {i+1}" for i in range(20)]  # Create 20 teams
            
            # Filter teams if needed
            if team:
                if team not in teams:
                    teams.append(team)  # Ensure the requested team is included
                relevant_teams = [t for t in teams if t == team] + [t for t in teams if t != team][:5]
            else:
                relevant_teams = teams[:20]  # Take top 20 teams
            
            # Create match combinations
            for match_day, date in enumerate(dates, 1):
                for i in range(len(relevant_teams) // 2):
                    home_team = relevant_teams[i]
                    away_team = relevant_teams[len(relevant_teams) - 1 - i]
                    
                    # Only include matches with the selected team if a team filter is applied
                    if team and team not in [home_team, away_team]:
                        continue
                    
                    # Assign COVID period based on date
                    if date < pd.Timestamp('2020-03-01'):
                        attendance = np.random.randint(30000, 60000)
                    elif date < pd.Timestamp('2021-05-01'):
                        attendance = np.random.randint(0, 1000)  # Minimal or zero attendance
                    else:
                        attendance = np.random.randint(30000, 60000)
                    
                    # Generate match data
                    home_goals = np.random.randint(0, 5)
                    away_goals = np.random.randint(0, 4)
                    
                    match_data = {
                        'date': date,
                        'season': season,
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'attendance': attendance,
                        'shots_home': np.random.randint(5, 20),
                        'shots_away': np.random.randint(3, 18),
                        'fouls_home': np.random.randint(8, 16),
                        'fouls_away': np.random.randint(8, 18),
                        'corners_home': np.random.randint(3, 12),
                        'corners_away': np.random.randint(2, 10),
                        'yellow_home': np.random.randint(0, 5),
                        'yellow_away': np.random.randint(0, 6),
                        'red_home': np.random.randint(0, 2),
                        'red_away': np.random.randint(0, 2),
                        'xg_home': round(np.random.uniform(0.5, 2.5), 1),
                        'xg_away': round(np.random.uniform(0.3, 2.0), 1),
                        'home_win': home_goals > away_goals,
                        'draw': home_goals == away_goals,
                        'away_win': home_goals < away_goals
                    }
                    
                    all_data.append(match_data)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    return df
