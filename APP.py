import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
from io import StringIO

# הגדרות דף
st.set_page_config(
    page_title="Football Predictor Pro",
    page_icon="⚽",
    layout="centered"
)
st.title("⚽ Football Match Predictor Pro - עונת 2025/2026")

# קיבוץ הליגות - הגדרה מוקדמת
league_categories = {
    "🏆 ליגות אירופיות": ['Champions League', 'Europa League', 'Conference League'],
    "🇬🇧 אנגליה": ['Premier League', 'Championship'],
    "🇪🇸 ספרד": ['La Liga', 'Segunda División'],
    "🇮🇹 איטליה": ['Serie A'],
    "🇩🇪 גרמניה": ['Bundesliga'],
    "🇫🇷 צרפת": ['Ligue 1'],
    "🇮🇱 ישראל": ['ליגת העל הישראלית']
}

# ----------------------------
# קבוצות לפי ליגה (עונת 2025-2026)
# ----------------------------
LEAGUE_TEAMS = {
    'Bundesliga': [
        'Augsburg', 'Bayern Munich', 'Dortmund', 'Ein Frankfurt',
        'Freiburg', 'Hamburg', 'Heidenheim', 'Hoffenheim', 'Koln', 'Leverkusen',
        "M'gladbach", 'Mainz', 'RB Leipzig', 'St Pauli', 'Stuttgart',
        'Union Berlin', 'Werder Bremen', 'Wolfsburg'
    ],
    'Premier League': [
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
        'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham',
        'Leeds', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
        "Nott'm Forest", 'Sunderland', 'Tottenham', 'West Ham', 'Wolves'
    ],
    'Championship': [
        'Blackburn', 'Bristol City', 'Cardiff', 'Coventry', 'Derby', 
        'Hull', 'Ipswich', 'Leicester', 'Luton', 'Middlesbrough', 'Millwall', 
        'Norwich', 'Oxford United', 'Plymouth', 'Portsmouth', 'Preston', 
        'QPR', 'Sheffield United', 'Sheffield Weds', 'Southampton', 'Stoke', 
        'Swansea', 'Watford', 'West Brom'
    ],
    'La Liga': [
        'Alaves', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis',
        'Celta', 'Elche', 'Espanyol', 'Getafe', 'Girona', 'Levante',
        'Mallorca', 'Osasuna', 'Oviedo', 'Rayo Vallecano', 'Real Madrid', 'Sevilla', 
        'Sociedad', 'Valencia', 'Villarreal'
    ],
    'Segunda División': [
        'Albacete', 'Almeria', 'Burgos', 'Cartagena', 'Castellon',
        'Cordoba', 'Deportivo', 'Eibar', 'Granada', 'Huesca', 'Las Palmas',
        'Leganes', 'Malaga', 'Mirandes', 'Racing Ferrol', 'Racing Santander', 
        'Sporting Gijon', 'Tenerife', 'Valladolid', 'Zaragoza'
    ],
    'Ligue 1': [
        'Auxerre', 'Brest', 'Le Havre', 'Lens', 'Lille', 'Lorient', 'Lyon',
        'Marseille', 'Metz', 'Monaco', 'Montpellier', 'Nantes', 'Nice', 
        'Paris FC', 'Paris SG', 'Rennes', 'Strasbourg', 'Toulouse'
    ],
    'Serie A': [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Empoli', 'Fiorentina',
        'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza',
        'Napoli', 'Parma', 'Roma', 'Torino', 'Udinese', 'Venezia', 'Verona'
    ],
    'ליגת העל הישראלית': [
        'Maccabi Tel Aviv', 'Maccabi Haifa', 'Hapoel Beer Sheva', 'Beitar Jerusalem',
        'Hapoel Tel Aviv', 'Bnei Sakhnin', 'Hapoel Jerusalem', 'Hapoel Haifa',
        'Maccabi Netanya', 'Ashdod', 'Hapoel Petah Tikva', 'Maccabi Bnei Raina',
        'Ironi Kiryat Shmona', 'Ironi Tiberias'
    ],
    'Champions League': [
        'Real Madrid', 'Barcelona', 'Ath Madrid', 'Athletic Bilbao',
        'Bayern Munich', 'Dortmund', 'RB Leipzig', 'Leverkusen', 'Stuttgart',
        'Inter', 'Milan', 'Juventus', 'Atalanta', 'Bologna',
        'Man City', 'Arsenal', 'Liverpool', 'Chelsea', 'Aston Villa',
        'Paris SG', 'Monaco', 'Lille', 'Brest',
        'PSV', 'Feyenoord', 'Ajax', 'Benfica', 'Porto', 'Sporting',
        'Celtic', 'Rangers', 'Shakhtar', 'Young Boys', 'Red Star Belgrade',
        'Sparta Prague', 'Club Brugge', 'Salzburg', 'Galatasaray', 'Copenhagen'
    ],
    'Europa League': [
        'Man United', 'Tottenham', 'Brighton', 'West Ham',
        'Roma', 'Lazio', 'Fiorentina', 'Napoli',
        'Ein Frankfurt', 'Hoffenheim', 'Union Berlin',
        'Lyon', 'Nice', 'Marseille', 'Rennes',
        'Villarreal', 'Betis', 'Sociedad', 'Sevilla',
        'Ajax', 'AZ Alkmaar', 'Twente', 'Braga', 'Porto',
        'Fenerbahce', 'Galatasaray', 'Besiktas',
        'Olympiacos', 'PAOK', 'Rangers', 'Celtic'
    ],
    'Conference League': [
        'Chelsea', 'Fiorentina', 'Viktoria Plzen', 'Gent',
        'Heidenheim', 'Olympiacos', 'Rapid Wien', 'Molde',
        'Legia Warsaw', 'Dinamo Minsk', 'Hearts', 'Petrocub'
    ]
}

# נתוני ביצועים מורחבים של קבוצות אירופיות
EUROPEAN_TEAM_STATS = {
    # קבוצות חזקות מאוד
    'Real Madrid': {'home_goals': 2.9, 'away_goals': 2.3, 'home_conceded': 0.8, 'away_conceded': 1.0, 'strength': 96},
    'Barcelona': {'home_goals': 2.7, 'away_goals': 2.1, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 91},
    'Bayern Munich': {'home_goals': 3.0, 'away_goals': 2.4, 'home_conceded': 0.7, 'away_conceded': 0.9, 'strength': 94},
    'Man City': {'home_goals': 2.8, 'away_goals': 2.2, 'home_conceded': 0.8, 'away_conceded': 1.1, 'strength': 93},
    'Paris SG': {'home_goals': 2.6, 'away_goals': 2.0, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 89},
    
    # קבוצות חזקות
    'Liverpool': {'home_goals': 2.5, 'away_goals': 1.9, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 88},
    'Inter': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 0.9, 'away_conceded': 1.1, 'strength': 86},
    'Arsenal': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 85},
    'Dortmund': {'home_goals': 2.5, 'away_goals': 1.9, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 84},
    'Chelsea': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 83},
    'Ath Madrid': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 0.7, 'away_conceded': 1.0, 'strength': 82},
    'Milan': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.1, 'away_conceded': 1.3, 'strength': 81},
    'Napoli': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 80},
    'Juventus': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.0, 'away_conceded': 1.2, 'strength': 79},
    'RB Leipzig': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.2, 'away_conceded': 1.4, 'strength': 79},
    'Leverkusen': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.1, 'away_conceded': 1.3, 'strength': 78},
    
    # קבוצות טובות
    'Atalanta': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 78},
    'Man United': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 77},
    'Tottenham': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 76},
    'Roma': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 75},
    'Lazio': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.3, 'away_conceded': 1.5, 'strength': 74},
    'Villarreal': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 74},
    'Sevilla': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 73},
    'Athletic Bilbao': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 73},
    'Sociedad': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 72},
    'Betis': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 71},
    'Monaco': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 72},
    'Lyon': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 70},
    'Marseille': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 70},
    'Fiorentina': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 71},
    'Bologna': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 69},
    'Aston Villa': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 72},
    'Brighton': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 70},
    'West Ham': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 69},
    
    # קבוצות בינוניות
    'Ein Frankfurt': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 69},
    'Stuttgart': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 68},
    'Hoffenheim': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 67},
    'Union Berlin': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 67},
    'Lille': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 68},
    'Nice': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 67},
    'Rennes': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 66},
    'Brest': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 65},
    
    # קבוצות הולנדיות ופורטוגזיות
    'Ajax': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 71},
    'PSV': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 70},
    'Feyenoord': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 68},
    'AZ Alkmaar': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 65},
    'Twente': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 64},
    'Benfica': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 72},
    'Porto': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 71},
    'Sporting': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 70},
    'Braga': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 66},
    
    # קבוצות טורקיות ויווניות
    'Galatasaray': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 67},
    'Fenerbahce': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 66},
    'Besiktas': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 64},
    'Olympiacos': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 65},
    'PAOK': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 63},
    
    # קבוצות סקוטיות ואחרות
    'Celtic': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 66},
    'Rangers': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 65},
    'Shakhtar': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 64},
    'Salzburg': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 66},
    'Copenhagen': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 63},
    'Club Brugge': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 63},
    'Young Boys': {'home_goals': 1.4, 'away_goals': 0.8, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 61},
    'Red Star Belgrade': {'home_goals': 1.4, 'away_goals': 0.8, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 60},
    'Sparta Prague': {'home_goals': 1.3, 'away_goals': 0.7, 'home_conceded': 1.6, 'away_conceded': 1.9, 'strength': 59},
    
    # Conference League teams
    'Viktoria Plzen': {'home_goals': 1.4, 'away_goals': 0.8, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 60},
    'Gent': {'home_goals': 1.4, 'away_goals': 0.8, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 60},
    'Heidenheim': {'home_goals': 1.3, 'away_goals': 0.7, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 59},
    'Rapid Wien': {'home_goals': 1.3, 'away_goals': 0.7, 'home_conceded': 1.6, 'away_conceded': 1.9, 'strength': 58},
    'Molde': {'home_goals': 1.3, 'away_goals': 0.7, 'home_conceded': 1.6, 'away_conceded': 1.9, 'strength': 58},
    'Legia Warsaw': {'home_goals': 1.3, 'away_goals': 0.7, 'home_conceded': 1.6, 'away_conceded': 1.9, 'strength': 57},
    'Dinamo Minsk': {'home_goals': 1.2, 'away_goals': 0.6, 'home_conceded': 1.7, 'away_conceded': 2.0, 'strength': 55},
    'Hearts': {'home_goals': 1.2, 'away_goals': 0.6, 'home_conceded': 1.7, 'away_conceded': 2.0, 'strength': 56},
    'Petrocub': {'home_goals': 1.1, 'away_goals': 0.5, 'home_conceded': 1.8, 'away_conceded': 2.1, 'strength': 53}
}

# נתוני ביצועים של קבוצות ישראליות
ISRAELI_TEAM_STATS = {
    'Maccabi Tel Aviv': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 75},
    'Maccabi Haifa': {'home_goals': 1.9, 'away_goals': 1.4, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 72},
    'Hapoel Beer Sheva': {'home_goals': 1.8, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 70},
    'Beitar Jerusalem': {'home_goals': 1.7, 'away_goals': 1.2, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 67},
    'Hapoel Tel Aviv': {'home_goals': 1.6, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 65},
    'Bnei Sakhnin': {'home_goals': 1.5, 'away_goals': 1.0, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 63},
    'Hapoel Jerusalem': {'home_goals': 1.5, 'away_goals': 1.0, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 62},
    'Hapoel Haifa': {'home_goals': 1.5, 'away_goals': 1.0, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 62},
    'Maccabi Netanya': {'home_goals': 1.4, 'away_goals': 0.9, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 60},
    'Ashdod': {'home_goals': 1.3, 'away_goals': 0.8, 'home_conceded': 1.6, 'away_conceded': 1.9, 'strength': 58},
    'Hapoel Petah Tikva': {'home_goals': 1.3, 'away_goals': 0.8, 'home_conceded': 1.6, 'away_conceded': 1.9, 'strength': 58},
    'Maccabi Bnei Raina': {'home_goals': 1.2, 'away_goals': 0.7, 'home_conceded': 1.7, 'away_conceded': 2.0, 'strength': 56},
    'Ironi Kiryat Shmona': {'home_goals': 1.2, 'away_goals': 0.7, 'home_conceded': 1.7, 'away_conceded': 2.0, 'strength': 55},
    'Ironi Tiberias': {'home_goals': 1.1, 'away_goals': 0.6, 'home_conceded': 1.8, 'away_conceded': 2.1, 'strength': 53}
}

def get_team_stats(team, league_type):
    """קבלת סטטיסטיקות קבוצה"""
    # בדיקה אם הקבוצה קיימת במאגר הנתונים
    if team in EUROPEAN_TEAM_STATS:
        return EUROPEAN_TEAM_STATS[team]
    
    if team in ISRAELI_TEAM_STATS:
        return ISRAELI_TEAM_STATS[team]
    
    # ערכי ברירת מחדל לפי סוג הליגה
    if league_type == 'Champions League':
        return {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 76}
    elif league_type == 'Europa League':
        return {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 71}
    elif league_type == 'Conference League':
        return {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 65}
    elif league_type == 'ליגת העל הישראלית':
        return {'home_goals': 1.4, 'away_goals': 1.0, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 62}
    else:
        return {'home_goals': 1.5, 'away_goals': 1.2, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 70}

# ----------------------------
# טעינת נתונים
# ----------------------------
def standardize_column_names(df):
    """סטנדרטיזציה של שמות עמודות"""
    column_mappings = {
        'team1': 'HomeTeam', 'Team 1': 'HomeTeam', 'Home': 'HomeTeam', 'HT': 'HomeTeam',
        'team2': 'AwayTeam', 'Team 2': 'AwayTeam', 'Away': 'AwayTeam', 'AT': 'AwayTeam',
        'score1': 'FTHG', 'Score 1': 'FTHG', 'HomeGoals': 'FTHG', 'HG': 'FTHG',
        'score2': 'FTAG', 'Score 2': 'FTAG', 'AwayGoals': 'FTAG', 'AG': 'FTAG',
        'HomeCorners': 'HC', 'AwayCorners': 'AC'
    }
    
    for old_col, new_col in column_mappings.items():
        if old_col in df.columns and new_col not in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    return df

@st.cache_data(ttl=3600)
def load_league_data():
    """טעינת נתונים מהאינטרנט"""
    data_sources = {
        "Premier League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/epl.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/PL2324.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/PL2223.csv",
            "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
            "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
        ],
        "Championship": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/E1%202526.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/E1%202425.csv",
            "https://www.football-data.co.uk/mmz4281/2526/E1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/E1.csv"
        ],
        "La Liga": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/laliga.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/LALIGA2324.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/LALIGA2223.csv",
            "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/SP1.csv"
        ],
        "Segunda División": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/SP2%202425.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/SP2%202324.csv",
            "https://www.football-data.co.uk/mmz4281/2526/SP2.csv",
            "https://www.football-data.co.uk/mmz4281/2425/SP2.csv"
        ],
        "Serie A": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/seriea.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/SERIE%20A2324.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/SERIE%20A%202223.csv",
            "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/I1.csv"
        ],
        "Bundesliga": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/bundesliga.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/BUNDESLIGA2324.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/BUNDESLIGA2223.csv",
            "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/D1.csv"
        ],
        "Ligue 1": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/ligue1.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/LIGUE%201%202324.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/LIGUE1%202223.csv",
            "https://www.football-data.co.uk/mmz4281/2526/F1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/F1.csv"
        ],
        "ליגת העל הישראלית": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/israeli_premier_league_csv.csv.txt"
        ],
        "Champions League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/CL.csv"
        ],
        "Europa League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/EL.csv"
        ],
        "Conference League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/ECL.csv"
        ]
    }
    
    league_data = {}
    for league, urls in data_sources.items():
        for i, url in enumerate(urls):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                df = pd.read_csv(StringIO(response.text))
                df = standardize_column_names(df)
                
                # המרת עמודות מספריות
                for col in ['FTHG', 'FTAG', 'HC', 'AC']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                if not df.empty and len(df) > 5:
                    league_data[league] = df
                    break
            except requests.exceptions.RequestException:
                continue
            except Exception:
                continue
    
    return league_data

# ----------------------------
# פונקציות חיזוי
# ----------------------------
def predict_match_with_data(home_team, away_team, df, league_name):
    """חיזוי משחק על בסיס נתונים"""
    try:
        # חיפוש משחקי בית של הקבוצה הביתית
        home_matches = df[df['HomeTeam'].str.contains(home_team, case=False, na=False)]
        # חיפוש משחקי חוץ של הקבוצה האורחת
        away_matches = df[df['AwayTeam'].str.contains(away_team, case=False, na=False)]
        
        # הצגת מידע דיבאג בסרגל הצד
        with st.sidebar:
            st.markdown("### 📊 נתוני CSV")
            st.markdown(f"**{league_name}**")
            st.markdown(f"- סה״כ משחקים: {len(df)}")
            st.markdown(f"- משחקי בית של {home_team}: {len(home_matches)}")
            st.markdown(f"- משחקי חוץ של {away_team}: {len(away_matches)}")
        
        # חישוב ממוצעי שערים
        if len(home_matches) > 0:
            home_goals_avg = home_matches['FTHG'].mean()
            home_conceded_avg = home_matches['FTAG'].mean()
        else:
            home_goals_avg = df['FTHG'].mean() if 'FTHG' in df.columns else 1.5
            home_conceded_avg = df['FTAG'].mean() if 'FTAG' in df.columns else 1.2
            
        if len(away_matches) > 0:
            away_goals_avg = away_matches['FTAG'].mean()
            away_conceded_avg = away_matches['FTHG'].mean()
        else:
            away_goals_avg = df['FTAG'].mean() if 'FTAG' in df.columns else 1.2
            away_conceded_avg = df['FTHG'].mean() if 'FTHG' in df.columns else 1.5
        
        # חישוב ממוצעי הליגה
        league_home_avg = df['FTHG'].mean() if 'FTHG' in df.columns else 1.5
        league_away_avg = df['FTAG'].mean() if 'FTAG' in df.columns else 1.2
        
        # חישוב כוח התקפי והגנתי
        home_attack_strength = home_goals_avg / league_home_avg if league_home_avg > 0 else 1
        home_defense_strength = home_conceded_avg / league_away_avg if league_away_avg > 0 else 1
        away_attack_strength = away_goals_avg / league_away_avg if league_away_avg > 0 else 1
        away_defense_strength = away_conceded_avg / league_home_avg if league_home_avg > 0 else 1
        
        # חישוב שערים צפויים
        home_expected = home_attack_strength * away_defense_strength * league_home_avg
        away_expected = away_attack_strength * home_defense_strength * league_away_avg
        
        # וידוא שהערכים תקינים
        if pd.isna(home_expected) or home_expected <= 0:
            home_expected = 1.5
        if pd.isna(away_expected) or away_expected <= 0:
            away_expected = 1.2
        
        # הצגת ממוצעים בסרגל הצד
        with st.sidebar:
            st.markdown("### ⚽ ממוצעי שערים")
            st.markdown(f"**{home_team}:**")
            st.markdown(f"- זכה בבית: {home_goals_avg:.2f}")
            st.markdown(f"- ספג בבית: {home_conceded_avg:.2f}")
            st.markdown(f"**{away_team}:**")
            st.markdown(f"- זכה בחוץ: {away_goals_avg:.2f}")
            st.markdown(f"- ספג בחוץ: {away_conceded_avg:.2f}")
        
        # חישוב הסתברויות באמצעות פואסון
        max_goals = 5
        home_win = draw = away_win = 0.0
        
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = poisson.pmf(i, home_expected) * poisson.pmf(j, away_expected)
                if i > j:
                    home_win += prob
                elif i == j:
                    draw += prob
                else:
                    away_win += prob
        
        return {
            'home_win': round(home_win, 3),
            'draw': round(draw, 3),
            'away_win': round(away_win, 3),
            'total_goals': round(home_expected + away_expected, 1),
            'home_expected': round(home_expected, 2),
            'away_expected': round(away_expected, 2),
            'data_source': 'CSV'
        }
    except Exception as e:
        st.sidebar.error(f"שגיאה בעיבוד נתונים: {str(e)}")
        # ערכי ברירת מחדל במקרה של שגיאה
        return {
            'home_win': 0.45,
            'draw': 0.30,
            'away_win': 0.25,
            'total_goals': 2.5,
            'data_source': 'Default'
        }

def predict_match_european_and_israeli(home_team, away_team, league_type):
    """חיזוי משחק אירופי או ישראלי"""
    home_stats = get_team_stats(home_team, league_type)
    away_stats = get_team_stats(away_team, league_type)
    
    # הצגת הסטטיסטיקות שנמצאו
    with st.sidebar:
        st.markdown("### 📊 נתוני קבוצות")
        st.markdown(f"**{home_team}:**")
        st.markdown(f"- כוח: {home_stats['strength']}")
        st.markdown(f"- שערים בבית: {home_stats['home_goals']}")
        st.markdown(f"**{away_team}:**")
        st.markdown(f"- כוח: {away_stats['strength']}")
        st.markdown(f"- שערים בחוץ: {away_stats['away_goals']}")
        
        # בדיקה אם משתמשים בערכי ברירת מחדל
        if home_team not in EUROPEAN_TEAM_STATS and home_team not in ISRAELI_TEAM_STATS:
            st.markdown(f"⚠️ {home_team} - ערכי ברירת מחדל")
        if away_team not in EUROPEAN_TEAM_STATS and away_team not in ISRAELI_TEAM_STATS:
            st.markdown(f"⚠️ {away_team} - ערכי ברירת מחדל")
    
    # חישוב יחס כוחות
    strength_ratio = home_stats['strength'] / away_stats['strength']
    
    # חישוב שערים צפויים
    home_goals = home_stats['home_goals'] * (1 + (strength_ratio - 1) * 0.2)
    away_goals = away_stats['away_goals'] * (1 + (1/strength_ratio - 1) * 0.15)
    
    # חישוב הסתברויות
    max_goals = 5
    home_win = draw = away_win = 0.0
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            prob = poisson.pmf(i, home_goals) * poisson.pmf(j, away_goals)
            if i > j:
                home_win += prob
            elif i == j:
                draw += prob
            else:
                away_win += prob
    
    return {
        'home_win': round(home_win, 3),
        'draw': round(draw, 3),
        'away_win': round(away_win, 3),
        'total_goals': round(home_goals + away_goals, 1),
        'home_expected': round(home_goals, 2),
        'away_expected': round(away_goals, 2),
        'data_source': 'Stats DB'
    }

# ----------------------------
# ממשק משתמש
# ----------------------------

# טעינת נתונים
with st.spinner('טוען נתונים...'):
    data = load_league_data()

# הצגת סטטוס טעינת נתונים בסרגל הצד
with st.sidebar:
    st.markdown("### 📁 סטטוס נתונים")
    for league in ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']:
        if league in data:
            st.success(f"✅ {league}")
        else:
            st.error(f"❌ {league}")

# בחירת קטגוריה וליגה
selected_category = st.selectbox("בחר קטגוריה", options=list(league_categories.keys()))
available_leagues = league_categories[selected_category]
selected_league = st.selectbox("בחר ליגה", options=available_leagues)

# בדיקה שהליגה קיימת
if selected_league not in LEAGUE_TEAMS:
    st.error("הליגה הנבחרת לא זמינה")
    st.stop()

# בחירת קבוצות
teams = LEAGUE_TEAMS[selected_league]
col1, col2 = st.columns(2)

with col1:
    home_team = st.selectbox("קבוצה ביתית", options=teams)

with col2:
    away_team = st.selectbox("קבוצה אורחת", options=[t for t in teams if t != home_team])

# כפתור חיזוי
if st.button("🔮 חשב חיזוי", type="primary", use_container_width=True):
    with st.spinner('מחשב...'):
        # חיזוי לפי סוג הליגה
        if selected_league in ['Champions League', 'Europa League', 'Conference League', 'ליגת העל הישראלית']:
            prediction = predict_match_european_and_israeli(home_team, away_team, selected_league)
        elif selected_league in data:
            prediction = predict_match_with_data(home_team, away_team, data[selected_league], selected_league)
        else:
            # אם אין נתונים, נשתמש בערכי ברירת מחדל
            st.warning("אין נתונים זמינים לליגה זו, משתמש בערכים כלליים")
            prediction = {
                'home_win': 0.45,
                'draw': 0.30,
                'away_win': 0.25,
                'total_goals': 2.5,
                'data_source': 'Default'
            }
        
        # הצגת מקור הנתונים
        if 'data_source' in prediction:
            st.info(f"📊 מקור נתונים: {prediction['data_source']}")
        
        # הצגת תוצאות
        st.markdown("---")
        st.subheader("📊 תוצאות החיזוי")
        
        # הצגת הסתברויות
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=f"🏠 {home_team}",
                value=f"{prediction['home_win']*100:.1f}%",
                delta="ניצחון" if prediction['home_win'] > 0.4 else None
            )
        
        with col2:
            st.metric(
                label="🤝 תיקו",
                value=f"{prediction['draw']*100:.1f}%"
            )
        
        with col3:
            st.metric(
                label=f"✈️ {away_team}",
                value=f"{prediction['away_win']*100:.1f}%",
                delta="ניצחון" if prediction['away_win'] > 0.4 else None
            )
        
        # הצגת שערים צפויים (אם זמין)
        if 'home_expected' in prediction and 'away_expected' in prediction:
            st.markdown("---")
            st.subheader("⚽ תוצאה צפויה")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{home_team}", f"{prediction['home_expected']:.1f}")
            with col2:
                st.markdown("### -")
            with col3:
                st.metric(f"{away_team}", f"{prediction['away_expected']:.1f}")
        
        # המלצה
        st.markdown("---")
        st.subheader("💡 המלצה")
        
        max_prob = max(prediction['home_win'], prediction['draw'], prediction['away_win'])
        
        if max_prob == prediction['home_win']:
            st.success(f"**המלצה: ניצחון ל-{home_team}** (סיכוי של {prediction['home_win']*100:.1f}%)")
        elif max_prob == prediction['draw']:
            st.info(f"**המלצה: תיקו** (סיכוי של {prediction['draw']*100:.1f}%)")
        else:
            st.warning(f"**המלצה: ניצחון ל-{away_team}** (סיכוי של {prediction['away_win']*100:.1f}%)")
        
        # סך שערים
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("⚽ סך שערים צפוי", f"{prediction['total_goals']}")
        
        with col2:
            if prediction['total_goals'] > 2.5:
                st.success("מומלץ: מעל 2.5 שערים")
            else:
                st.info("מומלץ: מתחת ל-2.5 שערים")

# Footer
st.markdown("---")
st.markdown("*⚽ Football Predictor Pro | נבנה עם ❤️ לחובבי כדורגל*")