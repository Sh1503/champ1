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
        'Angers', 'Auxerre', 'Brest', 'Le Havre', 'Lens', 'Lille', 'Lyon',
        'Marseille', 'Monaco', 'Montpellier', 'Nantes', 'Nice', 'Paris SG',
        'Reims', 'Rennes', 'St Etienne', 'Strasbourg', 'Toulouse'
    ],
    'Serie A': [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Empoli', 'Fiorentina',
        'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza',
        'Napoli', 'Parma', 'Roma', 'Torino', 'Udinese', 'Venezia', 'Verona'
    ],
    'ליגת העל הישראלית': [
        'מכבי תל אביב', 'מכבי חיפה', 'הפועל באר שבע', 'הפועל תל אביב', 
        'בני סכנין', 'מכבי פתח תקוה', 'הפועל חיפה', 'עירוני קריית שמונה',
        'מכבי נתניה', 'מכבי בני ריינה', 'הפועל עכו', 'אשדוד',
        'הפועל כפר סבא', 'הפועל ירושלים'
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
    'Atalanta': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 78},
    'Man United': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 77},
    'Tottenham': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 76}
}

# נתוני ביצועים של קבוצות ישראליות
ISRAELI_TEAM_STATS = {
    'מכבי תל אביב': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 75},
    'מכבי חיפה': {'home_goals': 1.9, 'away_goals': 1.4, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 72},
    'הפועל באר שבע': {'home_goals': 1.8, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 70},
    'הפועל תל אביב': {'home_goals': 1.7, 'away_goals': 1.2, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 68},
    'בני סכנין': {'home_goals': 1.5, 'away_goals': 1.0, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 65},
    'מכבי פתח תקוה': {'home_goals': 1.4, 'away_goals': 0.9, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 62},
    'הפועל חיפה': {'home_goals': 1.6, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 64},
    'עירוני קריית שמונה': {'home_goals': 1.3, 'away_goals': 0.8, 'home_conceded': 1.6, 'away_conceded': 1.9, 'strength': 60}
}

def get_team_stats(team, league_type):
    """קבלת סטטיסטיקות קבוצה"""
    if team in EUROPEAN_TEAM_STATS:
        return EUROPEAN_TEAM_STATS[team]
    
    if team in ISRAELI_TEAM_STATS:
        return ISRAELI_TEAM_STATS[team]
    
    if league_type == 'Champions League':
        return {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 76}
    elif league_type == 'Europa League':
        return {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 71}
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
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/epl.csv",
            "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
            "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
        ],
        "Championship": [
            "https://www.football-data.co.uk/mmz4281/2526/E1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/E1.csv"
        ],
        "La Liga": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/laliga.csv",
            "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/SP1.csv"
        ],
        "Segunda División": [
            "https://www.football-data.co.uk/mmz4281/2526/SP2.csv",
            "https://www.football-data.co.uk/mmz4281/2425/SP2.csv"
        ],
        "Serie A": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/seriea.csv",
            "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/I1.csv"
        ],
        "Bundesliga": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/bundesliga.csv",
            "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/D1.csv"
        ],
        "Ligue 1": [
            "https://raw.githubusercontent.com/sh1503/football-match-predictor/main/ligue1.csv",
            "https://www.football-data.co.uk/mmz4281/2526/F1.csv",
            "https://www.football-data.co.uk/mmz4281/2425/F1.csv"
        ]
    }
    
    league_data = {}
    for league, urls in data_sources.items():
        for url in urls:
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
            except:
                continue
    
    return league_data

# ----------------------------
# פונקציות חיזוי
# ----------------------------
def predict_match_with_data(home_team, away_team, df):
    """חיזוי משחק על בסיס נתונים"""
    try:
        # חיפוש משחקי בית של הקבוצה הביתית
        home_matches = df[df['HomeTeam'].str.contains(home_team, case=False, na=False)]
        # חיפוש משחקי חוץ של הקבוצה האורחת
        away_matches = df[df['AwayTeam'].str.contains(away_team, case=False, na=False)]
        
        # חישוב ממוצעי שערים
        if len(home_matches) > 0:
            home_goals_avg = home_matches['FTHG'].mean()
        else:
            home_goals_avg = df['FTHG'].mean() if 'FTHG' in df.columns else 1.5
            
        if len(away_matches) > 0:
            away_goals_avg = away_matches['FTAG'].mean()
        else:
            away_goals_avg = df['FTAG'].mean() if 'FTAG' in df.columns else 1.2
        
        # וידוא שהערכים תקינים
        if pd.isna(home_goals_avg) or home_goals_avg <= 0:
            home_goals_avg = 1.5
        if pd.isna(away_goals_avg) or away_goals_avg <= 0:
            away_goals_avg = 1.2
        
        # חישוב הסתברויות באמצעות פואסון
        max_goals = 5
        home_win = draw = away_win = 0.0
        
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob = poisson.pmf(i, home_goals_avg) * poisson.pmf(j, away_goals_avg)
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
            'total_goals': round(home_goals_avg + away_goals_avg, 1)
        }
    except:
        # ערכי ברירת מחדל במקרה של שגיאה
        return {
            'home_win': 0.45,
            'draw': 0.30,
            'away_win': 0.25,
            'total_goals': 2.5
        }

def predict_match_european_and_israeli(home_team, away_team, league_type):
    """חיזוי משחק אירופי או ישראלי"""
    home_stats = get_team_stats(home_team, league_type)
    away_stats = get_team_stats(away_team, league_type)
    
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
        'total_goals': round(home_goals + away_goals, 1)
    }

# ----------------------------
# ממשק משתמש
# ----------------------------

# קיבוץ הליגות
league_categories = {
    "🏆 ליגות אירופיות": ['Champions League', 'Europa League'],
    "🇬🇧 אנגליה": ['Premier League', 'Championship'],
    "🇪🇸 ספרד": ['La Liga', 'Segunda División'],
    "🇮🇹 איטליה": ['Serie A'],
    "🇩🇪 גרמניה": ['Bundesliga'],
    "🇫🇷 צרפת": ['Ligue 1'],
    "🇮🇱 ישראל": ['ליגת העל הישראלית']
}

# טעינת נתונים
with st.spinner('טוען נתונים...'):
    data = load_league_data()

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
        if selected_league in ['Champions League', 'Europa League', 'ליגת העל הישראלית']:
            prediction = predict_match_european_and_israeli(home_team, away_team, selected_league)
        elif selected_league in data:
            prediction = predict_match_with_data(home_team, away_team, data[selected_league])
        else:
            # אם אין נתונים, נשתמש בערכי ברירת מחדל
            st.warning("אין נתונים זמינים לליגה זו, משתמש בערכים כלליים")
            prediction = {
                'home_win': 0.45,
                'draw': 0.30,
                'away_win': 0.25,
                'total_goals': 2.5
            }
        
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