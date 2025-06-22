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
# קבוצות לפי ליגה - מעודכן לפי UEFA 2025/26
# ----------------------------
LEAGUE_TEAMS = {
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
    'Serie A': [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Empoli', 'Fiorentina',
        'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza',
        'Napoli', 'Parma', 'Roma', 'Torino', 'Udinese', 'Venezia', 'Verona'
    ],
    'Bundesliga': [
        'Augsburg', 'Bayern Munich', 'Bochum', 'Dortmund', 'Ein Frankfurt',
        'Freiburg', 'Heidenheim', 'Hoffenheim', 'Holstein Kiel', 'Leverkusen',
        "M'gladbach", 'Mainz', 'RB Leipzig', 'St Pauli', 'Stuttgart',
        'Union Berlin', 'Werder Bremen', 'Wolfsburg'
    ],
    'Ligue 1': [
        'Angers', 'Auxerre', 'Brest', 'Le Havre', 'Lens', 'Lille', 'Lyon',
        'Marseille', 'Monaco', 'Montpellier', 'Nantes', 'Nice', 'Paris SG',
        'Reims', 'Rennes', 'St Etienne', 'Strasbourg', 'Toulouse'
    ],
    'Israeli Premier League': [
        'Maccabi Tel Aviv', 'Maccabi Haifa', 'Hapoel Beer Sheva', 'Beitar Jerusalem',
        'Hapoel Tel Aviv', 'Maccabi Netanya', 'Hapoel Haifa', 'Ashdod',
        'Hapoel Jerusalem', 'Bnei Sakhnin', 'Maccabi Bnei Raina', 'Ironi Kiryat Shmona',
        'Hapoel Katamon', 'Hapoel Petah Tikva', 'Hapoel Hadera', 'Maccabi Petah Tikva'
    ],
    # UEFA Champions League 2025/26 - כולל קבוצות מהמוקדמות
    'Champions League': [
        # מקומות ישירים לליגה
        'Paris SG',  # אלופי 2024/25
        'Tottenham',  # אלופי יורופה ליג 2024/25
        'Liverpool', 'Arsenal', 'Man City', 'Chelsea',  # אנגליה (4)
        'Newcastle', 'Villarreal',  # European Performance Spots
        'Napoli', 'Inter', 'Atalanta', 'Juventus',  # איטליה (4)
        'Barcelona', 'Real Madrid', 'Ath Madrid', 'Athletic Club',  # ספרד (4)
        'Bayern Munich', 'Leverkusen', 'Ein Frankfurt', 'Dortmund',  # גרמניה (4)
        'Marseille', 'Monaco',  # צרפת (יתר)
        'PSV', 'Ajax',  # הולנד (2)
        'Sporting CP',  # פורטוגל (1)
        'Union SG',  # בלגיה (1)
        'Galatasaray',  # טורקיה (1)
        'Slavia Praha',  # צ'כיה (1)
        'Olympiacos',  # יוון - Champions League winner rebalancing
        
        # קבוצות מהסיבוב הראשון של המוקדמות
        'Žalgiris', 'Hamrun Spartans',  # ליטא, מלטה
        'KuPS', 'Milsami',  # פינלנד, מולדובה
        'New Saints', 'Shkëndija',  # ויילס, מקדוניה הצפונית
        'Iberia 1999', 'Malmö',  # גאורגיה, שוודיה
        'Levadia', 'RFS',  # אסטוניה, לטביה
        'Drita', 'Differdange 03',  # קוסובו, לוקסמבורג
        'Víkingur', 'Lincoln Red Imps',  # איי פארו, גיברלטר
        'Egnatia', 'Breidablik',  # אלבניה, איסלנד
        'Shelbourne', 'Linfield',  # אירלנד, צפון אירלנד
        'FCSB', 'Inter d\'Escaldes',  # רומניה, אנדורה
        'Virtus', 'Zrinjski',  # סן מרינו, בוסניה
        'Olimpija Ljubljana', 'Kairat',  # סלובניה, קזחסטן
        'Noah', 'Budućnost',  # ארמניה, מונטנגרו
        'Ludogorets', 'Dinamo Minsk',  # בולגריה, בלארוס
        
        # קבוצות מהסיבוב השני - League Path
        'Rangers', 'Panathinaikos',  # סקוטלנד, יוון
        'Salzburg', 'Servette',  # אוסטריה, שווייץ
        'Viktoria Plzen', 'Brann'  # צ'כיה, נורווגיה
    ],
    # UEFA Europa League 2025/26 - כולל קבוצות מהמוקדמות
    'Europa League': [
        # קבוצות עם מקומות ישירים לליגה
        'Man United', 'West Ham', 'Brighton',  # אנגליה
        'Roma', 'Lazio', 'Fiorentina', 'Torino',  # איטליה
        'Betis', 'Sociedad', 'Sevilla', 'Valencia', 'Celta',  # ספרד
        'Hoffenheim', 'Union Berlin', 'Mainz', 'Freiburg',  # גרמניה
        'Nice', 'Rennes', 'Lens', 'Strasbourg',  # צרפת
        'AZ Alkmaar', 'Twente', 'Utrecht',  # הולנד
        'Braga', 'Vitoria Guimaraes',  # פורטוגל
        'Fenerbahce', 'Besiktas',  # טורקיה
        'PAOK', 'AEK Athens',  # יוון
        'Dinamo Zagreb',  # קרואטיה - Conference League winner rebalancing
        'Ludogorets',  # בולגריה
        'CFR Cluj',  # רומניה
        'Viktoria Plzen',  # צ'כיה
        'Anderlecht',  # בלגיה
        'Copenhagen',  # דנמרק
        'Molde',  # נורווגיה
        'Malmo',  # שוודיה
        'Rapid Vienna',  # אוסטריה
        
        # קבוצות מהסיבוב הראשון של המוקדמות
        'Shakhtar Donetsk', 'Ilves',  # אוקראינה, פינלנד
        'Sheriff Tiraspol', 'Prishtina',  # מולדובה, קוסובו
        'Spartak Trnava', 'Häcken',  # סלובקיה, שוודיה
        'Sabah', 'Celje',  # אזרבייג'ן, סלובניה
        'Legia Warsaw', 'Aktobe',  # פולין, קזחסטן
        'Levski Sofia', 'Hapoel Beer Sheva',  # בולגריה, ישראל
        'AEK Larnaca', 'Partizan',  # קפריסין, סרביה
        'Paksi', 'CFR Cluj',  # הונגריה, רומניה
        
        # קבוצות מהסיבוב השני
        'Lugano',  # שווייץ
        'Midtjylland', 'Hibernian',  # דנמרק, סקוטלנד
        'Ostrava'  # צ'כיה
    ],
    # UEFA Conference League 2025/26 - כולל קבוצות מהמוקדמות
    'Conference League': [
        # כל הקבוצות נכנסות דרך מוקדמות - רשימה מורחבת
        'Crystal Palace', 'Fulham', 'Brentford',  # אנגליה
        'Genoa', 'Empoli', 'Monza',  # איטליה
        'Getafe', 'Mallorca', 'Osasuna',  # ספרד
        'Augsburg', 'St Pauli', 'Heidenheim',  # גרמניה
        'Toulouse', 'Montpellier', 'Le Havre',  # צרפת
        'Go Ahead Eagles', 'Vitesse',  # הולנד
        'Hearts', 'Aberdeen', 'Hibernian',  # סקוטלנד
        'Panathinaikos', 'Aris',  # יוון
        'Shamrock Rovers',  # אירלנד
        'Olimpija', 'Celje',  # סלובניה
        'Cercle Brugge', 'Mechelen',  # בלגיה
        'Rosenborg', 'Viking',  # נורווגיה
        'Hammarby', 'Elfsborg',  # שוודיה
        'St Gallen', 'Lugano',  # שווייץ
        'Borac',  # בוסניה
        'Jagiellonia',  # פולין
        'LASK',  # אוסטריה
        'Omonia',  # קפריסין
        'Maccabi Haifa', 'Beitar Jerusalem',  # ישראל
        'Dinamo Tbilisi',  # גאורגיה
        'Ararat-Armenia',  # ארמניה
        'Ballkani',  # קוסובו
        'Cukaricki',  # סרביה
        'Hajduk Split',  # קרואטיה
        'Domzale',  # סלובניה
        'Arda',  # בולגריה
        'Rapid Bucharest',  # רומניה
        'Zilina',  # סלובקיה
        'Jablonec',  # צ'כיה
        'Ujpest',  # הונגריה
        'Warta Poznan',  # פולין
        'KuPS',  # פינלנד
        'Paide',  # אסטוניה
        'Valmiera',  # לטביה
        'Vaduz',  # ליכטנשטיין
        'Akureyri',  # איסלנד
        'Dungannon Swifts',  # צפון אירלנד
        'Strassen',  # לוקסמבורג
        'Banga',  # ליטא
        'Dinamo Tirana',  # אלבניה
        'Petrocub',  # מולדובה
        'Zira',  # אזרבייג'ן
        'Torpedo Kutaisi',  # גאורגיה
        'Alashkert',  # ארמניה
        'Llapi',  # קוסובו
        'Osijek',  # קרואטיה
        'Universitatea Craiova',  # רומניה
        'Dunajska Streda',  # סלובקיה
        'Puskas Academy',  # הונגריה
        'Lechia Gdansk',  # פולין
        'FC Inter Turku',  # פינלנד
        'Honka',  # פינלנד
        'Kalju',  # אסטוניה
        'Liepaja',  # לטביה
        'Jelgava',  # לטביה
        'FCB Magpies'  # גיברלטר
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
    except:
        return None

@st.cache_data(ttl=3600)
def load_league_data():
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
    if df is None or df.empty:
        # חיזוי בסיסי עם יתרון בית
        return {
            "home_win": 0.42,
            "draw": 0.28,
            "away_win": 0.30,
            "total_goals": 2.6,
            "total_corners": 10.5
        }
    
    # בדיקה אם יש נתונים עבור הקבוצות
    home_games = df[df['HomeTeam'] == home_team] if 'HomeTeam' in df.columns else pd.DataFrame()
    away_games = df[df['AwayTeam'] == away_team] if 'AwayTeam' in df.columns else pd.DataFrame()
    
    if home_games.empty or away_games.empty:
        return {
            "home_win": 0.42,
            "draw": 0.28,
            "away_win": 0.30,
            "total_goals": 2.6,
            "total_corners": 10.5
        }
    
    # חישוב ממוצעי שערים
    home_goals = home_games['FTHG'].mean() if 'FTHG' in df.columns and not home_games['FTHG'].empty else 1.5
    away_goals = away_games['FTAG'].mean() if 'FTAG' in df.columns and not away_games['FTAG'].empty else 1.2
    
    # הוספת יתרון בית
    home_goals *= 1.15
    away_goals *= 0.95
    
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
    total_corners = 10.5
    if 'HC' in df.columns and 'AC' in df.columns:
        home_corners = home_games['HC'].mean() if not home_games['HC'].empty else 5.5
        away_corners = away_games['AC'].mean() if not away_games['AC'].empty else 5.0
        total_corners = round(home_corners + away_corners, 1)
    
    return {
        "home_win": round(home_win, 3),
        "draw": round(draw, 3),
        "away_win": round(away_win, 3),
        "total_goals": round(home_goals + away_goals, 1),
        "total_corners": total_corners
    }

# ----------------------------
# ממשק משתמש
# ----------------------------

# טעינת נתונים
data = load_league_data()

# קיבוץ ליגות
league_categories = {
    "🏆 תחרויות UEFA 2025/26": ['Champions League', 'Europa League', 'Conference League'],
    "🇮🇱 ליגת העל הישראלית": ['Israeli Premier League'],
    "🇪🇺 ליגות הטופ באירופה": ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
}

# בחירת ליגה
st.markdown("### 🏟️ בחר תחרות ומשחק")

selected_category = st.selectbox("בחר קטגוריה", options=list(league_categories.keys()))
available_leagues = league_categories[selected_category]
selected_league = st.selectbox("בחר ליגה/תחרות", options=available_leagues)

if selected_league in LEAGUE_TEAMS:
    teams = LEAGUE_TEAMS[selected_league]
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 קבוצה ביתית", options=teams)
    
    with col2:
        away_team = st.selectbox("✈️ קבוצה אורחת", options=[t for t in teams if t != home_team])
    
    # כפתור חיזוי
    if st.button("🔮 חשב חיזוי", type="primary"):
        
        # חיזוי המשחק
        if selected_league in data:
            prediction = predict_match(home_team, away_team, data[selected_league])
        else:
            prediction = predict_match(home_team, away_team, None)
        
        # הצגת תוצאות
        st.markdown("---")
        st.subheader("🎯 תוצאות החיזוי")
        
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
        st.subheader("📊 סטטיסטיקות המשחק")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("⚽ שערים צפויים", f"{prediction['total_goals']}")
        
        with col2:
            st.metric("🚩 קרנות צפויות", f"{prediction['total_corners']}")
        
        # המלצות
        st.markdown("---")
        st.subheader("💡 המלצות הימור")
        
        max_prob = max(prediction['home_win'], prediction['draw'], prediction['away_win'])
        
        if max_prob == prediction['home_win']:
            st.success(f"🏠 **ההימור המומלץ**: ניצחון ל-{home_team} ({prediction['home_win']*100:.1f}%)")
        elif max_prob == prediction['draw']:
            st.success(f"🤝 **ההימור המומלץ**: תיקו ({prediction['draw']*100:.1f}%)")
        else:
            st.success(f"✈️ **ההימור המומלץ**: ניצחון ל-{away_team} ({prediction['away_win']*100:.1f}%)")
        
        # המלצות נוספות לשערים
        if prediction['total_goals'] > 2.5:
            st.info(f"⚽ **משחק התקפי**: המלצה על מעל 2.5 שערים (צפוי: {prediction['total_goals']})")
        else:
            st.info(f"🛡️ **משחק הגנתי**: המלצה על מתחת ל-2.5 שערים (צפוי: {prediction['total_goals']})")

# מידע נוסף
with st.expander("ℹ️ אודות השיטה וההחדשות"):
    st.markdown("""
    ### 🆕 עדכונים עונת 2025/26:
    
    **תחרויות UEFA מעודכנות לפי האתר הרשמי:**
    - 🏆 **ליגת האלופות**: 36 קבוצות בפורמט חדש
    - 🥈 **ליגת אירופה**: תוספת קבוצות מאלופת Conference League
    - 🥉 **ליגת הקונפרנס**: כל הקבוצות דרך מוקדמות
    
    **שיטת החיזוי:**
    - 📊 מבוסס על נתונים היסטוריים אמיתיים (כשזמינים)
    - 🏠 התחשבות ביתרון בית (15% יותר שערים)
    - 📈 התפלגות פואסון למשחקי כדורגל
    - ⚽ חיזוי שערים וקרנות על בסיס ביצועים קודמים
    
    **נתונים:**
    - 🔄 עדכון אוטומטי מ-GitHub
    - 🌐 תמיכה בכל הליגות הגדולות
    - 🎯 דיוק גבוה יותר לליגות עם נתונים היסטוריים
    """)

st.markdown("---")
st.markdown("*⚽ מעודכן לפי נתוני UEFA הרשמיים לעונת 2025/26*")