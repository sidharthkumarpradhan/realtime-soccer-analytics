import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from plotly.subplots import make_subplots

def plot_home_advantage_evolution(home_advantage_data):
    """
    Create a bar chart showing the evolution of home win percentage
    
    Args:
        home_advantage_data (pandas.DataFrame): Aggregated metrics by period
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Create figure
    fig = go.Figure()
    
    # Add bars for home wins, draws, and away wins
    fig.add_trace(go.Bar(
        x=home_advantage_data['period'],
        y=home_advantage_data['home_win_pct'],
        name='Home Wins',
        marker_color='#1E88E5'
    ))
    
    fig.add_trace(go.Bar(
        x=home_advantage_data['period'],
        y=home_advantage_data['draw_pct'],
        name='Draws',
        marker_color='#FFC107'
    ))
    
    fig.add_trace(go.Bar(
        x=home_advantage_data['period'],
        y=home_advantage_data['away_win_pct'],
        name='Away Wins',
        marker_color='#EF5350'
    ))
    
    # Update layout
    fig.update_layout(
        barmode='group',
        xaxis_title='Period',
        yaxis_title='Percentage of Matches',
        legend_title="Match Outcome",
        hovermode="x unified",
        height=500
    )
    
    return fig

def plot_win_percentages(home_advantage_data):
    """
    Create a bar chart showing average points earned by home vs away teams
    
    Args:
        home_advantage_data (pandas.DataFrame): Aggregated metrics by period
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    # Create figure
    fig = go.Figure()
    
    # Add bars for home and away points
    fig.add_trace(go.Bar(
        x=home_advantage_data['period'],
        y=home_advantage_data['home_points_avg'],
        name='Home Team',
        marker_color='#1E88E5'
    ))
    
    fig.add_trace(go.Bar(
        x=home_advantage_data['period'],
        y=home_advantage_data['away_points_avg'],
        name='Away Team',
        marker_color='#FFC107'
    ))
    
    # Add home advantage line (differential)
    fig.add_trace(go.Scatter(
        x=home_advantage_data['period'],
        y=home_advantage_data['home_points_avg'] - home_advantage_data['away_points_avg'],
        name='Advantage',
        mode='lines+markers',
        line=dict(color='#4CAF50', width=3),
        yaxis='y2'
    ))
    
    # Update layout with secondary y-axis
    fig.update_layout(
        barmode='group',
        xaxis_title='Period',
        yaxis_title='Average Points per Match',
        yaxis2=dict(
            title=dict(
                text='Home Advantage (Points)',
                font=dict(color='#4CAF50')
            ),
            tickfont=dict(color='#4CAF50'),
            overlaying='y',
            side='right'
        ),
        legend_title="",
        hovermode="x unified",
        height=500
    )
    
    return fig

def plot_attendance_impact(attendance_data, match_data):
    """
    Create a chart showing the relationship between attendance and match outcomes
    
    Args:
        attendance_data (pandas.DataFrame): Attendance statistics by period
        match_data (pandas.DataFrame): Full match data
        
    Returns:
        plotly.graph_objects.Figure: Attendance impact figure
    """
    # Check if attendance data is available
    if 'attendance' not in match_data.columns or match_data['attendance'].isnull().all():
        # Create an info figure
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="Attendance data not available",
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(height=500)
        return fig
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bar chart for average attendance
    fig.add_trace(
        go.Bar(
            x=attendance_data['period'],
            y=attendance_data['avg_attendance'],
            name='Avg. Attendance',
            marker_color='#90CAF9',
            opacity=0.7
        ),
        secondary_y=False
    )
    
    # Add line chart for home win percentage
    home_win_pct = match_data.groupby('period')['home_win'].mean() * 100
    fig.add_trace(
        go.Scatter(
            x=home_win_pct.index,
            y=home_win_pct.values,
            name='Home Win %',
            line=dict(color='#1E88E5', width=3),
            mode='lines+markers'
        ),
        secondary_y=True
    )
    
    # Add line chart for away win percentage
    away_win_pct = match_data.groupby('period')['away_win'].mean() * 100
    fig.add_trace(
        go.Scatter(
            x=away_win_pct.index,
            y=away_win_pct.values,
            name='Away Win %',
            line=dict(color='#EF5350', width=3),
            mode='lines+markers'
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title_text="Stadium Attendance Impact on Match Outcomes",
        xaxis_title="Period",
        legend_title="",
        hovermode="x unified",
        height=500
    )
    
    # Update y-axes
    fig.update_yaxes(
        title_text="Average Attendance", 
        secondary_y=False
    )
    fig.update_yaxes(
        title_text="Win Percentage", 
        secondary_y=True
    )
    
    return fig

def plot_fouls_comparison(foul_data):
    """
    Create a chart comparing fouls by home and away teams
    
    Args:
        foul_data (pandas.DataFrame): Aggregated foul statistics by period
        
    Returns:
        plotly.graph_objects.Figure: Fouls comparison figure
    """
    # Check if foul data is available
    if foul_data.empty:
        # Create an info figure
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="Fouls data not available",
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(height=500)
        return fig
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bar chart for home fouls
    fig.add_trace(
        go.Bar(
            x=foul_data['period'],
            y=foul_data['fouls_home_avg'],
            name='Home Fouls',
            marker_color='#1E88E5'
        ),
        secondary_y=False
    )
    
    # Add bar chart for away fouls
    fig.add_trace(
        go.Bar(
            x=foul_data['period'],
            y=foul_data['fouls_away_avg'],
            name='Away Fouls',
            marker_color='#FFC107'
        ),
        secondary_y=False
    )
    
    # Add line chart for differential
    if 'foul_differential' in foul_data.columns:
        fig.add_trace(
            go.Scatter(
                x=foul_data['period'],
                y=foul_data['foul_differential'],
                name='Differential (Home - Away)',
                line=dict(color='#4CAF50', width=3),
                mode='lines+markers'
            ),
            secondary_y=True
        )
    
    # Update layout
    fig.update_layout(
        barmode='group',
        xaxis_title='Period',
        legend_title="",
        hovermode="x unified",
        height=500
    )
    
    # Update y-axes
    fig.update_yaxes(
        title_text="Average Fouls per Match", 
        secondary_y=False
    )
    fig.update_yaxes(
        title_text="Foul Differential", 
        secondary_y=True
    )
    
    return fig

def create_metrics_heatmap(df, metrics, period_column='period'):
    """
    Create a heatmap showing the correlation between different metrics
    
    Args:
        df (pandas.DataFrame): Match data
        metrics (list): List of metric columns to include
        period_column (str): Column name for the period
        
    Returns:
        matplotlib.figure.Figure: Heatmap figure
    """
    import numpy as np
    import warnings
    
    # Check if all metrics are present
    available_metrics = [m for m in metrics if m in df.columns]
    
    if not available_metrics or df.empty:
        # Create empty figure with message
        fig, ax = plt.subplots(figsize=(10, 1))
        ax.text(0.5, 0.5, "Metrics data not available", 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    # Filter out rows with all NaN values for the metrics
    filtered_df = df.dropna(subset=available_metrics, how='all')
    
    if filtered_df.empty:
        # Create empty figure with message
        fig, ax = plt.subplots(figsize=(10, 1))
        ax.text(0.5, 0.5, "No data available after filtering NaN values", 
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig
    
    # Calculate correlation matrix with warnings suppressed
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Fill NaN values with column means
        metrics_data = filtered_df[available_metrics].fillna(filtered_df[available_metrics].mean())
        # Calculate correlation matrix
        corr_matrix = metrics_data.corr()
    
    # Replace any remaining NaN values with 0 for visualization
    corr_matrix = corr_matrix.fillna(0)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap with more defensive approach
    try:
        sns.heatmap(
            corr_matrix, 
            annot=True, 
            cmap='coolwarm', 
            center=0,
            linewidths=.5,
            ax=ax,
            vmin=-1, vmax=1  # Explicitly set min/max values
        )
        
        # Set title and labels
        ax.set_title("Correlation Matrix of Match Metrics")
    except Exception as e:
        # If heatmap fails, create a simple message
        ax.clear()
        ax.text(0.5, 0.5, f"Could not create heatmap: {str(e)}", 
                ha='center', va='center', fontsize=12)
        ax.axis('off')
    
    return fig

def plot_home_advantage_time_series(df, metric='home_win', window=10):
    """
    Create a time series chart showing the evolution of a metric over time
    
    Args:
        df (pandas.DataFrame): Match data with dates
        metric (str): Column name for the metric to plot
        window (int): Rolling window size for smoothing
        
    Returns:
        plotly.graph_objects.Figure: Time series figure
    """
    # Check if date and metric columns are present
    if 'date' not in df.columns or metric not in df.columns:
        # Create an info figure
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=f"Required data not available ({metric})",
            showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(height=500)
        return fig
    
    # Ensure date is sorted
    df_sorted = df.sort_values('date')
    
    # Calculate rolling average
    rolling_data = df_sorted[metric].rolling(window=window, min_periods=1).mean()
    
    # Create figure
    fig = go.Figure()
    
    # Add scatter plot with rolling average
    fig.add_trace(go.Scatter(
        x=df_sorted['date'],
        y=rolling_data,
        mode='lines',
        name=f'{metric.replace("_", " ").title()} ({window}-match rolling avg)',
        line=dict(color='#1E88E5', width=3)
    ))
    
    # Add markers and shaded regions for COVID periods
    # Convert timestamps to strings for plotly
    try:
        covid_start_str = '2020-03-01'  # String format for plotly
        covid_end_str = '2021-07-31'    # String format for plotly
        
        # Add vertical lines indicating COVID period boundaries
        fig.add_shape(
            type="line", 
            x0=covid_start_str, 
            y0=0, 
            x1=covid_start_str, 
            y1=1, 
            line=dict(color="red", width=2, dash="dash"),
            xref="x", 
            yref="paper"
        )
        
        # Add annotation for COVID start
        fig.add_annotation(
            x=covid_start_str,
            y=1,
            text="COVID Start",
            showarrow=False,
            yshift=10
        )
        
        # Add vertical line for COVID end
        fig.add_shape(
            type="line", 
            x0=covid_end_str, 
            y0=0, 
            x1=covid_end_str, 
            y1=1, 
            line=dict(color="green", width=2, dash="dash"),
            xref="x", 
            yref="paper"
        )
        
        # Add annotation for COVID end
        fig.add_annotation(
            x=covid_end_str,
            y=1,
            text="COVID End",
            showarrow=False,
            yshift=10
        )
        
        # Get min and max dates as strings
        min_date_str = df_sorted['date'].min().strftime('%Y-%m-%d')
        max_date_str = df_sorted['date'].max().strftime('%Y-%m-%d')
        
        # Add shaded rectangle for Pre-COVID period
        fig.add_shape(
            type="rect",
            x0=min_date_str,
            x1=covid_start_str,
            y0=0,
            y1=1,
            fillcolor="lightgreen",
            opacity=0.2,
            layer="below",
            line_width=0,
            xref="x",
            yref="paper"
        )
        
        # Add annotation for Pre-COVID (using paper coordinates instead)
        fig.add_annotation(
            x=0.15,  # Positioned at 15% of the chart width
            y=0.95,
            text="Pre-COVID",
            showarrow=False,
            yshift=10,
            xref="paper",
            yref="paper"
        )
        
        # Add shaded rectangle for During-COVID period
        fig.add_shape(
            type="rect",
            x0=covid_start_str,
            x1=covid_end_str,
            y0=0,
            y1=1,
            fillcolor="lightcoral",
            opacity=0.2,
            layer="below",
            line_width=0,
            xref="x",
            yref="paper"
        )
        
        # Add annotation for During-COVID (using paper coordinates)
        fig.add_annotation(
            x=0.5,  # Positioned at 50% of the chart width
            y=0.95,
            text="During-COVID",
            showarrow=False,
            yshift=10,
            xref="paper",
            yref="paper"
        )
        
        # Add shaded rectangle for Post-COVID period
        fig.add_shape(
            type="rect",
            x0=covid_end_str,
            x1=max_date_str,
            y0=0,
            y1=1,
            fillcolor="lightgreen",
            opacity=0.2,
            layer="below",
            line_width=0,
            xref="x",
            yref="paper"
        )
        
        # Add annotation for Post-COVID (using paper coordinates)
        fig.add_annotation(
            x=0.85,  # Positioned at 85% of the chart width
            y=0.95,
            text="Post-COVID",
            showarrow=False,
            yshift=10,
            xref="paper",
            yref="paper"
        )
    except Exception as e:
        # If there's any error with the COVID period markers, log it but don't crash
        print(f"Error adding COVID period markers: {str(e)}")
        # Add a simple annotation explaining the issue
        fig.add_annotation(
            x=0.5,
            y=0.9,
            xref="paper",
            yref="paper",
            text="Note: COVID period markers could not be displayed",
            showarrow=False,
            font=dict(color="red")
        )
    
    # Update layout
    fig.update_layout(
        title=f"Evolution of {metric.replace('_', ' ').title()} Over Time",
        xaxis_title="Date",
        yaxis_title=f"{metric.replace('_', ' ').title()} Rate",
        hovermode="x unified",
        height=500
    )
    
    return fig
