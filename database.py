import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create SQLAlchemy base
Base = declarative_base()

# Define Match model
class Match(Base):
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    season = Column(String(20), nullable=False)
    league = Column(String(50), nullable=False)
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    home_goals = Column(Integer)
    away_goals = Column(Integer)
    attendance = Column(Integer)
    home_win = Column(Boolean)
    draw = Column(Boolean)
    away_win = Column(Boolean)
    matchday = Column(Integer)
    
    # Extended statistics (may be null)
    shots_home = Column(Integer)
    shots_away = Column(Integer)
    fouls_home = Column(Integer)
    fouls_away = Column(Integer)
    corners_home = Column(Integer)
    corners_away = Column(Integer)
    yellow_home = Column(Integer)
    yellow_away = Column(Integer)
    red_home = Column(Integer)
    red_away = Column(Integer)
    xg_home = Column(Float)
    xg_away = Column(Float)
    
    # API Source tracking
    data_source = Column(String(50))
    data_source_id = Column(String(100))  # ID in the source system
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert the model to a dictionary"""
        return {
            'id': self.id,
            'date': self.date,
            'season': self.season,
            'league': self.league,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'attendance': self.attendance,
            'home_win': self.home_win,
            'draw': self.draw,
            'away_win': self.away_win,
            'matchday': self.matchday,
            'shots_home': self.shots_home,
            'shots_away': self.shots_away,
            'fouls_home': self.fouls_home,
            'fouls_away': self.fouls_away,
            'corners_home': self.corners_home,
            'corners_away': self.corners_away,
            'yellow_home': self.yellow_home,
            'yellow_away': self.yellow_away,
            'red_home': self.red_home,
            'red_away': self.red_away,
            'xg_home': self.xg_home,
            'xg_away': self.xg_away
        }

# Create cached teams model
class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    league = Column(String(50), nullable=False)
    data_source = Column(String(50))
    data_source_id = Column(String(100))
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert the model to a dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'league': self.league
        }

class Database:
    def __init__(self):
        # Get database URL from environment
        self.db_url = os.getenv("DATABASE_URL")
        
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        # Create engine
        self.engine = create_engine(self.db_url)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Create session maker
        self.Session = sessionmaker(bind=self.engine)
    
    def get_matches(self, league, seasons, team=None):
        """
        Get matches from the database
        
        Args:
            league (str): League name
            seasons (list): List of season strings
            team (str, optional): Team name to filter by
            
        Returns:
            pandas.DataFrame: DataFrame of matches
        """
        session = self.Session()
        
        try:
            # Start with base query
            query = session.query(Match).filter(
                Match.league == league,
                Match.season.in_(seasons)
            )
            
            # Add team filter if provided
            if team:
                query = query.filter(
                    (Match.home_team == team) | (Match.away_team == team)
                )
            
            # Execute query
            matches = query.all()
            
            # Convert to dataframe
            if matches:
                match_dicts = [match.to_dict() for match in matches]
                return pd.DataFrame(match_dicts)
            else:
                return pd.DataFrame()
                
        finally:
            session.close()
    
    def save_matches(self, matches_df, league, data_source="API"):
        """
        Save matches to the database
        
        Args:
            matches_df (pandas.DataFrame): DataFrame of matches
            league (str): League name
            data_source (str): Source of the data (e.g., "football-data.org")
        """
        if matches_df.empty:
            return
            
        session = self.Session()
        
        try:
            # Add league column if not present
            if 'league' not in matches_df.columns:
                matches_df['league'] = league
            
            # Add data source column if not present
            if 'data_source' not in matches_df.columns:
                matches_df['data_source'] = data_source
                
            # Convert date column to datetime if it's not already
            if 'date' in matches_df.columns and not pd.api.types.is_datetime64_dtype(matches_df['date']):
                matches_df['date'] = pd.to_datetime(matches_df['date'])
            
            # For each match, check if it exists and update or insert
            for _, row in matches_df.iterrows():
                # Create key fields to check for existence
                match_date = row.get('date')
                home_team = row.get('home_team')
                away_team = row.get('away_team')
                season = row.get('season')
                
                # Skip if missing required data
                if not all([match_date, home_team, away_team, season]):
                    continue
                
                # Check if match already exists
                existing_match = session.query(Match).filter(
                    Match.date == match_date,
                    Match.home_team == home_team,
                    Match.away_team == away_team,
                    Match.season == season
                ).first()
                
                if existing_match:
                    # Update existing match
                    for key, value in row.items():
                        if hasattr(existing_match, key) and key not in ['id']:
                            setattr(existing_match, key, value)
                    # Update the last_updated field
                    setattr(existing_match, 'last_updated', datetime.utcnow())
                else:
                    # Create new match
                    match_data = {k: v for k, v in row.items() if k in Match.__table__.columns.keys() and k != 'id'}
                    match_data['last_updated'] = datetime.utcnow()
                    new_match = Match(**match_data)
                    session.add(new_match)
            
            # Commit changes
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_teams(self, league):
        """
        Get teams for a league from the database
        
        Args:
            league (str): League name
            
        Returns:
            list: List of team names
        """
        session = self.Session()
        
        try:
            # Query teams
            teams = session.query(Team).filter(Team.league == league).all()
            
            # Return team names
            return [team.name for team in teams]
            
        finally:
            session.close()
    
    def save_teams(self, teams, league, data_source="API"):
        """
        Save teams to the database
        
        Args:
            teams (list): List of team names
            league (str): League name
            data_source (str): Source of the data
        """
        if not teams:
            return
            
        session = self.Session()
        
        try:
            # Get existing teams for this league
            existing_teams = {team.name: team for team in session.query(Team).filter(Team.league == league).all()}
            
            # For each team, update or insert
            for team_name in teams:
                if team_name in existing_teams:
                    # Update the last_updated field
                    setattr(existing_teams[team_name], 'last_updated', datetime.utcnow())
                else:
                    # Create new team
                    new_team = Team(
                        name=team_name,
                        league=league,
                        data_source=data_source,
                        last_updated=datetime.utcnow()
                    )
                    session.add(new_team)
            
            # Commit changes
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

# Create singleton instance
db = Database()