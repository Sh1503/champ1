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
# קבוצות לפי ליגה
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
    'La Liga': [
        'Alaves', 'Almeria', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis',
        'Cadiz', 'Celta', 'Getafe', 'Girona', 'Las Palmas', 'Leganes',
        'Mallorca', 'Osasuna', 'Real Madrid', 'Sevilla', 'Sociedad',
        'Valencia', 'Valladolid', 'Villarreal'
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
        'Maccabi Tel Aviv', 'Maccabi Haifa', 'Hapoel Beer Sheva', 'Beitar Jerusalem',
        'Hapoel Tel Aviv', 'Maccabi Netanya', 'Hapoel Haifa', 'Ashdod',
        'Hapoel Jerusalem', 'Bnei Sakhnin', 'Maccabi Bnei Raina', 'Ironi Kiryat Shmona',
        'Hapoel Katamon', 'Hapoel Petah Tikva', 'Hapoel Hadera', 'Maccabi Petah Tikva'
    ],
    'Champions League': [
        'Real Madrid', 'Barcelona', 'Ath Madrid', 'Athletic Bilbao',
        'Bayern Munich', 'Dortmund', 'RB Leipzig', 'Leverkusen', 'Stuttgart',
        'Inter', 'Milan', 'Juventus', 'Atalanta', 'Bologna',
        'Man City', 'Arsenal', 'Liverpool', 'Chelsea', 'Aston Villa', 'Newcastle',
        'Paris SG', 'Monaco', 'Lille', 'Brest', 'Lyon',
        'Celtic', 'Rangers', 'PSV', 'Feyenoord', 'Ajax',
        'Benfica', 'Porto', 'Sporting', 'Braga',
        'Maccabi Tel Aviv'
    ],
    'Europa League': [
        'Man United', 'Tottenham', 'West Ham', 'Brighton', 'Fulham',
        'Roma', 'Lazio', 'Fiorentina', 'Napoli', 'Torino',
        'Ein Frankfurt', 'Hoffenheim', 'Union Berlin', 'Mainz',
        'Lyon', 'Nice', 'Marseille', 'Rennes', 'Lens',
        'Villarreal', 'Betis', 'Sociedad', 'Sevilla', 'Valencia',
        'Ajax', 'AZ Alkmaar', 'Twente',
        'Hapoel Beer Sheva', 'Maccabi Haifa'
    ],
    'Conference League': [
        'Chelsea', 'Brighton', 'Fulham', 'Crystal Palace', 'Brentford',
        'Fiorentina', 'Roma', 'Lazio', 'Genoa', 'Empoli',
        'Nice', 'Marseille', 'Rennes', 'Lyon', 'Toulouse',
        'Villarreal', 'Betis', 'Valencia', 'Getafe',
        'Ein Frankfurt', 'Union Berlin', 'Hoffenheim', 'Freiburg',
        'Ajax', 'AZ Alkmaar', 'Twente',
        'Celtic', 'Rangers', 'Hearts', 'Aberdeen',
        'Maccabi Haifa', 'Beitar Jerusalem'
    ]
}

# ----------------------------
# טעינת נתונים מ-GitHub
# ----------------------------
def load_github_data(github_raw_url):
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def load_league_data():
    # קבצים שקיימים בפועל ב-GitHub שלך
    data_sources = {
        "Premier League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/epl.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/premier_league_csv.csv.txt"
        ],
        "La Liga": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/laliga.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/laliga_csv.csv.txt"
        ],
        "Serie A": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/seriea.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/serie_a_csv.csv.txt"
        ],
        "Bundesliga": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/bundesliga.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/bundesliga_csv.csv.txt"
        ],
        "Ligue 1": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/ligue1.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/ligue1_csv.csv.txt"
        ],
        "Israeli Premier League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/israel_league.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/israel.csv.txt",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/israeli_premier_league_csv.csv.txt"
        ],
        "Champions League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/champions_league_csv.csv.txt"
        ],
        "Europa League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/europa_league_csv.csv.txt"
        ],
        "Conference League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/conference_league_csv.csv.txt"
        ]
    }
    
    league_data = {}
    
    for league, urls in data_sources.items():
        combined_df = None
        
        for url in urls:
            df = load_github_data(url)
            if df is not None:
                if combined_df is None:
                    combined_df = df
                else:
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
        
        if combined_df is not None and not combined_df.empty:
            league_data[league] = combined_df
    
    return league_data

# ----------------------------
# פונקציות חיזוי
# ----------------------------
def predict_match(home_team, away_team, df):
    # בדיקה אם יש נתונים עבור הקבוצות
    home_games = df[df['HomeTeam'] == home_team]
    away_games = df[df['AwayTeam'] == away_team]
    
    if home_games.empty or away_games.empty:
        # חיזוי בסיסי אם אין נתונים
        return {
            "home_win": 0.4,
            "draw": 0.3,
            "away_win": 0.3,
            "total_goals": 2.5,
            "total_corners": 10.0
        }
    
    # חישוב ממוצעי שערים
    home_goals = home_games['FTHG'].mean() if 'FTHG' in df.columns else 1.5
    away_goals = away_games['FTAG'].mean() if 'FTAG' in df.columns else 1.2
    
    # חישוב הסתברויות פואסון
    max_goals = 5
    home_win = draw = away_win = 0.0
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = poisson.pmf(i, home_goals) * poisson.pmf(j, away_goals)
            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p
    
    # חישוב קרנות
    total_corners = None
    if 'HC' in df.columns and 'AC' in df.columns:
        home_corners = home_games['HC'].mean()
        away_corners = away_games['AC'].mean()
        total_corners = round(home_corners + away_corners, 1)
    
    return {
        "home_win": round(home_win, 3),
        "draw": round(draw, 3),
        "away_win": round(away_win, 3),
        "total_goals": round(home_goals + away_goals, 1),
        "total_corners": total_corners if total_corners else 10.0
    }

# ----------------------------
# ממשק משתמש
# ----------------------------
st.markdown("### 🏆 בחר ליגה ומשחק לחיזוי")

# טעינת נתונים
data = load_league_data()

# הצגת סטטוס טעינת נתונים
if data:
    st.success(f"✅ נטענו נתונים עבור {len(data)} ליגות")
    for league, df in data.items():
        st.info(f"📊 {league}: {len(df)} משחקים")
else:
    st.warning("⚠️ לא נטענו נתונים מ-GitHub")

# בחירת ליגה
available_leagues = list(LEAGUE_TEAMS.keys())
selected_league = st.selectbox("🏟️ בחר ליגה", options=available_leagues)

# בחירת קבוצות
if selected_league in LEAGUE_TEAMS:
    teams = LEAGUE_TEAMS[selected_league]
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 קבוצה ביתית", options=teams)
    
    with col2:
        away_team = st.selectbox("✈️ קבוצה אורחת", options=[t for t in teams if t != home_team])
    
    # כפתור חיזוי
    if st.button("🔮 חשב חיזוי", type="primary"):
        # בדיקה אם יש נתונים עבור הליגה
        if selected_league in data:
            prediction = predict_match(home_team, away_team, data[selected_league])
            st.success("📊 חיזוי מבוסס על נתונים היסטוריים")
        else:
            # חיזוי בסיסי
            prediction = {
                "home_win": 0.4,
                "draw": 0.3,
                "away_win": 0.3,
                "total_goals": 2.5,
                "total_corners": 10.0
            }
            st.info("🎲 חיזוי בסיסי (אין נתונים היסטוריים)")
        
        # הצגת תוצאות
        st.markdown("---")
        st.subheader("🔮 תוצאות חיזוי")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=f"🏠 {home_team}",
                value=f"{prediction['home_win']*100:.1f}%"
            )
        
        with col2:
            st.metric(
                label="🤝 תיקו",
                value=f"{prediction['draw']*100:.1f}%"
            )
        
        with col3:
            st.metric(
                label=f"✈️ {away_team}",
                value=f"{prediction['away_win']*100:.1f}%"
            )
        
        # סטטיסטיקות נוספות
        st.markdown("---")
        st.subheader("📊 סטטיסטיקות")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("⚽ שערים צפויים", f"{prediction['total_goals']}")
        
        with col2:
            st.metric("🚩 קרנות צפויות", f"{prediction['total_corners']}")
        
        # המלצה
        st.markdown("---")
        max_prob = max(prediction['home_win'], prediction['draw'], prediction['away_win'])
        
        if max_prob == prediction['home_win']:
            st.success(f"💡 המלצה: ניצחון ל-{home_team} ({prediction['home_win']*100:.1f}%)")
        elif max_prob == prediction['draw']:
            st.success(f"💡 המלצה: תיקו ({prediction['draw']*100:.1f}%)")
        else:
            st.success(f"💡 המלצה: ניצחון ל-{away_team} ({prediction['away_win']*100:.1f}%)")

# מידע נוסף
with st.expander("ℹ️ מידע על השיטה"):
    st.markdown("""
    **שיטת החיזוי:**
    - החיזוי מבוסס על נתונים היסטוריים של משחקים קודמים
    - השימוש בהתפלגות פואסון לחישוב הסתברויות
    - חישוב ממוצעי שערים וקרנות לכל קבוצה
    - אם אין נתונים זמינים, מוצג חיזוי בסיסי
    
    **נתונים:**
    - הנתונים נטענים אוטומטית מ-GitHub
    - עדכון אוטומטי כל שעה
    - תמיכה בכל הליגות הגדולות באירופה וישראל
    """)

st.markdown("---")
st.markdown("*⚽ נבנה עם אהבה לכדורגל*")