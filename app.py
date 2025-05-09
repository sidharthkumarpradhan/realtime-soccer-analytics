import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from api import fetch_football_data, get_leagues, get_seasons, get_teams
from data_processing import (
    define_covid_periods,
    calculate_home_advantage_metrics, 
    analyze_foul_data,
    calculate_win_percentages,
    get_attendance_stats,
    calculate_team_performance
)
from visualization import (
    plot_home_advantage_evolution,
    plot_win_percentages,
    plot_attendance_impact,
    plot_fouls_comparison,
    create_metrics_heatmap,
    plot_home_advantage_time_series
)
from sqlite_db import SQLiteDB
import data_dictionary as dd

# Initialize database connections
sqlite_db = SQLiteDB('football_data.db')

# Set page configuration
st.set_page_config(
    page_title="Home Field Advantage in Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1, h2, h3 {
    color: #1E3A8A;
}
.sub-header {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1E3A8A;
    margin-bottom: 1rem;
}
.metric-card {
    background-color: #F3F4F6;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #1E40AF;
}
.metric-card h3 {
    margin-top: 0;
    font-size: 1.2rem;
}
.footnote {
    font-size: 0.8rem;
    font-style: italic;
    color: #6B7280;
    margin-top: 2rem;
}
.load-button {
    background-color: #1E40AF;
    color: white;
    padding: 1rem 2rem;
    font-size: 1.2rem;
    border-radius: 0.5rem;
    margin-top: 2rem;
    transition: all 0.3s;
}
.load-button:hover {
    background-color: #1E3A8A;
    transform: translateY(-2px);
}
.team-logos {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin: 2rem 0;
}
.team-logo {
    margin: 0.5rem;
    padding: 0.5rem;
    background-color: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.landing-card {
    background-color: white;
    border-radius: 0.5rem;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
}
footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    text-align: center;
    padding: 1rem;
    background-color: #1E3A8A;
    color: white;
    box-shadow: 0 -2px 5px rgba(0,0,0,0.2);
    z-index: 1000;
}
.footer-heart {
    color: #EF4444;
    font-size: 1.2rem;
}
.logo-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}
.logo-item {
    background-color: white;
    border-radius: 0.5rem;
    padding: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
}
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Import logger for debugging
from logger import logger

# Define a function to create the footer
def create_footer():
    logger.info("Displaying footer section")
    footer_html = """
    <footer>
        <p style="margin: 0; font-size: 0.8rem;">Copyright © 2025, Fairfield Dolan School of Business, DATA 6560: Sports Analytics</p>
        <p style="margin: 0; font-size: 0.8rem;">Prof. Bianca Gadzé</p>
        <p style="margin: 0; font-size: 0.8rem;">Made with ❤️ by Charlotte Finnerty, Evan Mansfield, Kiran Malik and Sidharth Kumar Pradhan</p>
    </footer>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
    
    # Add some padding at the bottom to prevent content from being hidden behind the fixed footer
    st.markdown("<div style='margin-bottom:80px;'></div>", unsafe_allow_html=True)

# Sidebar for analysis options
with st.sidebar:
    # Add logo at the top of the sidebar
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/Premier_League_Logo.svg/1200px-Premier_League_Logo.svg.png", width=120)
    st.title("Analysis Options")
    
    # League selection
    st.markdown("### Select League")
    league = st.selectbox(
        "Football League",
        ["Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1"],
        index=0
    )
    
    # Seasons selection
    st.markdown("### Select Seasons")
    available_seasons = get_seasons(league)
    selected_seasons = st.multiselect(
        "Seasons",
        available_seasons,
        default=["2019/2020", "2020/2021", "2021/2022"]
    )
    
    # Team filter (optional)
    st.markdown("### Filter by Team (Optional)")
    teams = get_teams(league)
    team_filter = st.selectbox(
        "Team",
        ["All Teams"] + teams,
        index=0
    )
    
    # Convert "All Teams" to None for API
    if team_filter == "All Teams":
        team_filter = None
    
    # COVID period ranges
    st.markdown("### COVID Period Definition")
    pre_covid_end = st.date_input(
        "Pre-COVID End Date",
        value=date(2020, 3, 1)
    )
    
    during_covid_end = st.date_input(
        "During-COVID End Date",
        value=date(2021, 7, 31)
    )
    
    # Analysis options
    st.markdown("#### Analysis Options")
    rolling_window = st.slider("Rolling Average Window (matches)", 5, 50, 20)
    
    # Load data button in sidebar
    st.markdown("### Data Controls")
    if st.button("Load Real-Time Football Data"):
        if not selected_seasons:
            st.error("Please select at least one season first")
        else:
            st.session_state.data_loaded = True
            st.rerun()
    
    # Reset the SQLite database if needed to fix any schema issues
    if st.button("Reset Database"):
        sqlite_db.reset_database()
        st.success("Database has been reset. Please refresh the page.")
        st.session_state.data_loaded = False
        st.stop()

# Function to load data
def load_data():
    with st.spinner("Fetching football data..."):
        if selected_seasons:
            # First try to get data from the SQLite database
            sqlite_data = sqlite_db.get_matches(league, selected_seasons, team_filter)
            
            # If no data in SQLite, fetch from API
            if sqlite_data.empty:
                data = fetch_football_data(league, selected_seasons, team_filter)
                
                # Add period classification
                data = define_covid_periods(
                    data, 
                    pre_covid_end=pre_covid_end,
                    during_covid_end=during_covid_end
                )
                
                # Save data to SQLite database
                sqlite_db.save_matches(data, league)
            else:
                data = sqlite_data
                
                # Make sure the period column exists and is correct
                if 'period' not in data.columns:
                    data = define_covid_periods(
                        data, 
                        pre_covid_end=pre_covid_end,
                        during_covid_end=during_covid_end
                    )
            return data
        else:
            st.warning("Please select at least one season")
            return pd.DataFrame()

# Main application logic based on data loading state
if st.session_state.data_loaded:
    # Load data when needed
    data = load_data()
    
    # Always display the title and logo at the top
    st.title("European Football Home Field Advantage Analysis")
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/Premier_League_Logo.svg/1200px-Premier_League_Logo.svg.png", width=200)
    
    if not data.empty:
        tabs = st.tabs([
            "Home Advantage Evolution", 
            "Match Statistics", 
            "Attendance Impact", 
            "Team Analysis",
            "Database Explorer",
            "Data Dictionary"
        ])
        
        # Tab 1: Home Advantage Evolution
        with tabs[0]:
            st.markdown('<div class="sub-header">Home Field Advantage Over Time</div>', unsafe_allow_html=True)
            st.markdown("""
            This section examines how home advantage has evolved across different periods: 
            pre-COVID, during COVID (with empty or limited-capacity stadiums), and post-COVID.
            """)
            
            # Calculate key metrics
            home_advantage_metrics = calculate_home_advantage_metrics(data)
            
            # Create metrics cards
            cols = st.columns(3)
            
            periods = home_advantage_metrics['period'].unique()
            
            # Metrics for home win percentage
            for i, period in enumerate(periods):
                period_data = home_advantage_metrics[home_advantage_metrics['period'] == period]
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>{period}</h3>
                        <p>Home Win %: <b>{period_data['home_win_pct'].values[0]:.1f}%</b></p>
                        <p>Away Win %: <b>{period_data['away_win_pct'].values[0]:.1f}%</b></p>
                        <p>Home Advantage: <b>{period_data['home_advantage'].values[0]:.1f}%</b></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Home advantage evolution
            st.markdown("### Home Win Percentage by Period")
            fig_home_adv = plot_home_advantage_evolution(home_advantage_metrics)
            st.plotly_chart(fig_home_adv, use_container_width=True)
            
            # Home vs Away Points
            st.markdown("### Average Points Earned by Home vs Away Teams")
            fig_points = plot_win_percentages(home_advantage_metrics)
            st.plotly_chart(fig_points, use_container_width=True)
            
            # Time series evolution
            st.markdown("### Home Advantage Evolution Over Time")
            fig_time_series = plot_home_advantage_time_series(data, metric='home_win', window=rolling_window)
            st.plotly_chart(fig_time_series, use_container_width=True)
            
            st.markdown("""
            <div class="footnote">
            Note: The time series chart shows a rolling average of the home win percentage over the selected number of matches.
            This helps to visualize the trend more clearly by smoothing out match-to-match variations.
            </div>
            """, unsafe_allow_html=True)
        
        # Tab 2: Match Statistics
        with tabs[1]:
            st.markdown('<div class="sub-header">Match Statistics Analysis</div>', unsafe_allow_html=True)
            st.markdown("""
            This section compares various match statistics between home and away teams across different periods.
            We can examine how factors like fouls, cards, and shots change with or without crowd presence.
            """)
            
            # Create summary metrics cards for Match Statistics
            metric_cols = st.columns(3)
            
            # Add metrics for fouls and cards if available
            if 'fouls_home' in data.columns and 'fouls_away' in data.columns:
                overall_fouls_home = data['fouls_home'].mean()
                overall_fouls_away = data['fouls_away'].mean()
                foul_differential = overall_fouls_home - overall_fouls_away
                
                with metric_cols[0]:
                    st.metric(
                        label="Avg. Home Fouls", 
                        value=f"{overall_fouls_home:.2f}", 
                        delta=f"{foul_differential:.2f}" if foul_differential != 0 else None,
                        delta_color="inverse"  # Red for higher fouls (negative)
                    )
            
            if 'yellow_home' in data.columns and 'yellow_away' in data.columns:
                overall_yellow_home = data['yellow_home'].mean()
                overall_yellow_away = data['yellow_away'].mean()
                yellow_differential = overall_yellow_home - overall_yellow_away
                
                with metric_cols[1]:
                    st.metric(
                        label="Avg. Home Yellow Cards", 
                        value=f"{overall_yellow_home:.2f}", 
                        delta=f"{yellow_differential:.2f}" if yellow_differential != 0 else None,
                        delta_color="inverse"  # Red for higher cards (negative)
                    )
            
            if 'shots_home' in data.columns and 'shots_away' in data.columns:
                overall_shots_home = data['shots_home'].mean()
                overall_shots_away = data['shots_away'].mean()
                shots_differential = overall_shots_home - overall_shots_away
                
                with metric_cols[2]:
                    st.metric(
                        label="Avg. Home Shots", 
                        value=f"{overall_shots_home:.2f}", 
                        delta=f"{shots_differential:.2f}" if shots_differential != 0 else None,
                        delta_color="normal"  # Green for higher shots (positive)
                    )
            
            st.markdown("---")  # Add separator
            
            # Calculate foul data
            foul_data = analyze_foul_data(data)
            
            # Fouls comparison
            st.markdown("### Home vs Away Team Fouls Committed")
            fig_fouls = plot_fouls_comparison(foul_data)
            st.plotly_chart(fig_fouls, use_container_width=True)
            
            # Create correlation heatmaps by period
            st.markdown("### Correlation Between Match Metrics")
            
            # Select metrics for analysis
            metrics = ['home_goals', 'away_goals', 'shots_home', 'shots_away', 
                      'fouls_home', 'fouls_away', 'yellow_home', 'yellow_away']
            
            # Create a row of 3 columns for the three periods
            metric_cols = st.columns(3)
            
            periods = data['period'].unique()
            
            for i, period in enumerate(periods):
                period_data = data[data['period'] == period]
                with metric_cols[i]:
                    st.markdown(f"#### {period} Period")
                    
                    fig = create_metrics_heatmap(period_data, metrics)
                    st.pyplot(fig)
        
        # Tab 3: Attendance Impact
        with tabs[2]:
            st.markdown('<div class="sub-header">Impact of Stadium Attendance</div>', unsafe_allow_html=True)
            st.markdown("""
            This section explores the relationship between stadium attendance and home advantage.
            By comparing periods with different levels of attendance, we can see how crowd support influences match outcomes.
            """)
            
            # Create summary metrics cards for Attendance Impact
            attend_cols = st.columns(3)
            
            # Add attendance metrics if available
            if 'attendance' in data.columns and data['attendance'].notna().any():
                # Get average attendance by period
                period_attendance = data.groupby('period')['attendance'].mean().reset_index()
                
                # Get overall stats
                overall_attendance = data['attendance'].mean()
                max_attendance = data['attendance'].max()
                
                with attend_cols[0]:
                    st.metric(
                        label="Average Attendance", 
                        value=f"{overall_attendance:,.0f}"
                    )
                
                with attend_cols[1]:
                    st.metric(
                        label="Maximum Attendance", 
                        value=f"{max_attendance:,.0f}"
                    )
                
                # Calculate correlation between attendance and home wins
                home_win_corr = data['attendance'].corr(data['home_win'])
                
                with attend_cols[2]:
                    st.metric(
                        label="Correlation with Home Wins", 
                        value=f"{home_win_corr:.2f}",
                        delta=f"{'Positive' if home_win_corr > 0 else 'Negative'} correlation" if not pd.isna(home_win_corr) else None,
                        delta_color="normal" if home_win_corr > 0 else "inverse"
                    )
                
                st.markdown("---")  # Add separator
            else:
                with attend_cols[0]:
                    st.warning("Attendance data not available")
            
            # Calculate attendance stats
            attendance_stats = get_attendance_stats(data)
            
            # Create attendance visualization
            st.markdown("### Attendance vs Home Win Percentage")
            fig_attendance = plot_attendance_impact(attendance_stats, data)
            st.plotly_chart(fig_attendance, use_container_width=True)
            
            # Create a breakdown of attendance levels and outcomes
            st.markdown("### Home Win Percentage by Attendance Level")
            
            # Add some attendance analysis
            if 'attendance' in data.columns and data['attendance'].notna().any():
                # Create attendance bins
                data['attendance_bin'] = pd.cut(
                    data['attendance'], 
                    bins=[0, 10000, 30000, 50000, 100000],
                    labels=['1-10k', '10k-30k', '30k-50k', '50k+']
                )
                
                # Calculate win % by attendance bin
                attendance_analysis = data.groupby('attendance_bin').agg(
                    matches=('home_win', 'count'),
                    home_wins=('home_win', 'sum'),
                    away_wins=('away_win', 'sum'),
                    draws=('draw', 'sum')
                ).reset_index()
                
                attendance_analysis['home_win_pct'] = (attendance_analysis['home_wins'] / attendance_analysis['matches']) * 100
                attendance_analysis['away_win_pct'] = (attendance_analysis['away_wins'] / attendance_analysis['matches']) * 100
                attendance_analysis['draw_pct'] = (attendance_analysis['draws'] / attendance_analysis['matches']) * 100
                
                # Create bar chart
                fig = px.bar(
                    attendance_analysis,
                    x='attendance_bin',
                    y=['home_win_pct', 'draw_pct', 'away_win_pct'],
                    title="Match Outcomes by Attendance Level",
                    labels={'attendance_bin': 'Attendance Level', 'value': 'Percentage (%)', 'variable': 'Outcome'},
                    barmode='stack',
                    color_discrete_map={
                        'home_win_pct': '#1E40AF',
                        'draw_pct': '#9CA3AF',
                        'away_win_pct': '#DC2626'
                    }
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Attendance data is not available for the selected matches")
        
        # Tab 4: Team Analysis
        with tabs[3]:
            st.markdown('<div class="sub-header">Team-Specific Analysis</div>', unsafe_allow_html=True)
            st.markdown("""
            This section provides a deeper analysis for specific teams, showing how their performance 
            changed across different periods, both at home and away.
            """)
            
            # Create summary metrics cards for team analysis
            team_metric_cols = st.columns(4)
            
            if team_filter:
                # Overall team statistics
                team_data = data[(data['home_team'] == team_filter) | (data['away_team'] == team_filter)]
                home_games = data[data['home_team'] == team_filter]
                away_games = data[data['away_team'] == team_filter]
                
                # Home and away win totals
                home_wins = home_games['home_win'].sum() if not home_games.empty else 0
                away_wins = away_games['away_win'].sum() if not away_games.empty else 0
                total_games = len(team_data) if not team_data.empty else 0
                
                with team_metric_cols[0]:
                    st.metric(
                        label=f"{team_filter} Games", 
                        value=f"{total_games}"
                    )
                
                with team_metric_cols[1]:
                    st.metric(
                        label="Home Wins", 
                        value=f"{home_wins}"
                    )
                
                with team_metric_cols[2]:
                    st.metric(
                        label="Away Wins", 
                        value=f"{away_wins}"
                    )
                
                # Overall win percentage
                total_wins = home_wins + away_wins
                win_pct = (total_wins / total_games * 100) if total_games > 0 else 0
                
                with team_metric_cols[3]:
                    st.metric(
                        label="Overall Win %", 
                        value=f"{win_pct:.1f}%"
                    )
                
                st.markdown("---")  # Add separator
                # Team-specific analysis
                home_performance, away_performance = calculate_team_performance(data, team_filter)
                
                st.markdown(f"### {team_filter}'s Performance")
                
                # Display team metrics
                perf_cols = st.columns(2)
                
                with perf_cols[0]:
                    st.markdown("#### Home Performance")
                    st.dataframe(home_performance, use_container_width=True)
                    
                    # Create visualization
                    fig_home = px.bar(
                        home_performance, x='period', y='win_pct',
                        title=f"{team_filter}'s Home Win Percentage",
                        labels={'period': 'Period', 'win_pct': 'Win Percentage (%)'},
                        color='period',
                        color_discrete_map={
                            'Pre-COVID': '#1E40AF',
                            'During-COVID': '#9CA3AF',
                            'Post-COVID': '#047857'
                        }
                    )
                    st.plotly_chart(fig_home, use_container_width=True)
                    
                with perf_cols[1]:
                    st.markdown("#### Away Performance")
                    st.dataframe(away_performance, use_container_width=True)
                    
                    # Create visualization
                    fig_away = px.bar(
                        away_performance, x='period', y='win_pct',
                        title=f"{team_filter}'s Away Win Percentage",
                        labels={'period': 'Period', 'win_pct': 'Win Percentage (%)'},
                        color='period',
                        color_discrete_map={
                            'Pre-COVID': '#1E40AF',
                            'During-COVID': '#9CA3AF',
                            'Post-COVID': '#047857'
                        }
                    )
                    st.plotly_chart(fig_away, use_container_width=True)
                    
                # Calculate home advantage for the team
                team_advantage = pd.DataFrame({
                    'period': home_performance['period'],
                    'home_win_pct': home_performance['win_pct'],
                    'away_win_pct': away_performance['win_pct']
                })
                
                team_advantage['home_advantage'] = team_advantage['home_win_pct'] - team_advantage['away_win_pct']
                
                # Create home advantage visualization
                st.markdown(f"### {team_filter}'s Home Field Advantage")
                
                fig_advantage = px.bar(
                    team_advantage, x='period', y='home_advantage',
                    title=f"{team_filter}'s Home Advantage (Home Win % - Away Win %)",
                    labels={'period': 'Period', 'home_advantage': 'Home Advantage (%)'},
                    color='period',
                    color_discrete_map={
                        'Pre-COVID': '#1E40AF',
                        'During-COVID': '#9CA3AF',
                        'Post-COVID': '#047857'
                    }
                )
                
                # Add a zero line
                fig_advantage.add_hline(y=0, line_dash="dash", line_color="grey")
                
                st.plotly_chart(fig_advantage, use_container_width=True)
                
            else:
                st.info("Select a specific team in the sidebar to view team-specific analysis")
        
        # Tab 5: Database Explorer
        with tabs[4]:
            st.markdown('<div class="sub-header">Database Explorer</div>', unsafe_allow_html=True)
            st.markdown("""
            This section allows you to explore the underlying data and run custom SQL queries.
            Use this to perform your own analysis or export specific datasets.
            """)
            
            # Database statistics
            db_stats = sqlite_db.get_database_stats()
            
            # Create metrics row
            metrics_cols = st.columns(4)
            metrics_cols[0].metric("Total Matches", db_stats['matches_count'])
            metrics_cols[1].metric("Total Teams", db_stats['teams_count'])
            metrics_cols[2].metric("Leagues", len(db_stats['league_counts']))
            metrics_cols[3].metric("Seasons", len(db_stats['season_counts']))
            
            # Database tables
            st.markdown("### Database Schema")
            
            schema_tabs = st.tabs(["Matches Table", "Teams Table"])
            
            with schema_tabs[0]:
                # Show matches table schema
                st.code("""
CREATE TABLE matches (
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
    data_source TEXT,
    data_source_id TEXT,
    last_updated TEXT
)
                """)
            
            with schema_tabs[1]:
                # Show teams table schema
                st.code("""
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    league TEXT NOT NULL,
    data_source TEXT,
    data_source_id TEXT,
    last_updated TEXT
)
                """)
            
            # SQL query section
            st.markdown("### Run Custom SQL Queries")
            st.markdown("""
            Enter a custom SQL query to explore the data. Only SELECT queries are allowed for safety reasons.
            Examples:
            - `SELECT * FROM matches LIMIT 10`
            - `SELECT league, COUNT(*) FROM matches GROUP BY league`
            - `SELECT home_team, AVG(home_goals) FROM matches GROUP BY home_team ORDER BY AVG(home_goals) DESC LIMIT 10`
            """)
            
            # Query input
            custom_query = st.text_area(
                "SQL Query", 
                "SELECT * FROM matches LIMIT 10",
                height=100
            )
            
            # Execute query button
            if st.button("Run Query"):
                with st.spinner("Executing query..."):
                    result = sqlite_db.execute_custom_query(custom_query)
                    st.dataframe(result, use_container_width=True)
                    
                    # Download button
                    if not result.empty:
                        csv = result.to_csv(index=False)
                        st.download_button(
                            "Download Results (CSV)",
                            csv,
                            "query_results.csv",
                            "text/csv",
                            key='download-csv'
                        )
        
        # Tab 6: Data Dictionary
        with tabs[5]:
            st.markdown('<div class="sub-header">Football Data Dictionary</div>', unsafe_allow_html=True)
            st.markdown("""
            This section explains the football metrics and terminology used in this application.
            It's designed to help users who are new to football understand the data and analysis.
            """)
            
            # Create sections for different types of definitions
            dict_tabs = st.tabs(["Column Definitions", "Football Terms", "COVID Periods", "League Information"])
            
            with dict_tabs[0]:
                st.markdown("### Data Column Definitions")
                st.markdown("This table explains all the data columns used in the analysis.")
                
                # Create DataFrame from column definitions
                cols_df = pd.DataFrame([
                    {
                        'Column': col,
                        'Description': details['description'],
                        'Category': details['category'],
                        'Unit': details['unit']
                    }
                    for col, details in dd.COLUMN_DEFINITIONS.items()
                ])
                
                # Group by category for better organization
                for category, group in cols_df.groupby('Category'):
                    st.markdown(f"#### {category}")
                    st.dataframe(
                        group[['Column', 'Description', 'Unit']].reset_index(drop=True),
                        use_container_width=True
                    )
            
            with dict_tabs[1]:
                st.markdown("### Football Terminology")
                st.markdown("Common football terms and their explanations.")
                
                # Create DataFrame from football terms
                terms_df = pd.DataFrame([
                    {'Term': term, 'Definition': definition}
                    for term, definition in dd.FOOTBALL_TERMS.items()
                ])
                
                st.dataframe(terms_df, use_container_width=True)
            
            with dict_tabs[2]:
                st.markdown("### COVID-19 Period Definitions")
                st.markdown("""
                This application divides the analysis into three distinct periods related to the COVID-19 pandemic:
                """)
                
                covid_cols = st.columns(3)
                
                with covid_cols[0]:
                    st.markdown("""
                    #### Pre-COVID
                    - Before March 2020
                    - Normal match conditions
                    - Full stadium attendance
                    - Regular scheduling
                    """)
                    
                with covid_cols[1]:
                    st.markdown("""
                    #### During-COVID
                    - March 2020 to July 2021
                    - Matches behind closed doors or with limited attendance
                    - Compressed scheduling
                    - "Ghost games" with artificial crowd noise on broadcasts
                    - Five substitutions allowed instead of three
                    """)
                    
                with covid_cols[2]:
                    st.markdown("""
                    #### Post-COVID
                    - After July 2021
                    - Return to normal attendance
                    - Some lingering effects
                    - Some changes (like five substitutions) remained in place
                    """)
            
            with dict_tabs[3]:
                st.markdown("### League Information")
                st.markdown("Information about the football leagues included in this analysis.")
                
                # Create DataFrame from league information
                leagues_df = pd.DataFrame([
                    {
                        'League': league,
                        'Country': details['country'],
                        'Teams': details['teams'],
                        'Matches Per Season': details['matches_per_season'],
                        'Description': details['description']
                    }
                    for league, details in dd.LEAGUE_INFO.items()
                ])
                
                st.dataframe(leagues_df, use_container_width=True)
        
        # Add footer at the end of the data analysis section
        create_footer()
    
else:
    # Import the logger for debugging
    from logger import logger
    logger.info("Displaying the welcome page")
    
    # Display welcome page when no data is loaded - using only native Streamlit components
    st.title("European Football Home Field Advantage Analysis")
    
    # Create a landing card with native Streamlit components
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/Premier_League_Logo.svg/1200px-Premier_League_Logo.svg.png", width=300)
    
    st.header("Welcome to Football Home Advantage Analysis")
    
    st.write("This interactive dashboard analyzes the impact of the COVID-19 pandemic on home field advantage in European football leagues.")
    st.write("The analysis covers three distinct periods: Pre-COVID, During-COVID (empty stadiums), and Post-COVID.")
    
    st.subheader("Featured Teams")
    
    # Team logos in a grid layout - updated with more reliable URLs
    team_logos = {
        "Manchester United": "https://upload.wikimedia.org/wikipedia/en/7/7a/Manchester_United_FC_crest.svg",
        "Liverpool": "https://upload.wikimedia.org/wikipedia/en/0/0c/Liverpool_FC.svg",
        "Manchester City": "https://upload.wikimedia.org/wikipedia/en/e/eb/Manchester_City_FC_badge.svg",
        "Chelsea": "https://upload.wikimedia.org/wikipedia/en/c/cc/Chelsea_FC.svg",
        "Arsenal": "https://upload.wikimedia.org/wikipedia/en/5/53/Arsenal_FC.svg",
        "Tottenham Hotspur": "https://upload.wikimedia.org/wikipedia/en/b/b4/Tottenham_Hotspur.svg",
        "Real Madrid": "https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg",
        "Barcelona": "https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg",
        "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg",
        "PSG": "https://upload.wikimedia.org/wikipedia/en/a/a7/Paris_Saint-Germain_F.C..svg",
        # Using the provided URL for Juventus logo
        "Juventus": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg/800px-Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg.png",
    }
    
    # Create team logo display with native Streamlit columns
    logger.info(f"Displaying {len(team_logos)} team logos")
    
    # Create a more structured grid layout with 3 columns (better alignment)
    # Use a container to add some styling and structure
    logo_container = st.container()
    
    with logo_container:
        # Create 3 equal columns for a better looking grid
        cols = st.columns(3)
        
        # Group teams to ensure proper alignment
        for i, (team, logo) in enumerate(team_logos.items()):
            try:
                with cols[i % 3]:
                    # Center align the image and text
                    st.write(f"<div style='text-align: center;'>", unsafe_allow_html=True)
                    st.image(logo, width=80)  # Slightly larger
                    st.caption(team)
                    st.write("</div>", unsafe_allow_html=True)
                    logger.debug(f"Successfully displayed logo for {team}")
            except Exception as e:
                logger.error(f"Error displaying logo for {team}: {e}")
                with cols[i % 3]:
                    st.error(f"Error loading {team} logo")

    # Research highlights using native Streamlit
    st.subheader("Research Highlights")
    
    st.write("This research investigates how the COVID-19 pandemic affected home advantage in European soccer leagues. Key questions include:")
    
    # Display bullet points
    st.markdown("• How did home win percentages change during matches played in empty stadiums?")
    st.markdown("• Did referee decisions (fouls, cards) show different patterns without crowd pressure?")
    st.markdown("• Which teams were most affected by the absence of fans?")
    st.markdown("• Has home advantage returned to pre-pandemic levels?")
    
    # Load data prompt and button
    st.subheader("Select options in the sidebar and click below to start:")
    
    if st.button("Load Real-Time Football Data", use_container_width=True):
        if not selected_seasons:
            st.error("Please select at least one season in the sidebar first")
        else:
            # Set the data loaded flag to true to trigger analysis on next run
            st.session_state.data_loaded = True
            st.rerun()

# Add footer at the end of the welcome page section
create_footer()