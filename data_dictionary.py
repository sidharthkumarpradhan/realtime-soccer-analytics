"""
This module contains the data dictionary definitions for the football data analysis application.
It provides descriptions for each metric and term used in the analysis.
"""

# Dictionary mapping column names to their descriptions and units
COLUMN_DEFINITIONS = {
    # Basic match information
    'date': {
        'description': 'Date when the match was played',
        'category': 'Match Info',
        'unit': 'Date'
    },
    'season': {
        'description': 'Football season (e.g., "2019/2020")',
        'category': 'Match Info',
        'unit': 'Season Year'
    },
    'league': {
        'description': 'Name of the league (e.g., "Premier League", "La Liga")',
        'category': 'Match Info',
        'unit': 'League Name'
    },
    'home_team': {
        'description': 'Name of the team playing at their home stadium',
        'category': 'Match Info',
        'unit': 'Team Name'
    },
    'away_team': {
        'description': 'Name of the team playing away from their home stadium',
        'category': 'Match Info',
        'unit': 'Team Name'
    },
    'matchday': {
        'description': 'Round/matchday number in the season (typically 1-38 in major European leagues)',
        'category': 'Match Info',
        'unit': 'Match Number'
    },
    'attendance': {
        'description': 'Number of spectators present at the match',
        'category': 'Stadium',
        'unit': 'People'
    },
    'period': {
        'description': 'COVID period classification (Pre-COVID, During-COVID, Post-COVID)',
        'category': 'Analysis',
        'unit': 'Period'
    },
    
    # Goals and results
    'home_goals': {
        'description': 'Number of goals scored by the home team',
        'category': 'Goals',
        'unit': 'Goals'
    },
    'away_goals': {
        'description': 'Number of goals scored by the away team',
        'category': 'Goals',
        'unit': 'Goals'
    },
    'home_win': {
        'description': 'Whether the home team won the match (True/False)',
        'category': 'Results',
        'unit': 'Boolean'
    },
    'draw': {
        'description': 'Whether the match ended in a draw (True/False)',
        'category': 'Results',
        'unit': 'Boolean'
    },
    'away_win': {
        'description': 'Whether the away team won the match (True/False)',
        'category': 'Results',
        'unit': 'Boolean'
    },
    
    # Advanced metrics
    'xg_home': {
        'description': 'Expected Goals (xG) for the home team - a statistical measure of the quality of goal-scoring chances',
        'category': 'Advanced',
        'unit': 'Expected Goals'
    },
    'xg_away': {
        'description': 'Expected Goals (xG) for the away team - a statistical measure of the quality of goal-scoring chances',
        'category': 'Advanced',
        'unit': 'Expected Goals'
    },
    'shots_home': {
        'description': 'Number of shots taken by the home team',
        'category': 'Offense',
        'unit': 'Shots'
    },
    'shots_away': {
        'description': 'Number of shots taken by the away team',
        'category': 'Offense',
        'unit': 'Shots'
    },
    'fouls_home': {
        'description': 'Number of fouls committed by the home team',
        'category': 'Discipline',
        'unit': 'Fouls'
    },
    'fouls_away': {
        'description': 'Number of fouls committed by the away team',
        'category': 'Discipline',
        'unit': 'Fouls'
    },
    'corners_home': {
        'description': 'Number of corner kicks awarded to the home team',
        'category': 'Set Pieces',
        'unit': 'Corners'
    },
    'corners_away': {
        'description': 'Number of corner kicks awarded to the away team',
        'category': 'Set Pieces',
        'unit': 'Corners'
    },
    'yellow_home': {
        'description': 'Number of yellow cards received by the home team',
        'category': 'Discipline',
        'unit': 'Cards'
    },
    'yellow_away': {
        'description': 'Number of yellow cards received by the away team',
        'category': 'Discipline',
        'unit': 'Cards'
    },
    'red_home': {
        'description': 'Number of red cards received by the home team',
        'category': 'Discipline',
        'unit': 'Cards'
    },
    'red_away': {
        'description': 'Number of red cards received by the away team',
        'category': 'Discipline',
        'unit': 'Cards'
    },
    
    # Analysis metrics (derived)
    'home_win_pct': {
        'description': 'Percentage of matches won by the home team',
        'category': 'Analysis',
        'unit': 'Percentage'
    },
    'draw_pct': {
        'description': 'Percentage of matches ending in a draw',
        'category': 'Analysis',
        'unit': 'Percentage'
    },
    'away_win_pct': {
        'description': 'Percentage of matches won by the away team',
        'category': 'Analysis',
        'unit': 'Percentage'
    },
    'home_points_avg': {
        'description': 'Average points earned per match by home teams (3 for win, 1 for draw, 0 for loss)',
        'category': 'Analysis',
        'unit': 'Points'
    },
    'away_points_avg': {
        'description': 'Average points earned per match by away teams (3 for win, 1 for draw, 0 for loss)',
        'category': 'Analysis',
        'unit': 'Points'
    },
    'home_advantage': {
        'description': 'Difference between home win percentage and away win percentage',
        'category': 'Analysis',
        'unit': 'Percentage Points'
    },
    'home_goals_avg': {
        'description': 'Average number of goals scored by home teams per match',
        'category': 'Analysis',
        'unit': 'Goals'
    },
    'away_goals_avg': {
        'description': 'Average number of goals scored by away teams per match',
        'category': 'Analysis',
        'unit': 'Goals'
    }
}

# Football terminology explanations
FOOTBALL_TERMS = {
    'Home Field Advantage': 'The benefit that the home team is said to gain over the away team. It may come from fan support, familiarity with the pitch, or psychological factors.',
    'Expected Goals (xG)': 'A statistical measure of the quality of goal-scoring chances and how likely they are to be scored.',
    'Clean Sheet': 'When a team prevents the opposition from scoring any goals during a match.',
    'Matchday': 'A round of fixtures in a league season. Most top European leagues have 38 matchdays in a season.',
    'Set Piece': 'A situation when the ball is returned to open play following a stoppage, such as a corner kick, free kick, or throw-in.',
    'Derby': 'A match between two rival teams, typically from the same city or region.',
    'UEFA': 'Union of European Football Associations, the governing body for football in Europe.',
    'FIFA': 'Fédération Internationale de Football Association, the international governing body for football.',
    'VAR': 'Video Assistant Referee, a match official who reviews decisions made by the head referee using video footage.',
    'Pitch': 'The playing surface for a football match, typically made of grass or artificial turf.',
    'Formation': 'The arrangement of players on the field, usually described by numbers (e.g., 4-4-2, 4-3-3).',
    'Yellow Card': 'A warning given to a player for misconduct. Two yellow cards in the same match result in a red card.',
    'Red Card': 'A penalty that results in a player being ejected from the match, leaving their team to play with one fewer player.',
    'Offside': 'A rule that prevents attacking players from being behind the last defender when the ball is played to them.',
    'Penalty Kick': 'A direct free kick taken from the penalty spot, awarded when a foul occurs in the penalty area.',
    'Goal Difference': 'The difference between goals scored and goals conceded, used as a tiebreaker in league standings.',
    'Relegation': 'When teams at the bottom of the league table are demoted to a lower division at the end of the season.',
    'Promotion': 'When teams at the top of a lower division are elevated to a higher division at the end of the season.',
    'Own Goal': 'When a player accidentally scores a goal against their own team.'
}

# COVID-19 periods explanation
COVID_PERIODS = {
    'Pre-COVID': 'Matches played before March 2020, before pandemic restrictions were implemented in European football.',
    'During-COVID': 'Matches played between March 2020 and July 2021, when most matches were played with limited or no fans in attendance due to pandemic restrictions.',
    'Post-COVID': 'Matches played after July 2021, when most stadiums began allowing fans to return, though sometimes with capacity restrictions.'
}

# League information
LEAGUE_INFO = {
    'Premier League': {
        'country': 'England',
        'teams': 20,
        'matches_per_season': 38,
        'description': 'The top tier of English football, widely regarded as one of the most competitive and popular leagues in the world.'
    },
    'La Liga': {
        'country': 'Spain',
        'teams': 20,
        'matches_per_season': 38,
        'description': 'The top professional football division of the Spanish football league system.'
    },
    'Bundesliga': {
        'country': 'Germany',
        'teams': 18,
        'matches_per_season': 34,
        'description': 'The top tier of German football. Unlike other major European leagues, it has 18 teams instead of 20.'
    },
    'Serie A': {
        'country': 'Italy',
        'teams': 20,
        'matches_per_season': 38,
        'description': 'The top flight of Italian football, known historically for its tactical and defensive style of play.'
    },
    'Ligue 1': {
        'country': 'France',
        'teams': 20,
        'matches_per_season': 38,
        'description': 'The top tier of French football, featuring some of the most talented young players in Europe.'
    }
}