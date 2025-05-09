# Football Home Field Advantage Analysis

![Premier League Logo](https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/Premier_League_Logo.svg/1200px-Premier_League_Logo.svg.png)

## Overview

This interactive Streamlit application analyzes "The Home Field Advantage Evolution in European Soccer" across three distinct periods: Pre-COVID, During COVID, and Post-COVID. The app visualizes how crowd support influences various match performance indicators during these periods.

Using data from top European leagues (Premier League, La Liga, Bundesliga, Serie A, and Ligue 1), the application provides comprehensive insights into how home advantage changed when matches were played in empty stadiums during the pandemic.

## Features

- **Real-time Data**: Fetches current football data from professional APIs (football-data.org and API-Football)
- **Period Analysis**: Compares match statistics across Pre-COVID, During-COVID, and Post-COVID periods
- **Interactive Visualizations**: Explore correlations between attendance and performance metrics
- **Team-specific Analysis**: Filter analysis by specific teams to examine their home advantage evolution
- **Database Integration**: Local SQLite database for efficient data retrieval and caching
- **Data Dictionary**: Comprehensive explanations of football metrics for users new to the sport

## Deployment

### Prerequisites

- Python 3.8+
- Required libraries listed in `requirements_for_streamlit.txt`

### Local Setup

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/football-home-advantage.git
   cd football-home-advantage
   ```

2. Install dependencies
   ```bash
   pip install -r requirements_for_streamlit.txt
   ```

3. Set up your API keys
   - Copy the `.env.example` file to `.env`
   - Add your API keys from [football-data.org](https://www.football-data.org/) and [API-Football](https://www.api-football.com/)

4. Run the Streamlit app
   ```bash
   streamlit run app.py
   ```

### Deploying to Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Sharing](https://streamlit.io/sharing)
3. Log in with GitHub and select your repository
4. Add the required secrets (API keys) in Streamlit's secrets management
5. Deploy!

## Data Sources

This application uses the following data sources:

- **[football-data.org API](https://www.football-data.org/)**: Primary source for match data
- **[API-Football](https://www.api-football.com/)**: Secondary source for additional statistics

## Project Structure

- `app.py`: Main Streamlit application
- `api.py`: API interaction functions
- `data_processing.py`: Data processing and analysis functions
- `visualization.py`: Functions for creating visualizations
- `sqlite_db.py`: SQLite database functions
- `data_dictionary.py`: Definitions and explanations for football terms
- `.env.example`: Template for API keys and configuration

## Example Visualizations

The application provides various visualizations including:

- Home win percentage evolution over time
- Home vs. away performance metrics
- Attendance impact on match outcomes
- Team-specific performance breakdowns
- Statistical correlations between match metrics

## Acknowledgements

- Developed for DATA 6560: Sports Analytics
- Project supervisor: Prof. Bianca Gadzé

## License

This project is licensed under the MIT License - see the LICENSE file for details.