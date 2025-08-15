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
# מקורות נתונים
# ----------------------------
def load_data_from_multiple_sources(github_urls):
    """טעינת נתונים ממקורות מרובים עם fallback"""
    for i, url in enumerate(github_urls):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
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
            "https://raw.githubusercontent.com/datasets/football-datasets/master/datasets/england/season-2425/E0.csv",
            "https://raw.githubusercontent.com/jokecamp/FootballData/master/football-data.co.uk/england/E0.csv"
        ],
        "Championship": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/E1%202425.csv",
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/E1%202526.csv",
            "https://raw.githubusercontent.com/footballcsv/england/master/2024-25/eng.2.csv",
            "https://raw.githubusercontent.com/datasets/football-datasets/master/datasets/england/season-2425/E1.csv"
        ],
        "La Liga": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/laliga.csv",
            "https://raw.githubusercontent.com/footballcsv/espana/master/2024-25/esp.1.csv",
            "https://raw.githubusercontent.com/datasets/football-datasets/master/datasets/spain/season-2425/SP1.csv",
            "https://raw.githubusercontent.com/jokecamp/FootballData/master/football-data.co.uk/spain/SP1.csv"
        ],
        "Segunda División": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/SP2%202425.csv",
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/SP2%202324.csv",
            "https://raw.githubusercontent.com/footballcsv/espana/master/2024-25/esp.2.csv",
            "https://raw.githubusercontent.com/datasets/football-datasets/master/datasets/spain/season-2425/SP2.csv"
        ],
        "Serie A": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/seriea.csv",
            "https://raw.githubusercontent.com/footballcsv/italy/master/2024-25/it.1.csv",
            "https://raw.githubusercontent.com/datasets/football-datasets/master/datasets/italy/season-2425/I1.csv",
            "https://raw.githubusercontent.com/jokecamp/FootballData/master/football-data.co.uk/italy/I1.csv"
        ],
        "Bundesliga": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/bundesliga.csv",
            "https://raw.githubusercontent.com/footballcsv/deutschland/master/2024-25/de.1.csv",
            "https://raw.githubusercontent.com/datasets/football-datasets/master/datasets/germany/season-2425/D1.csv",
            "https://raw.githubusercontent.com/jokecamp/FootballData/master/football-data.co.uk/germany/D1.csv"
        ],
        "Ligue 1": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/ligue1.csv",
            "https://raw.githubusercontent.com/footballcsv/france/master/2024-25/fr.1.csv",
            "https://raw.githubusercontent.com/datasets/football-datasets/master/datasets/france/season-2425/F1.csv",
            "https://raw.githubusercontent.com/jokecamp/FootballData/master/football-data.co.uk/france/F1.csv"
        ],
        "Israeli Premier League": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/israeli_league.csv",
            "https://raw.githubusercontent.com/footballcsv/cache.footballdata/master/2024-25/il.1.csv",
            "https://raw.githubusercontent.com/schochastics/football-data/master/data/results.csv"
        ]
    }
    
    league_data = {}
    for league, urls in data_sources.items():
        df = load_data_from_multiple_sources(urls)
        if df is not None:
            if 'team1' in df.columns:
                df = df.rename(columns={'team1': 'HomeTeam', 'team2': 'AwayTeam', 'score1': 'FTHG', 'score2': 'FTAG'})
            league_data[league] = df
            st.success(f"✅ נתונים נטענו בהצלחה עבור {league}")
        else:
            st.error(f"❌ לא ניתן לטעון נתונים עבור {league}")
    
    return league_data

# ----------------------------
# פונקציות חיזוי
# ----------------------------
def predict_match_regular(home_team, away_team, df):
    home_matches = df[df['HomeTeam'].str.contains(home_team, case=False, na=False)]
    away_matches = df[df['AwayTeam'].str.contains(away_team, case=False, na=False)]
    
    if home_matches.empty or away_matches.empty:
        home_goals = df['FTHG'].mean() if 'FTHG' in df.columns else 1.5
        away_goals = df['FTAG'].mean() if 'FTAG' in df.columns else 1.2
    else:
        home_goals = home_matches['FTHG'].mean()
        away_goals = away_matches['FTAG'].mean()
    
    max_goals = 5
    home_win = draw = away_win = 0.0
    
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            p = poisson.pmf(i, home_goals) * poisson.pmf(j, away_goals)
            if i > j: home_win += p
            elif i == j: draw += p
            else: away_win += p
    
    return {
        "home_win": round(home_win, 3),
        "draw": round(draw, 3),
        "away_win": round(away_win, 3),
        "total_goals": round(home_goals + away_goals, 1),
        "total_corners": get_corners_prediction(home_team, away_team, df)
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
            if i > j: home_win += p
            elif i == j: draw += p
            else: away_win += p
    
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
    if 'HC' in df.columns and 'AC' in df.columns:
        home_corners = df[df['HomeTeam'].str.contains(home_team, case=False, na=False)]['HC'].mean()
        away_corners = df[df['AwayTeam'].str.contains(away_team, case=False, na=False)]['AC'].mean()
        if not pd.isna(home_corners) and not pd.isna(away_corners):
            return round(home_corners + away_corners, 1)
    return None

def predict_match(home_team, away_team, league, df=None):
    if league in ['Champions League', 'Europa League', 'Conference League']:
        return predict_match_european(home_team, away_team, league)
    else:
        return predict_match_regular(home_team, away_team, df)

# ----------------------------
# ממשק משתמש
# ----------------------------
data = load_league_data()

# קיבוץ הליגות
league_categories = {
    "🏆 ליגות אירופיות": ['Champions League', 'Europa League', 'Conference League'],
    "🇪🇺 ליגות ראשונות": ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1'],
    "🏟️ ליגות שניות": ['Championship', 'Segunda División']
}

# בחירת קטגוריה וליגה
selected_category = st.selectbox("בחר קטגוריה", options=list(league_categories.keys()))
available_leagues = league_categories[selected_category]
selected_league = st.selectbox("בחר ליגה", options=available_leagues)

if selected_league in LEAGUE_TEAMS:
    teams = LEAGUE_TEAMS[selected_league]
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("קבוצה ביתית", options=teams)
    
    with col2:
        away_team = st.selectbox("קבוצה אורחת", options=[t for t in teams if t != home_team])
    
    if st.button("חשב חיזוי ⚡", type="primary"):
        if selected_league in ['Champions League', 'Europa League', 'Conference League']:
            prediction = predict_match(home_team, away_team, selected_league)
        elif selected_league in data and not data[selected_league].empty:
            prediction = predict_match(home_team, away_team, selected_league, data[selected_league])
        else:
            st.error("לא נמצאו נתונים עבור הליגה הנבחרת")
            st.stop()
        
        # הצגת תוצאות
        st.subheader("🔮 תוצאות חיזוי:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=f"🏠 ניצחון ל־{home_team}", value=f"{prediction['home_win']*100:.1f}%")
        with col2:
            st.metric(label="🤝 תיקו", value=f"{prediction['draw']*100:.1f}%")
        with col3:
            st.metric(label=f"✈️ ניצחון ל־{away_team}", value=f"{prediction['away_win']*100:.1f}%")
        
        st.divider()
        
        # סטטיסטיקות נוספות
        st.subheader("📊 סטטיסטיקות נוספות")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("⚽ שערים צפויים", f"{prediction['total_goals']}")
        
        with col2:
            if prediction['total_corners'] is not None:
                st.metric("🚩 קרנות צפויות", f"{prediction['total_corners']}")
            else:
                st.metric("🚩 קרנות צפויות", "לא זמין")
        
        # המלצות הימור
        st.subheader("💡 המלצות")
        max_prob = max(prediction['home_win'], prediction['draw'], prediction['away_win'])
        
        if max_prob == prediction['home_win']:
            st.success(f"🏠 ההימור המומלץ: ניצחון ל־{home_team} ({prediction['home_win']*100:.1f}%)")
        elif max_prob == prediction['draw']:
            st.success(f"🤝 ההימור המומלץ: תיקו ({prediction['draw']*100:.1f}%)")
        else:
            st.success(f"✈️ ההימור המומלץ: ניצחון ל־{away_team} ({prediction['away_win']*100:.1f}%)")
        
        if prediction['total_goals'] > 2.5:
            st.info(f"⚽ משחק עתיר שערים - המלצה: מעל 2.5 שערים ({prediction['total_goals']} צפוי)")
        else:
            st.info(f"🛡️ משחק דחוס - המלצה: מתחת ל-2.5 שערים ({prediction['total_goals']} צפוי)")

else:
    st.error("שגיאה בטעינת נתוני הליגה")

st.markdown("---")
st.markdown("*נבנה עם ❤️ לחובבי כדורגל*")