import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
from io import StringIO
import re

# הגדרות דף
st.set_page_config(
    page_title="Football Predictor Pro",
    page_icon="⚽",
    layout="centered"
)
st.title("⚽ Football Match Predictor Pro - עונת 2025/2026")

# ----------------------------
# קבוצות לפי ליגה (עונת 2025-2026)
# ----------------------------
LEAGUE_TEAMS = {
    'Bundesliga': [
        'Augsburg', 'Bayern Munich', 'Bochum', 'Dortmund', 'Ein Frankfurt',
        'Freiburg', 'Heidenheim', 'Hoffenheim', 'Holstein Kiel', 'Leverkusen',
        "M'gladbach", 'Mainz', 'RB Leipzig', 'St Pauli', 'Stuttgart',
        'Union Berlin', 'Werder Bremen', 'Wolfsburg'
    ],
    'Premier League': [
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
        'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham',
        'Leeds United', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
        "Nott'm Forest", 'Sunderland', 'Tottenham', 'West Ham', 'Wolves'
    ],
    'Championship': [
        'Birmingham', 'Blackburn', 'Bristol City', 'Charlton', 'Coventry',
        'Derby', 'Hull', 'Ipswich', 'Leicester', 'Middlesbrough', 'Millwall', 
        'Norwich', 'Oxford', 'Portsmouth', 'Preston', 'QPR', 
        'Sheffield United', 'Sheffield Weds', 'Southampton', 'Stoke', 
        'Swansea', 'Watford', 'West Brom', 'Wrexham'
    ],
    'La Liga': [
        'Alaves', 'Almeria', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis',
        'Cadiz', 'Celta', 'Getafe', 'Girona', 'Las Palmas', 'Leganes',
        'Mallorca', 'Osasuna', 'Real Madrid', 'Sevilla', 'Sociedad',
        'Valencia', 'Valladolid', 'Villarreal'
    ],
    'Segunda División': [
        'Albacete', 'Almeria', 'Andorra', 'Burgos', 'Cadiz', 'Castellon',
        'Ceuta', 'Cordoba', 'Cultural Leonesa', 'Deportivo La Coruna', 
        'Eibar', 'Granada', 'Huesca', 'Las Palmas', 'Leganes', 'Malaga', 
        'Mirandes', 'Oviedo', 'Racing Santander', 'Real Sociedad B', 
        'Valladolid', 'Zaragoza'
    ],
    'Ligue 1': [
        'Angers', 'Auxerre', 'Brest', 'Le Havre', 'Lens', 'Lille', 'Lyon',
        'Marseille', 'Monaco', 'Montpellier', 'Nantes', 'Nice', 'Paris SG',
        'Reims', 'Rennes', 'St Etienne', 'Strasbourg', 'Toulouse'
    ],
    'Serie A': [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Empoli', 'Fiorentina',
        'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza',
        'Napoli', 'Parma', 'Roma', 'Torino', 'Udinese', 'Venezia', 'Verona'
    ],
    'Israeli Premier League': [
        'Maccabi Tel Aviv', 'Hapoel Beer Sheva', 'Maccabi Haifa', 'Hapoel Tel Aviv',
        'Maccabi Netanya', 'Hapoel Haifa', 'Ashdod', 'Bnei Sakhnin',
        'Hapoel Jerusalem', 'Ironi Kiryat Shmona', 'Maccabi Bnei Raina',
        'Hapoel Katamon Jerusalem', 'Hapoel Petah Tikva', 'Sektzia Nes Tziona'
    ],
    'Champions League': [
        'Real Madrid', 'Barcelona', 'Ath Madrid', 'Athletic Bilbao',
        'Bayern Munich', 'Dortmund', 'RB Leipzig', 'Leverkusen', 'Stuttgart',
        'Inter', 'Milan', 'Juventus', 'Atalanta', 'Bologna', 'AC Fiorentina',
        'Man City', 'Arsenal', 'Liverpool', 'Chelsea', 'Aston Villa', 'Newcastle',
        'Paris SG', 'Monaco', 'Lille', 'Brest', 'Lyon',
        'Celtic', 'Rangers', 'PSV', 'Feyenoord', 'Ajax',
        'Benfica', 'Porto', 'Sporting', 'Braga',
        'Shakhtar', 'Dynamo Kyiv',
        'Young Boys', 'Red Star Belgrade', 'Sparta Prague', 'Slavia Prague',
        'Club Brugge', 'Anderlecht', 'Salzburg', 'Sturm Graz',
        'Galatasaray', 'Fenerbahce', 'Besiktas',
        'Bodo/Glimt', 'Molde', 'Copenhagen'
    ],
    'Europa League': [
        'Man United', 'Tottenham', 'West Ham', 'Brighton', 'Fulham',
        'Roma', 'Lazio', 'Fiorentina', 'Napoli', 'Torino',
        'Ein Frankfurt', 'Hoffenheim', 'Union Berlin', 'Mainz',
        'Lyon', 'Nice', 'Marseille', 'Rennes', 'Strasbourg', 'Lens',
        'Villarreal', 'Betis', 'Sociedad', 'Sevilla', 'Valencia', 'Celta',
        'Ajax', 'AZ Alkmaar', 'Twente', 'Utrecht', 'Vitesse',
        'Braga', 'Vitoria Guimaraes', 'Rio Ave',
        'Fenerbahce', 'Galatasaray', 'Besiktas', 'Trabzonspor',
        'Olympiacos', 'PAOK', 'AEK Athens', 'Panathinaikos'
    ],
    'Conference League': [
        'Chelsea', 'Brighton', 'Fulham', 'Crystal Palace', 'Brentford',
        'Fiorentina', 'Atalanta', 'Roma', 'Lazio', 'Genoa', 'Empoli',
        'Nice', 'Marseille', 'Rennes', 'Lyon', 'Toulouse', 'Montpellier',
        'Villarreal', 'Betis', 'Valencia', 'Getafe', 'Osasuna',
        'Ein Frankfurt', 'Union Berlin', 'Hoffenheim', 'Freiburg', 'Augsburg',
        'Ajax', 'AZ Alkmaar', 'Twente', 'Utrecht', 'Vitesse', 'Go Ahead Eagles',
        'Celtic', 'Rangers', 'Hearts', 'Aberdeen', 'Hibernian'
    ]
}

# נתוני ביצועים של קבוצות אירופיות
EUROPEAN_TEAM_STATS = {
    'Real Madrid': {'home_goals': 2.9, 'away_goals': 2.3, 'home_conceded': 0.8, 'away_conceded': 1.0, 'strength': 96},
    'Barcelona': {'home_goals': 2.7, 'away_goals': 2.1, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 91},
    'Bayern Munich': {'home_goals': 3.0, 'away_goals': 2.4, 'home_conceded': 0.7, 'away_conceded': 0.9, 'strength': 94},
    'Man City': {'home_goals': 2.8, 'away_goals': 2.2, 'home_conceded': 0.8, 'away_conceded': 1.1, 'strength': 93},
    'Paris SG': {'home_goals': 2.6, 'away_goals': 2.0, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 89},
    'Liverpool': {'home_goals': 2.5, 'away_goals': 1.9, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 88},
    'Inter': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 0.9, 'away_conceded': 1.1, 'strength': 86},
    'Arsenal': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 85},
    'Dortmund': {'home_goals': 2.5, 'away_goals': 1.9, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 84},
    'Chelsea': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 83},
    'Ath Madrid': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 0.7, 'away_conceded': 1.0, 'strength': 82},
    'Milan': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.1, 'away_conceded': 1.3, 'strength': 81},
    'Napoli': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 80},
    'Juventus': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.0, 'away_conceded': 1.2, 'strength': 79},
    'Atalanta': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 78}
}

def get_team_stats(team, league_type):
    if team in EUROPEAN_TEAM_STATS:
        return EUROPEAN_TEAM_STATS[team]
    
    if league_type == 'Champions League':
        return {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 76}
    elif league_type == 'Europa League':
        return {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 71}
    else:  # Conference League
        return {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 66}

# ----------------------------
# פונקציות עזר לניקוי ומיפוי שמות
# ----------------------------
def standardize_column_names(df):
    """סטנדרטיזציה של שמות עמודות"""
    column_mappings = {
        # שמות קבוצות
        'team1': 'HomeTeam',
        'Team 1': 'HomeTeam',
        'Home': 'HomeTeam',
        'HT': 'HomeTeam',
        'team2': 'AwayTeam',
        'Team 2': 'AwayTeam',
        'Away': 'AwayTeam',
        'AT': 'AwayTeam',
        
        # תוצאות
        'score1': 'FTHG',
        'Score 1': 'FTHG',
        'HomeGoals': 'FTHG',
        'HG': 'FTHG',
        'score2': 'FTAG',
        'Score 2': 'FTAG',
        'AwayGoals': 'FTAG',
        'AG': 'FTAG',
        
        # קרנות
        'HomeCorners': 'HC',
        'AwayCorners': 'AC'
    }
    
    for old_col, new_col in column_mappings.items():
        if old_col in df.columns and new_col not in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    return df

def clean_team_name(name):
    """ניקוי שם קבוצה"""
    if pd.isna(name):
        return ""
    # הסרת רווחים מיותרים
    name = str(name).strip()
    # החלפת תווים מיוחדים
    name = name.replace("'", "'")
    return name

def find_team_in_data(team_name, df, column):
    """מציאת קבוצה בנתונים עם גמישות בהתאמה"""
    if column not in df.columns:
        return pd.DataFrame()
    
    # ניסיון 1: התאמה מדויקת
    matches = df[df[column] == team_name]
    if not matches.empty:
        return matches
    
    # ניסיון 2: התאמה חלקית
    matches = df[df[column].str.contains(team_name, case=False, na=False, regex=False)]
    if not matches.empty:
        return matches
    
    # ניסיון 3: התאמה של חלק מהשם
    team_parts = team_name.split()
    for part in team_parts:
        if len(part) > 3:  # רק מילים משמעותיות
            matches = df[df[column].str.contains(part, case=False, na=False, regex=False)]
            if not matches.empty:
                return matches
    
    return pd.DataFrame()

# ----------------------------
# מקורות נתונים
# ----------------------------
def load_data_from_multiple_sources(github_urls):
    """טעינת נתונים ממקורות מרובים עם fallback"""
    for i, url in enumerate(github_urls):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            
            # סטנדרטיזציה של שמות עמודות
            df = standardize_column_names(df)
            
            # ניקוי שמות קבוצות
            if 'HomeTeam' in df.columns:
                df['HomeTeam'] = df['HomeTeam'].apply(clean_team_name)
            if 'AwayTeam' in df.columns:
                df['AwayTeam'] = df['AwayTeam'].apply(clean_team_name)
            
            # המרת עמודות מספריות
            numeric_columns = ['FTHG', 'FTAG', 'HC', 'AC']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            if not df.empty and len(df) > 10:  # וידוא שיש נתונים מספיקים
                source_name = url.split('/')[3] if '/' in url else 'unknown'
                st.info(f"📊 נתונים נטענו מ: {source_name} (מקור {i+1})")
                return df
        except Exception as e:
            source_name = url.split('/')[3] if '/' in url else 'unknown'
            st.warning(f"⚠️ לא ניתן לטעון מ-{source_name}: {str(e)[:50]}...")
            continue
    return None

@st.cache_data(ttl=3600)
def load_league_data():
    data_sources = {
        "Premier League": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/epl.csv",
            "https://raw.githubusercontent.com/footballcsv/england/master/2024-25/eng.1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
            "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
        ],
        "Championship": [
            "https://www.football-data.co.uk/mmz4281/2425/E1.csv",
            "https://www.football-data.co.uk/mmz4281/2324/E1.csv",
            "https://raw.githubusercontent.com/footballcsv/england/master/2023-24/eng.2.csv"
        ],
        "La Liga": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/laliga.csv",
            "https://www.football-data.co.uk/mmz4281/2425/SP1.csv",
            "https://www.football-data.co.uk/mmz4281/2324/SP1.csv"
        ],
        "Segunda División": [
            "https://www.football-data.co.uk/mmz4281/2425/SP2.csv",
            "https://www.football-data.co.uk/mmz4281/2324/SP2.csv",
            "https://raw.githubusercontent.com/footballcsv/espana/master/2023-24/esp.2.csv"
        ],
        "Serie A": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/seriea.csv",
            "https://www.football-data.co.uk/mmz4281/2425/I1.csv",
            "https://www.football-data.co.uk/mmz4281/2324/I1.csv"
        ],
        "Bundesliga": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/bundesliga.csv",
            "https://www.football-data.co.uk/mmz4281/2425/D1.csv",
            "https://www.football-data.co.uk/mmz4281/2324/D1.csv"
        ],
        "Ligue 1": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/ligue1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/F1.csv",
            "https://www.football-data.co.uk/mmz4281/2324/F1.csv"
        ],
        "Israeli Premier League": [
            "https://www.football-data.co.uk/new/ISR.csv"
        ]
    }
    
    league_data = {}
    successful_leagues = []
    failed_leagues = []
    
    for league, urls in data_sources.items():
        df = load_data_from_multiple_sources(urls)
        if df is not None:
            league_data[league] = df
            successful_leagues.append(league)
        else:
            failed_leagues.append(league)
    
    # הצגת סיכום טעינה
    if successful_leagues:
        st.success(f"✅ נטענו בהצלחה: {', '.join(successful_leagues)}")
    if failed_leagues:
        st.warning(f"⚠️ לא זמינים: {', '.join(failed_leagues)}")
    
    return league_data

# ----------------------------
# פונקציות חיזוי משופרות
# ----------------------------
def predict_match_regular(home_team, away_team, df):
    """חיזוי משחק רגיל עם טיפול משופר בשגיאות"""
    try:
        # בדיקה שהעמודות הנדרשות קיימות
        required_columns = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.warning(f"חסרות עמודות: {missing_columns}")
            # ערכי ברירת מחדל
            home_goals = 1.5
            away_goals = 1.2
        else:
            # מציאת משחקים של הקבוצות
            home_matches = find_team_in_data(home_team, df, 'HomeTeam')
            away_matches = find_team_in_data(away_team, df, 'AwayTeam')
            
            # חישוב ממוצעים
            if home_matches.empty and away_matches.empty:
                st.info("משתמש בממוצעי הליגה")
                home_goals = df['FTHG'].mean() if not df['FTHG'].isna().all() else 1.5
                away_goals = df['FTAG'].mean() if not df['FTAG'].isna().all() else 1.2
            else:
                if not home_matches.empty:
                    home_goals = home_matches['FTHG'].mean()
                else:
                    home_goals = df['FTHG'].mean() if not df['FTHG'].isna().all() else 1.5
                
                if not away_matches.empty:
                    away_goals = away_matches['FTAG'].mean()
                else:
                    away_goals = df['FTAG'].mean() if not df['FTAG'].isna().all() else 1.2
            
            # וידוא שהערכים תקינים
            if pd.isna(home_goals) or home_goals <= 0:
                home_goals = 1.5
            if pd.isna(away_goals) or away_goals <= 0:
                away_goals = 1.2
        
        # חישוב הסתברויות
        max_goals = 5
        home_win = draw = away_win = 0.0
        
        for i in range(max_goals+1):
            for j in range(max_goals+1):
                p = poisson.pmf(i, home_goals) * poisson.pmf(j, away_goals)
                if i > j: 
                    home_win += p
                elif i == j: 
                    draw += p
                else: 
                    away_win += p
        
        return {
            "home_win": round(home_win, 3),
            "draw": round(draw, 3),
            "away_win": round(away_win, 3),
            "total_goals": round(home_goals + away_goals, 1),
            "total_corners": get_corners_prediction(home_team, away_team, df)
        }
        
    except Exception as e:
        st.error(f"שגיאה בחישוב החיזוי: {str(e)}")
        # החזרת ערכי ברירת מחדל
        return {
            "home_win": 0.4,
            "draw": 0.3,
            "away_win": 0.3,
            "total_goals": 2.5,
            "total_corners": None
        }

def predict_match_european(home_team, away_team, league_type):
    home_stats = get_team_stats(home_team, league_type)
    away_stats = get_team_stats(away_team, league_type)
    
    strength_factor = home_stats['strength'] / away_stats['strength']
    home_advantage = 0.25 if league_type == 'Champions League' else 0.3
    
    home_goals_expected = home_stats['home_goals'] * (1 + (strength_factor - 1) * 0.3)
    away_goals_expected = away_stats['away_goals'] * (1 + (1/strength_factor - 1) * 0.2)
    
    max_goals = 5
    home_win = draw = away_win = 0.0
    
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            p = poisson.pmf(i, home_goals_expected) * poisson.pmf(j, away_goals_expected)
            if i > j: 
                home_win += p
            elif i == j: 
                draw += p
            else: 
                away_win += p
    
    corners_home = 5.5 + (home_stats['strength'] - 75) * 0.05
    corners_away = 4.5 + (away_stats['strength'] - 75) * 0.03
    
    return {
        "home_win": round(home_win, 3),
        "draw": round(draw, 3),
        "away_win": round(away_win, 3),
        "total_goals": round(home_goals_expected + away_goals_expected, 1),
        "total_corners": round(corners_home + corners_away, 1)
    }

def get_corners_prediction(home_team, away_team, df):
    """חיזוי קרנות עם טיפול משופר בשגיאות"""
    try:
        if 'HC' in df.columns and 'AC' in df.columns:
            home_matches = find_team_in_data(home_team, df, 'HomeTeam')
            away_matches = find_team_in_data(away_team, df, 'AwayTeam')
            
            if not home_matches.empty and 'HC' in home_matches.columns:
                home_corners = home_matches['HC'].mean()
            else:
                home_corners = None
            
            if not away_matches.empty and 'AC' in away_matches.columns:
                away_corners = away_matches['AC'].mean()
            else:
                away_corners = None
            
            if home_corners is not None and away_corners is not None:
                if not pd.isna(home_corners) and not pd.isna(away_corners):
                    return round(home_corners + away_corners, 1)
    except:
        pass
    
    return None

def predict_match(home_team, away_team, league, df=None):
    if league in ['Champions League', 'Europa League', 'Conference League']:
        return predict_match_european(home_team, away_team, league)
    else:
        return predict_match_regular(home_team, away_team, df)

# ----------------------------
# ממשק משתמש
# ----------------------------
# טעינת נתונים
with st.spinner('🔄 טוען נתונים...'):
    data = load_league_data()

# הוספת אפשרות לטעינת קובץ ידנית
with st.sidebar:
    st.header("⚙️ הגדרות")
    
    # אפשרות להעלות קובץ CSV
    st.subheader("📁 העלה נתונים משלך")
    uploaded_file = st.file_uploader("בחר קובץ CSV", type=['csv'])
    
    if uploaded_file is not None:
        try:
            custom_df = pd.read_csv(uploaded_file)
            custom_df = standardize_column_names(custom_df)
            
            # ניקוי שמות קבוצות
            if 'HomeTeam' in custom_df.columns:
                custom_df['HomeTeam'] = custom_df['HomeTeam'].apply(clean_team_name)
            if 'AwayTeam' in custom_df.columns:
                custom_df['AwayTeam'] = custom_df['AwayTeam'].apply(clean_team_name)
            
            custom_league = st.text_input("שם הליגה", value="Custom League")
            if st.button("הוסף ליגה"):
                data[custom_league] = custom_df
                LEAGUE_TEAMS[custom_league] = list(pd.concat([custom_df['HomeTeam'], custom_df['AwayTeam']]).unique())
                st.success(f"✅ הליגה {custom_league} נוספה בהצלחה!")
                st.rerun()
        except Exception as e:
            st.error(f"שגיאה בקריאת הקובץ: {str(e)}")
    
    st.divider()
    
    # הצגת סטטוס נתונים
    st.subheader("📊 סטטוס נתונים")
    for league in data.keys():
        if league in data:
            st.success(f"✅ {league}")
    
    # ליגות ללא נתונים
    all_leagues = set()
    for category_leagues in league_categories.values():
        all_leagues.update(category_leagues)
    
    missing_leagues = all_leagues - set(data.keys())
    if missing_leagues:
        st.subheader("⚠️ ליגות ללא נתונים")
        for league in missing_leagues:
            st.warning(f"❌ {league}")

# קיבוץ הליגות
league_categories = {
    "🏆 ליגות אירופיות": ['Champions League', 'Europa League', 'Conference League'],
    "🇪🇺 ליגות ראשונות": ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1'],
    "🏟️ ליגות שניות": ['Championship', 'Segunda División'],
    "🇮🇱 ליגה ישראלית": ['Israeli Premier League']
}

# הוספת קטגוריה לליגות מותאמות אישית
if any(league not in sum(league_categories.values(), []) for league in data.keys()):
    custom_leagues = [league for league in data.keys() if league not in sum(league_categories.values(), [])]
    if custom_leagues:
        league_categories["🔧 ליגות מותאמות"] = custom_leagues

# בחירת קטגוריה וליגה
selected_category = st.selectbox("בחר קטגוריה", options=list(league_categories.keys()))
available_leagues = league_categories[selected_category]

# סינון רק ליגות זמינות
available_leagues_with_data = [l for l in available_leagues if l in LEAGUE_TEAMS]

if not available_leagues_with_data:
    st.error(f"❌ אין ליגות זמינות בקטגוריה {selected_category}")
    st.info("💡 נסה קטגוריה אחרת או העלה קובץ נתונים בסרגל הצדדי")
    st.stop()

selected_league = st.selectbox("בחר ליגה", options=available_leagues_with_data)

if selected_league in LEAGUE_TEAMS:
    teams = LEAGUE_TEAMS[selected_league]
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("קבוצה ביתית", options=teams)
    
    with col2:
        away_team = st.selectbox("קבוצה אורחת", options=[t for t in teams if t != home_team])
    
    # הצגת מידע על זמינות הנתונים
    if selected_league not in ['Champions League', 'Europa League', 'Conference League']:
        if selected_league in data and not data[selected_league].empty:
            st.success(f"✅ נתונים זמינים עבור {selected_league}")
            with st.expander("📊 פרטי הנתונים"):
                df = data[selected_league]
                st.write(f"מספר משחקים: {len(df)}")
                if 'HomeTeam' in df.columns and 'AwayTeam' in df.columns:
                    unique_teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique()
                    st.write(f"קבוצות בנתונים: {len(unique_teams)}")
                    if st.checkbox("הצג רשימת קבוצות בנתונים"):
                        st.write(sorted([t for t in unique_teams if pd.notna(t)]))
        else:
            st.warning(f"⚠️ אין נתונים זמינים עבור {selected_league} - משתמש בערכי ברירת מחדל")
    
    if st.button("חשב חיזוי ⚡", type="primary", use_container_width=True):
        with st.spinner('מחשב חיזוי...'):
            try:
                if selected_league in ['Champions League', 'Europa League', 'Conference League']:
                    prediction = predict_match(home_team, away_team, selected_league)
                elif selected_league in data and not data[selected_league].empty:
                    prediction = predict_match(home_team, away_team, selected_league, data[selected_league])
                else:
                    # יצירת DataFrame ריק עם ערכי ברירת מחדל
                    st.warning("משתמש בערכי ברירת מחדל")
                    empty_df = pd.DataFrame(columns=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
                    prediction = predict_match(home_team, away_team, selected_league, empty_df)
                
                # הצגת תוצאות
                st.subheader("🔮 תוצאות חיזוי:")
                
                # גרף עוגה להסתברויות
                import plotly.graph_objects as go
                
                fig = go.Figure(data=[go.Pie(
                    labels=[f'{home_team} (ניצחון)', 'תיקו', f'{away_team} (ניצחון)'],
                    values=[prediction['home_win'], prediction['draw'], prediction['away_win']],
                    hole=.3,
                    marker_colors=['#2ecc71', '#95a5a6', '#e74c3c']
                )])
                fig.update_layout(
                    title=f"{home_team} vs {away_team}",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # הסתברויות
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label=f"🏠 {home_team}", 
                        value=f"{prediction['home_win']*100:.1f}%",
                        delta="ניצחון ביתי" if prediction['home_win'] > 0.4 else None
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
                        delta="ניצחון חוץ" if prediction['away_win'] > 0.4 else None
                    )
                
                st.divider()
                
                # סטטיסטיקות נוספות
                st.subheader("📊 סטטיסטיקות נוספות")
                col1, col2 = st.columns(2)
                
                with col1:
                    goals_color = "🔴" if prediction['total_goals'] > 3 else "🟡" if prediction['total_goals'] > 2.5 else "🟢"
                    st.metric(f"{goals_color} שערים צפויים", f"{prediction['total_goals']}")
                
                with col2:
                    if prediction['total_corners'] is not None:
                        st.metric("🚩 קרנות צפויות", f"{prediction['total_corners']}")
                    else:
                        st.metric("🚩 קרנות צפויות", "לא זמין")
                
                # המלצות הימור
                st.subheader("💡 המלצות")
                
                # המלצה ראשית
                max_prob = max(prediction['home_win'], prediction['draw'], prediction['away_win'])
                
                if max_prob == prediction['home_win']:
                    st.success(f"🏠 **ההימור המומלץ: ניצחון ל־{home_team}** ({prediction['home_win']*100:.1f}%)")
                elif max_prob == prediction['draw']:
                    st.success(f"🤝 **ההימור המומלץ: תיקו** ({prediction['draw']*100:.1f}%)")
                else:
                    st.success(f"✈️ **ההימור המומלץ: ניצחון ל־{away_team}** ({prediction['away_win']*100:.1f}%)")
                
                # המלצות נוספות
                col1, col2 = st.columns(2)
                
                with col1:
                    if prediction['total_goals'] > 2.5:
                        st.info(f"⚽ **מעל 2.5 שערים** (צפוי: {prediction['total_goals']})")
                    else:
                        st.info(f"🛡️ **מתחת ל-2.5 שערים** (צפוי: {prediction['total_goals']})")
                
                with col2:
                    if prediction['total_goals'] > 3.5:
                        st.info(f"🔥 **משחק פתוח** - המלצה: מעל 3.5")
                    elif prediction['total_goals'] < 2:
                        st.info(f"🔒 **משחק סגור** - המלצה: מתחת ל-2.5")
                    else:
                        st.info(f"⚖️ **משחק מאוזן** - 2-3 שערים צפויים")
                
                # כפתור לחיזוי נוסף
                if st.button("🔄 חיזוי נוסף", use_container_width=True):
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ שגיאה בחישוב החיזוי: {str(e)}")
                st.info("נסה לבחור קבוצות אחרות או ליגה אחרת")

else:
    st.error("שגיאה בטעינת נתוני הליגה")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("*נבנה עם ❤️ לחובבי כדורגל*")
with col2:
    st.markdown("*עונת 2025/2026*")
with col3:
    st.markdown("*הימורו באחריות*")