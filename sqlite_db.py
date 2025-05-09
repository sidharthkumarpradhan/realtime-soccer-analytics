"""
This module provides SQLite database functionality for the football data analysis application.
It allows for efficient storage and querying of football match data.
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime

class SQLiteDB:
    """SQLite database interface for football data"""
    
    def __init__(self, db_path='football_data.db'):
        """Initialize the database connection"""
        self.db_path = db_path
        
        # Connect and create tables initially
        with self._get_connection() as conn:
            self._create_tables(conn)
    
    def _get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self, conn):
        """Create necessary tables if they don't exist"""
        cursor = conn.cursor()
        
        # Create matches table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            season TEXT NOT NULL,
            league TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_goals INTEGER,
            away_goals INTEGER,
            attendance INTEGER,
            home_win INTEGER,
            draw INTEGER,
            away_win INTEGER,
            matchday INTEGER,
            shots_home INTEGER,
            shots_away INTEGER,
            fouls_home INTEGER,
            fouls_away INTEGER,
            corners_home INTEGER,
            corners_away INTEGER,
            yellow_home INTEGER,
            yellow_away INTEGER,
            red_home INTEGER,
            red_away INTEGER,
            xg_home REAL,
            xg_away REAL,
            period TEXT,
            data_source TEXT,
            data_source_id TEXT,
            last_updated TEXT
        )
        ''')
        
        # Create teams table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            league TEXT NOT NULL,
            data_source TEXT,
            data_source_id TEXT,
            last_updated TEXT
        )
        ''')
        
        # Create index for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_league_season ON matches (league, season)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_teams ON matches (home_team, away_team)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_teams_league ON teams (league)")
        
        conn.commit()
    
    def save_matches(self, matches_df, league, data_source="API"):
        """
        Save matches to the SQLite database
        
        Args:
            matches_df (pandas.DataFrame): DataFrame of matches
            league (str): League name
            data_source (str): Source of the data
        """
        if matches_df.empty:
            return
            
        # Ensure all required columns are present
        required_cols = ['date', 'season', 'home_team', 'away_team', 'home_goals', 'away_goals']
        if not all(col in matches_df.columns for col in required_cols):
            raise ValueError("Matches DataFrame is missing required columns")
            
        # Add league column if not present
        if 'league' not in matches_df.columns:
            matches_df['league'] = league
            
        # Add data source columns
        matches_df['data_source'] = data_source
        matches_df['last_updated'] = datetime.utcnow().isoformat()
        
        # Prepare data for SQLite (handle boolean columns)
        for col in ['home_win', 'draw', 'away_win']:
            if col in matches_df.columns:
                matches_df[col] = matches_df[col].astype(int)
        
        # Check for existing matches to avoid duplicates
        try:
            with self._get_connection() as conn:
                # Create a unique match identifier based on key fields
                matches_df['match_key'] = matches_df.apply(
                    lambda row: f"{row['home_team']}_{row['away_team']}_{row['season']}_{row['date']}", 
                    axis=1
                )
                
                # Get existing match keys
                existing_matches = pd.read_sql(
                    "SELECT home_team, away_team, season, date FROM matches WHERE league = ?", 
                    conn, 
                    params=(league,)
                )
                
                if not existing_matches.empty:
                    # Create keys for existing matches
                    existing_matches['match_key'] = existing_matches.apply(
                        lambda row: f"{row['home_team']}_{row['away_team']}_{row['season']}_{row['date']}", 
                        axis=1
                    )
                    
                    # Filter out matches that already exist
                    new_matches = matches_df[~matches_df['match_key'].isin(existing_matches['match_key'])]
                    
                    # Drop the temporary key column
                    new_matches = new_matches.drop('match_key', axis=1)
                else:
                    new_matches = matches_df.drop('match_key', axis=1)
                
                # Save only new matches to the database
                if not new_matches.empty:
                    new_matches.to_sql('matches', conn, if_exists='append', index=False)
                    print(f"Added {len(new_matches)} new matches to the database")
                else:
                    print("No new matches to add to the database")
                    
        except Exception as e:
            print(f"Error saving matches: {str(e)}")
        
    def save_teams(self, teams, league, data_source="API"):
        """
        Save teams to the SQLite database
        
        Args:
            teams (list): List of team names
            league (str): League name
            data_source (str): Source of the data
        """
        if not teams:
            return
            
        # Create DataFrame from team list
        teams_df = pd.DataFrame({
            'name': teams,
            'league': league,
            'data_source': data_source,
            'last_updated': datetime.utcnow().isoformat()
        })
        
        with self._get_connection() as conn:
            # Get existing teams
            existing_teams = pd.read_sql("SELECT name FROM teams WHERE league = ?", 
                                        conn, params=(league,))
            
            # Filter out existing teams
            if not existing_teams.empty:
                new_teams_df = teams_df[~teams_df['name'].isin(existing_teams['name'])]
            else:
                new_teams_df = teams_df
                
            # Save to database if there are new teams
            if not new_teams_df.empty:
                new_teams_df.to_sql('teams', conn, if_exists='append', index=False)
    
    def get_matches(self, league=None, seasons=None, team=None):
        """
        Get matches from the SQLite database
        
        Args:
            league (str, optional): League name to filter by
            seasons (list, optional): List of seasons to filter by
            team (str, optional): Team name to filter by
            
        Returns:
            pandas.DataFrame: DataFrame of matches
        """
        query = "SELECT * FROM matches"
        where_clauses = []
        params = []
        
        # Add filters
        if league:
            where_clauses.append("league = ?")
            params.append(league)
            
        if seasons:
            placeholders = ','.join(['?'] * len(seasons))
            where_clauses.append(f"season IN ({placeholders})")
            params.extend(seasons)
            
        if team:
            where_clauses.append("(home_team = ? OR away_team = ?)")
            params.extend([team, team])
            
        # Combine filters
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Create empty dataframe as default return value
        empty_df = pd.DataFrame()
        
        try:
            with self._get_connection() as conn:
                # Execute query
                df = pd.read_sql(query, conn, params=params)
                
                # Convert boolean columns
                for col in ['home_win', 'draw', 'away_win']:
                    if col in df.columns:
                        df[col] = df[col].astype(bool)
                        
                # Convert date to datetime
                if 'date' in df.columns and not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                
                return df
        except Exception as e:
            print(f"Error fetching matches: {str(e)}")
            return empty_df
    
    def get_teams(self, league=None):
        """
        Get teams from the SQLite database
        
        Args:
            league (str, optional): League name to filter by
            
        Returns:
            list: List of team names
        """
        query = "SELECT name FROM teams"
        params = []
        
        if league:
            query += " WHERE league = ?"
            params.append(league)
        
        teams = []    
        try:
            with self._get_connection() as conn:
                # Execute query
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # Get team names
                teams = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching teams: {str(e)}")
            
        return teams
    
    def execute_custom_query(self, query, params=None):
        """
        Execute a custom SQL query
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
            
        Returns:
            pandas.DataFrame: Query results
        """
        if params is None:
            params = ()
            
        # Check if query is read-only
        if not query.strip().lower().startswith(('select', 'pragma', 'explain')):
            raise ValueError("Only SELECT queries are allowed for safety reasons")
            
        try:
            # Execute query
            with self._get_connection() as conn:
                return pd.read_sql(query, conn, params=params)
        except Exception as e:
            # Return error message as DataFrame
            return pd.DataFrame({'Error': [str(e)]})
    
    def get_database_stats(self):
        """
        Get statistics about the database
        
        Returns:
            dict: Database statistics
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get table counts
                cursor.execute("SELECT COUNT(*) FROM matches")
                matches_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM teams")
                teams_count = cursor.fetchone()[0]
                
                # Get league counts
                cursor.execute("SELECT league, COUNT(*) FROM matches GROUP BY league")
                league_counts = dict(cursor.fetchall())
                
                # Get season counts
                cursor.execute("SELECT season, COUNT(*) FROM matches GROUP BY season")
                season_counts = dict(cursor.fetchall())
                
                # Get database file size
                db_size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
                
                return {
                    'matches_count': matches_count,
                    'teams_count': teams_count,
                    'league_counts': league_counts,
                    'season_counts': season_counts,
                    'database_size_mb': round(db_size_mb, 2)
                }
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
            return {
                'matches_count': 0,
                'teams_count': 0,
                'league_counts': {},
                'season_counts': {},
                'database_size_mb': 0
            }

    def reset_database(self):
        """
        Reset the database by removing the file and recreating the tables
        """
        try:
            # Close any existing connections
            if os.path.exists(self.db_path):
                # Remove the file
                os.remove(self.db_path)
                print(f"Database file {self.db_path} removed")
                
            # Create new database with updated schema
            with self._get_connection() as conn:
                self._create_tables(conn)
                print("Database recreated with updated schema")
                
            return True
        except Exception as e:
            print(f"Error resetting database: {str(e)}")
            return False

# Create a singleton instance
sqlite_db = SQLiteDB()