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
# קבוצות לפי ליגה - עונת 2025/26
# ----------------------------
LEAGUE_TEAMS = {
    'Premier League': [
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
        'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham',
        'Leeds United', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
        "Nott'm Forest", 'Sunderland', 'Tottenham', 'West Ham', 'Wolves'
    ],
    'La Liga': [
        'Alaves', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis',
        'Celta', 'Elche', 'Getafe', 'Girona', 'Las Palmas', 'Levante',
        'Mallorca', 'Osasuna', 'Real Madrid', 'Real Oviedo', 'Sevilla', 
        'Sociedad', 'Valencia', 'Valladolid', 'Villarreal'
    ],
    'Serie A': [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina',
        'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza',
        'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese',
        'Venezia', 'Verona'
    ],
    'Bundesliga': [
        'Augsburg', 'Bayern Munich', 'Bochum', 'Dortmund', 'Ein Frankfurt',
        'FC Koln', 'Freiburg', 'Hamburger SV', 'Heidenheim', 'Hoffenheim', 
        'Holstein Kiel', 'Leverkusen', "M'gladbach", 'Mainz', 'RB Leipzig', 
        'St Pauli', 'Stuttgart', 'Werder Bremen', 'Wolfsburg'
    ],
    'Ligue 1': [
        'Angers', 'Auxerre', 'Brest', 'FC Lorient', 'FC Metz', 'Lens', 
        'Lille', 'Lyon', 'Marseille', 'Monaco', 'Montpellier', 'Nantes', 
        'Nice', 'Paris FC', 'Paris SG', 'Reims', 'Rennes', 'St Etienne', 
        'Strasbourg'
    ],
    'Israeli Premier League': [
        'Maccabi Tel Aviv', 'Maccabi Haifa', 'Hapoel Beer Sheva', 'Beitar Jerusalem',
        'Hapoel Tel Aviv', 'Maccabi Netanya', 'Hapoel Haifa', 'Ashdod',
        'Hapoel Jerusalem', 'Bnei Sakhnin', 'Maccabi Bnei Raina', 'Ironi Kiryat Shmona',
        'Hapoel Katamon', 'Hapoel Petah Tikva'
    ],
    'Champions League': [
        'Paris SG', 'Tottenham', 'Liverpool', 'Arsenal', 'Man City', 'Chelsea',
        'Newcastle', 'Villarreal', 'Napoli', 'Inter', 'Atalanta', 'Juventus',
        'Barcelona', 'Real Madrid', 'Ath Madrid', 'Athletic Club',
        'Bayern Munich', 'Leverkusen', 'Ein Frankfurt', 'Dortmund',
        'Marseille', 'Monaco', 'PSV', 'Ajax', 'Sporting CP', 'Union SG',
        'Galatasaray', 'Slavia Praha', 'Olympiacos', 'Rangers', 'Panathinaikos',
        'Salzburg', 'Servette', 'Viktoria Plzen', 'Brann', 'Žalgiris',
        'Hamrun Spartans', 'KuPS', 'Milsami', 'New Saints', 'Shkëndija',
        'Iberia 1999', 'Malmö', 'Levadia', 'RFS', 'Drita', 'Differdange 03',
        'Víkingur', 'Lincoln Red Imps', 'Egnatia', 'Breidablik', 'Shelbourne',
        'Linfield', 'FCSB', 'Inter d\'Escaldes', 'Virtus', 'Zrinjski',
        'Olimpija Ljubljana', 'Kairat', 'Noah', 'Budućnost', 'Ludogorets',
        'Dinamo Minsk'
    ],
    'Europa League': [
        'Man United', 'West Ham', 'Brighton', 'Roma', 'Lazio', 'Fiorentina',
        'Torino', 'Betis', 'Sociedad', 'Sevilla', 'Valencia', 'Celta',
        'Hoffenheim', 'Union Berlin', 'Mainz', 'Freiburg', 'Nice', 'Rennes',
        'Lens', 'Strasbourg', 'AZ Alkmaar', 'Twente', 'Utrecht', 'Braga',
        'Vitoria Guimaraes', 'Fenerbahce', 'Besiktas', 'PAOK', 'AEK Athens',
        'Dinamo Zagreb', 'Ludogorets', 'CFR Cluj', 'Anderlecht', 'Copenhagen',
        'Molde', 'Malmo', 'Rapid Vienna', 'Shakhtar Donetsk', 'Ilves',
        'Sheriff Tiraspol', 'Prishtina', 'Spartak Trnava', 'Häcken', 'Sabah',
        'Celje', 'Legia Warsaw', 'Aktobe', 'Levski Sofia', 'Hapoel Beer Sheva',
        'AEK Larnaca', 'Partizan', 'Paksi', 'Lugano', 'Midtjylland',
        'Hibernian', 'Ostrava'
    ],
    'Conference League': [
        'Crystal Palace', 'Fulham', 'Brentford', 'Genoa', 'Empoli', 'Monza',
        'Getafe', 'Mallorca', 'Osasuna', 'Augsburg', 'St Pauli', 'Heidenheim',
        'Toulouse', 'Montpellier', 'Le Havre', 'Go Ahead Eagles', 'Vitesse',
        'Hearts', 'Aberdeen', 'Hibernian', 'Panathinaikos', 'Aris',
        'Shamrock Rovers', 'Olimpija', 'Celje', 'Cercle Brugge', 'Mechelen',
        'Rosenborg', 'Viking', 'Hammarby', 'Elfsborg', 'St Gallen', 'Lugano',
        'Borac', 'Jagiellonia', 'LASK', 'Omonia', 'Maccabi Haifa',
        'Beitar Jerusalem', 'Dinamo Tbilisi', 'Ararat-Armenia', 'Ballkani',
        'Cukaricki', 'Hajduk Split', 'Domzale', 'Arda', 'Rapid Bucharest',
        'Zilina', 'Jablonec', 'Ujpest', 'Warta Poznan', 'KuPS', 'Paide',
        'Valmiera', 'Vaduz', 'Akureyri', 'Dungannon Swifts', 'Strassen',
        'Banga', 'Dinamo Tirana', 'Petrocub', 'Zira', 'Torpedo Kutaisi',
        'Alashkert', 'Llapi', 'Osijek', 'Universitatea Craiova',
        'Dunajska Streda', 'Puskas Academy', 'Lechia Gdansk', 'FC Inter Turku',
        'Honka', 'Kalju', 'Liepaja', 'Jelgava', 'FCB Magpies', 'HJK Helsinki',
        'Ordabasy', 'Željezničar', 'Koper', 'SJK Seinäjoki', 'Klaksvík',
        'NSÍ Runavík', 'Partizani', 'Tre Fiori', 'Pyunik'
    ]
}

# ----------------------------
# מיפוי שמות קבוצות
# ----------------------------
TEAM_NAME_MAPPING = {
    "Nott'm Forest": "Nottm Forest",
    "Leeds United": "Leeds",
    "Maccabi Tel Aviv": "Maccabi Tel Aviv",
    "Maccabi Haifa": "Maccabi Haifa", 
    "Hapoel Beer Sheva": "Hapoel Beer Sheva",
    "Beitar Jerusalem": "Beitar Jerusalem",
    "Hapoel Tel Aviv": "Hapoel Tel Aviv",
    "Maccabi Netanya": "Maccabi Netanya",
    "Hapoel Haifa": "Hapoel Haifa",
    "Ashdod": "Ashdod",
    "Hapoel Jerusalem": "Hapoel Jerusalem",
    "Bnei Sakhnin": "Bnei Sakhnin",
    "Maccabi Bnei Raina": "Maccabi Bnei Raina",
    "Ironi Kiryat Shmona": "Ironi Kiryat Shmona",
    "Hapoel Katamon": "Hapoel Katamon",
    "Hapoel Petah Tikva": "Hapoel Petah Tikva",
    # מיפויים נוספים לקבוצות שעלו
    "FC Koln": "FC Cologne",
    "Ein Frankfurt": "Eintracht Frankfurt",
    "M'gladbach": "Borussia Mgladbach",
    "RB Leipzig": "RB Leipzig"
}

def get_team_name_for_data(team_name, league_name):
    """מחזיר שם קבוצה מתאים לנתונים"""
    european_leagues = ['Champions League', 'Europa League', 'Conference League']
    
    if league_name not in european_leagues:
        return TEAM_NAME_MAPPING.get(team_name, team_name)
    
    return team_name

# ----------------------------
# מערכת דירוגים מעודכנת לעונת 2025-26
# ----------------------------
DOMESTIC_LEAGUE_RATINGS = {
    # Premier League
    'Man City': 92, 'Arsenal': 88, 'Liverpool': 87, 'Chelsea': 82,
    'Newcastle': 79, 'Man United': 78, 'Tottenham': 77, 'Brighton': 74,
    'Aston Villa': 73, 'West Ham': 71, 'Crystal Palace': 68, 'Fulham': 67,
    'Brentford': 66, 'Wolves': 65, 'Everton': 64, "Nott'm Forest": 63,
    'Bournemouth': 62, 'Burnley': 58, 'Sunderland': 57, 'Leeds United': 56,
    
    # La Liga - עם הקבוצות החדשות
    'Real Madrid': 94, 'Barcelona': 89, 'Ath Madrid': 84, 'Sevilla': 76,
    'Sociedad': 75, 'Betis': 74, 'Villarreal': 73, 'Ath Bilbao': 72,
    'Valencia': 71, 'Celta': 69, 'Osasuna': 68, 'Getafe': 67,
    'Mallorca': 66, 'Girona': 65, 'Las Palmas': 64, 'Alaves': 61,
    'Valladolid': 60, 'Levante': 59, 'Elche': 58, 'Real Oviedo': 57,
    
    # Serie A - עם הקבוצות החדשות
    'Inter': 87, 'Juventus': 84, 'Milan': 83, 'Napoli': 82, 'Atalanta': 81,
    'Roma': 78, 'Lazio': 77, 'Fiorentina': 74, 'Bologna': 71, 'Torino': 69,
    'Genoa': 68, 'Udinese': 67, 'Monza': 66, 'Parma': 65, 'Venezia': 64,
    'Como': 63, 'Lecce': 61, 'Cagliari': 60, 'Verona': 59, 'Sassuolo': 58,
    'Pisa': 57, 'Cremonese': 56,
    
    # Bundesliga - עם הקבוצות החדשות
    'Bayern Munich': 91, 'Dortmund': 85, 'Leverkusen': 84, 'RB Leipzig': 80,
    'Ein Frankfurt': 76, 'Stuttgart': 75, 'Freiburg': 72, 'Hoffenheim': 69,
    "M'gladbach": 70, 'Wolfsburg': 68, 'Werder Bremen': 67, 'Mainz': 66,
    'Augsburg': 65, 'Heidenheim': 64, 'St Pauli': 63, 'Holstein Kiel': 62,
    'Bochum': 61, 'FC Koln': 60, 'Hamburger SV': 59,
    
    # Ligue 1 - עם הקבוצות החדשות
    'Paris SG': 90, 'Monaco': 79, 'Marseille': 78, 'Lyon': 76, 'Lille': 75,
    'Nice': 74, 'Rennes': 73, 'Lens': 72, 'Strasbourg': 69, 'Brest': 68,
    'Reims': 67, 'Nantes': 66, 'Montpellier': 64, 'St Etienne': 63,
    'Auxerre': 61, 'Angers': 60, 'FC Lorient': 59, 'Paris FC': 58,
    'FC Metz': 57,
    
    # Israeli Premier League
    'Maccabi Tel Aviv': 78, 'Maccabi Haifa': 75, 'Hapoel Beer Sheva': 73,
    'Beitar Jerusalem': 70, 'Hapoel Tel Aviv': 68, 'Maccabi Netanya': 65,
    'Hapoel Haifa': 63, 'Ashdod': 62, 'Hapoel Jerusalem': 61, 'Bnei Sakhnin': 60,
    'Maccabi Bnei Raina': 58, 'Ironi Kiryat Shmona': 57, 'Hapoel Katamon': 56,
    'Hapoel Petah Tikva': 55,
}

# דירוגים לליגות אירופיות
EUROPEAN_LEAGUE_RATINGS = {
    # ליגת האלופות
    'Real Madrid': 98, 'Man City': 96, 'Bayern Munich': 95, 'Paris SG': 94,
    'Barcelona': 93, 'Liverpool': 92, 'Arsenal': 91, 'Inter': 90,
    'Dortmund': 89, 'Chelsea': 88, 'Ath Madrid': 87, 'Milan': 86,
    'Napoli': 85, 'Tottenham': 84, 'Juventus': 83, 'Newcastle': 82,
    'Leverkusen': 81, 'Atalanta': 80, 'Athletic Club': 79, 'Monaco': 78,
    'Villarreal': 77, 'PSV': 76, 'Ajax': 75, 'Sporting CP': 74,
    'Marseille': 73, 'Ein Frankfurt': 72, 'Union SG': 71, 'Galatasaray': 70,
    'Slavia Praha': 69, 'Olympiacos': 68, 'Rangers': 67, 'Salzburg': 66,
    'Viktoria Plzen': 65, 'Panathinaikos': 64, 'Servette': 63, 'Brann': 62,
    'Malmö': 61, 'Ludogorets': 60, 'FCSB': 59, 'Žalgiris': 58,
    'New Saints': 57, 'Levadia': 56, 'Olimpija Ljubljana': 55, 'Noah': 54,
    'Shelbourne': 53, 'Drita': 52, 'Víkingur': 51, 'Egnatia': 50,
    'Hamrun Spartans': 49, 'KuPS': 48, 'Milsami': 47, 'Shkëndija': 46,
    'Iberia 1999': 45, 'RFS': 44, 'Differdange 03': 43, 'Lincoln Red Imps': 42,
    'Breidablik': 41, 'Linfield': 40, 'Inter d\'Escaldes': 39, 'Virtus': 38,
    'Zrinjski': 37, 'Kairat': 36, 'Budućnost': 35, 'Dinamo Minsk': 34,
    
    # ליגת אירופה
    'Man United': 79, 'Roma': 78, 'West Ham': 77, 'Lazio': 76,
    'Betis': 75, 'Brighton': 74, 'Fiorentina': 73, 'Hoffenheim': 72,
    'Nice': 71, 'AZ Alkmaar': 70, 'Sociedad': 69, 'Sevilla': 68,
    'Torino': 67, 'Union Berlin': 66, 'Rennes': 65, 'Twente': 64,
    'Braga': 63, 'Fenerbahce': 62, 'PAOK': 61, 'Dinamo Zagreb': 60,
    'Valencia': 59, 'Celta': 58, 'Mainz': 57, 'Freiburg': 56,
    'Lens': 55, 'Strasbourg': 54, 'Utrecht': 53, 'Vitoria Guimaraes': 52,
    'Besiktas': 51, 'AEK Athens': 50, 'CFR Cluj': 49, 'Anderlecht': 47,
    'Copenhagen': 46, 'Molde': 45, 'Malmo': 44, 'Rapid Vienna': 43,
    'Shakhtar Donetsk': 42, 'Sheriff Tiraspol': 41, 'Spartak Trnava': 40,
    'Sabah': 39, 'Celje': 38, 'Legia Warsaw': 37, 'Levski Sofia': 36,
    'Hapoel Beer Sheva': 35, 'AEK Larnaca': 34, 'Partizan': 33,
    'Paksi': 32, 'Lugano': 31, 'Midtjylland': 30, 'Hibernian': 29,
    'Ostrava': 28, 'Ilves': 27, 'Prishtina': 26, 'Häcken': 25,
    'Aktobe': 24,
    
    # ליגת הקונפרנס
    'Crystal Palace': 59, 'Fulham': 58, 'Brentford': 57, 'Genoa': 56,
    'Empoli': 55, 'Monza': 54, 'Getafe': 53, 'Mallorca': 52,
    'Osasuna': 51, 'Augsburg': 50, 'St Pauli': 49, 'Heidenheim': 48,
    'Toulouse': 47, 'Montpellier': 46, 'Le Havre': 45, 'Go Ahead Eagles': 44,
    'Vitesse': 43, 'Hearts': 42, 'Aberdeen': 41, 'Aris': 39,
    'Shamrock Rovers': 38, 'Olimpija': 37, 'Cercle Brugge': 36,
    'Mechelen': 35, 'Rosenborg': 34, 'Viking': 33, 'Hammarby': 32,
    'Elfsborg': 31, 'St Gallen': 30, 'Borac': 28, 'Jagiellonia': 27,
    'LASK': 26, 'HJK Helsinki': 26, 'Omonia': 25, 'Maccabi Haifa': 24,
    'Beitar Jerusalem': 23, 'Dinamo Tbilisi': 22, 'Torpedo Kutaisi': 22,
    'Ararat-Armenia': 21, 'Ballkani': 20, 'Cukaricki': 19, 'Ordabasy': 18,
    'Hajduk Split': 18, 'Domzale': 17, 'Kalju': 17, 'Arda': 16,
    'Pyunik': 16, 'Rapid Bucharest': 15, 'NSÍ Runavík': 15, 'Zilina': 14,
    'Jablonec': 13, 'Ujpest': 12, 'Warta Poznan': 11, 'Tre Fiori': 10,
    'Paide': 9, 'Valmiera': 8, 'Vaduz': 7, 'Akureyri': 6,
    'Dungannon Swifts': 5, 'Strassen': 4, 'Banga': 3, 'Dinamo Tirana': 2,
    'FCB Magpies': 1, 'Željezničar': 25, 'Koper': 23, 'SJK Seinäjoki': 21,
    'Klaksvík': 19, 'Partizani': 20, 'FC Inter Turku': 18, 'Honka': 17,
    'Liepaja': 8, 'Jelgava': 7, 'Puskas Academy': 12, 'Lechia Gdansk': 11,
    'Universitatea Craiova': 15, 'Dunajska Streda': 14, 'Osijek': 18,
    'Llapi': 16, 'Alashkert': 16, 'Zira': 8, 'Petrocub': 9
}

# ----------------------------
# טעינת נתונים מ-GitHub - מתוקן עם הקבצים הקיימים שלך
# ----------------------------
def load_github_data(github_raw_url):
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        st.warning(f"שגיאה בטעינת נתונים מ-{github_raw_url}: {e}")
        return None

def clean_numeric_columns(df):
    """נקה והמר עמודות מספריות"""
    if df is None or df.empty:
        return df
    
    numeric_cols = [
        'FTHG', 'FTAG', 'HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST', 
        'HF', 'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['', 'nan', 'NaN', 'null', 'NULL'], '0')
            
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
            except Exception as e:
                st.warning(f"בעיה בהמרת עמודה {col}: {e}")
                df[col] = 0
    
    return df

@st.cache_data(ttl=3600)
def load_league_data():
    """טעינת נתונים מתוקנת עם הקבצים הקיימים שלך"""
    data_sources = {
        "Premier League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/premier_league_csv.csv.txt",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/PL2223.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/PL2324.csv"
        ],
        "La Liga": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/laliga_csv.csv.txt",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/LALIGA2223.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/LALIGA2324.csv"
        ],
        "Serie A": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/serie_a_csv.csv.txt",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/SERIE%20A%202223.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/SERIE%20A2324.csv"
        ],
        "Bundesliga": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/bundesliga_csv.csv.txt",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/BUNDESLIGA2223.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/BUNDESLIGA2324.csv"
        ],
        "Ligue 1": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/ligue1_csv.csv.txt",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/LIGUE1%202223.csv",
            "https://raw.githubusercontent.com/Sh1503/champ1/main/LIGUE%201%202324.csv"
        ],
        "Israeli Premier League": [
            "https://raw.githubusercontent.com/Sh1503/champ1/main/israel_league.csv",
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
                df = clean_numeric_columns(df)
                
                if combined_df is None:
                    combined_df = df
                else:
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
        
        if combined_df is not None and not combined_df.empty:
            combined_df = clean_numeric_columns(combined_df)
            league_data[league] = combined_df
    
    return league_data

# ----------------------------
# פונקציות ניתוח ביצועים היסטוריים
# ----------------------------
def analyze_historical_performance(team_name, all_data):
    """ניתוח ביצועים היסטוריים של קבוצה בכל הליגות"""
    
    total_stats = {
        'games_played': 0,
        'wins': 0,
        'draws': 0,
        'losses': 0,
        'goals_scored': 0,
        'goals_conceded': 0
    }
    
    # קבל את שם הקבוצה המתאים לנתונים
    team_variations = [team_name, get_team_name_for_data(team_name, "")]
    
    # חפש בכל הנתונים ההיסטוריים
    for league, df in all_data.items():
        if df is None or df.empty:
            continue
            
        # בדוק עבור כל וריאציות שם הקבוצה
        for team_variant in team_variations:
            # בדוק גם בבית וגם בחוץ
            home_games = df[df['HomeTeam'] == team_variant]
            away_games = df[df['AwayTeam'] == team_variant]
            
            # חשב סטטיסטיקות בית
            for _, game in home_games.iterrows():
                try:
                    home_goals = int(game['FTHG'])
                    away_goals = int(game['FTAG'])
                    
                    total_stats['games_played'] += 1
                    total_stats['goals_scored'] += home_goals
                    total_stats['goals_conceded'] += away_goals
                    
                    if home_goals > away_goals:
                        total_stats['wins'] += 1
                    elif home_goals == away_goals:
                        total_stats['draws'] += 1
                    else:
                        total_stats['losses'] += 1
                except:
                    continue
            
            # חשב סטטיסטיקות חוץ
            for _, game in away_games.iterrows():
                try:
                    home_goals = int(game['FTHG'])
                    away_goals = int(game['FTAG'])
                    
                    total_stats['games_played'] += 1
                    total_stats['goals_scored'] += away_goals
                    total_stats['goals_conceded'] += home_goals
                    
                    if away_goals > home_goals:
                        total_stats['wins'] += 1
                    elif away_goals == home_goals:
                        total_stats['draws'] += 1
                    else:
                        total_stats['losses'] += 1
                except:
                    continue
    
    if total_stats['games_played'] >= 15:  # רק אם יש מספיק משחקים
        return total_stats
    
    return None

def calculate_performance_bonus(stats):
    """חישוב בונוס ביצועים מנתונים היסטוריים"""
    
    if not stats or stats['games_played'] == 0:
        return 0
    
    win_rate = stats['wins'] / stats['games_played']
    avg_goals_scored = stats['goals_scored'] / stats['games_played']
    avg_goals_conceded = stats['goals_conceded'] / stats['games_played']
    goal_difference = avg_goals_scored - avg_goals_conceded
    
    bonus = 0
    
    # בונוס לאחוז ניצחונות
    if win_rate > 0.65:
        bonus += 12
    elif win_rate > 0.55:
        bonus += 8
    elif win_rate > 0.45:
        bonus += 5
    elif win_rate > 0.35:
        bonus += 2
    
    # בונוס ליחס שערים
    if goal_difference > 1.2:
        bonus += 10
    elif goal_difference > 0.8:
        bonus += 7
    elif goal_difference > 0.3:
        bonus += 4
    elif goal_difference > 0:
        bonus += 2
    elif goal_difference > -0.3:
        bonus += 1
    
    # בונוס לכמות שערים (התקפיות)
    if avg_goals_scored > 2.2:
        bonus += 4
    elif avg_goals_scored > 1.8:
        bonus += 2
    elif avg_goals_scored > 1.5:
        bonus += 1
    
    return min(18, bonus)  # מקסימום 18 נקודות בונוס

def calculate_promoted_team_rating(team_name, league_name, all_data):
    """חישוב דירוג מבוסס ביצועים היסטוריים לקבוצות עולות"""
    
    # דירוגי בסיס לקבוצות עולות
    base_ratings = {
        'Premier League': 62,
        'La Liga': 60, 
        'Serie A': 61,
        'Bundesliga': 63,
        'Ligue 1': 59
    }
    
    base_rating = base_ratings.get(league_name, 60)
    
    # נסה למצוא נתונים היסטוריים של הקבוצה
    historical_performance = analyze_historical_performance(team_name, all_data)
    
    if historical_performance:
        performance_bonus = calculate_performance_bonus(historical_performance)
        adjusted_rating = min(78, base_rating + performance_bonus)
        
        # הצג מידע על החישוב
        win_rate = historical_performance['wins'] / historical_performance['games_played']
        avg_goals = historical_performance['goals_scored'] / historical_performance['games_played']
        
        st.info(f"""
        🆕 **דירוג מחושב עבור {team_name}**: {adjusted_rating}/100
        
        📊 **בסיס נתונים היסטוריים**:
        • משחקים: {historical_performance['games_played']}
        • אחוז ניצחונות: {win_rate:.1%}
        • ממוצע שערים: {avg_goals:.1f}
        • בונוס ביצועים: +{performance_bonus} נקודות
        """)
        
        return adjusted_rating
    
    return base_rating

def get_team_rating(team_name, league_name, all_data=None):
    """מחזיר דירוג קבוצה משופר עם תמיכה בקבוצות חדשות"""
    
    european_leagues = ['Champions League', 'Europa League', 'Conference League']
    
    if league_name in european_leagues:
        return EUROPEAN_LEAGUE_RATINGS.get(team_name, 50)
    
    # בדוק אם יש דירוג קיים
    if team_name in DOMESTIC_LEAGUE_RATINGS:
        return DOMESTIC_LEAGUE_RATINGS[team_name]
    
    # אם זו קבוצה חדשה, חשב דירוג מבוסס נתונים היסטוריים
    if all_data:
        calculated_rating = calculate_promoted_team_rating(team_name, league_name, all_data)
        return calculated_rating
    
    # דירוג ברירת מחדל לקבוצות חדשות
    default_ratings = {
        'Premier League': 62,
        'La Liga': 60,
        'Serie A': 61, 
        'Bundesliga': 63,
        'Ligue 1': 59
    }
    
    return default_ratings.get(league_name, 60)

# ----------------------------
# פונקציות חיזוי משופרות
# ----------------------------
def predict_european_match(home_team, away_team, competition_type):
    """חיזוי מתקדם לליגות אירופיות"""
    
    home_rating = get_team_rating(home_team, competition_type)
    away_rating = get_team_rating(away_team, competition_type)
    
    home_advantage = {
        'Champions League': 0.15,
        'Europa League': 0.20,
        'Conference League': 0.25
    }.get(competition_type, 0.20)
    
    home_strength = home_rating * (1 + home_advantage)
    away_strength = away_rating
    
    total_strength = home_strength + away_strength
    
    base_goals = {
        'Champions League': 2.7,
        'Europa League': 2.5,
        'Conference League': 2.3
    }.get(competition_type, 2.5)
    
    home_goals = base_goals * (home_strength / total_strength) * 2
    away_goals = base_goals * (away_strength / total_strength) * 2
    
    home_goals = max(0.5, min(4.0, home_goals))
    away_goals = max(0.5, min(4.0, away_goals))
    
    max_goals = 6
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
    
    corners_base = 10.0
    corners_factor = (home_rating + away_rating) / 100
    total_corners = round(corners_base * corners_factor, 1)
    
    return {
        "home_win": round(home_win, 3),
        "draw": round(draw, 3),
        "away_win": round(away_win, 3),
        "total_goals": round(home_goals + away_goals, 1),
        "total_corners": total_corners,
        "home_rating": home_rating,
        "away_rating": away_rating,
        "is_european": True
    }

def analyze_team_performance(team, df, is_home=True, league_name=None):
    """ניתוח ביצועי קבוצה מתקדם"""
    if df is None or df.empty:
        return None
    
    required_cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
    if not all(col in df.columns for col in required_cols):
        return None
    
    df = clean_numeric_columns(df)
    
    team_name_for_data = get_team_name_for_data(team, league_name)
    
    if is_home:
        team_games = df[df['HomeTeam'] == team_name_for_data].copy()
        goals_scored = 'FTHG'
        goals_conceded = 'FTAG'
    else:
        team_games = df[df['AwayTeam'] == team_name_for_data].copy()
        goals_scored = 'FTAG'
        goals_conceded = 'FTHG'
    
    if team_games.empty:
        return None
    
    try:
        team_games[goals_scored] = pd.to_numeric(team_games[goals_scored], errors='coerce').fillna(0)
        team_games[goals_conceded] = pd.to_numeric(team_games[goals_conceded], errors='coerce').fillna(0)
    except Exception as e:
        st.error(f"שגיאה בהמרת נתונים: {e}")
        return None
    
    stats = {
        'games_played': len(team_games),
        'avg_goals_scored': float(team_games[goals_scored].mean()),
        'avg_goals_conceded': float(team_games[goals_conceded].mean()),
        'wins': 0,
        'draws': 0,
        'losses': 0
    }
    
    for _, game in team_games.iterrows():
        try:
            home_goals = float(game['FTHG'])
            away_goals = float(game['FTAG'])
            
            if is_home:
                if home_goals > away_goals:
                    stats['wins'] += 1
                elif home_goals == away_goals:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
            else:
                if away_goals > home_goals:
                    stats['wins'] += 1
                elif away_goals == home_goals:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
        except (ValueError, TypeError) as e:
            st.warning(f"בעיה בעיבוד משחק: {e}")
            continue
    
    stats['win_rate'] = stats['wins'] / stats['games_played'] if stats['games_played'] > 0 else 0
    
    return stats

def predict_match_advanced(home_team, away_team, df, league_name=None):
    """חיזוי מתקדם משולב עם נתונים היסטוריים"""
    
    european_leagues = ['Champions League', 'Europa League', 'Conference League']
    
    if league_name in european_leagues:
        result = predict_european_match(home_team, away_team, league_name)
        
        st.success(f"⭐ **דירוג {home_team}**: {result['home_rating']}/100")
        st.success(f"⭐ **דירוג {away_team}**: {result['away_rating']}/100")
        
        rating_diff = result['home_rating'] - result['away_rating']
        if rating_diff > 15:
            st.info(f"🔥 {home_team} נחשבת מועמדת לניצחון (הפרש דירוג: +{rating_diff})")
        elif rating_diff < -15:
            st.info(f"🔥 {away_team} נחשבת מועמדת לניצחון (הפרש דירוג: +{abs(rating_diff)})")
        else:
            st.info("⚖️ משחק מאוזן - שתי קבוצות ברמה דומה")
        
        return result
    
    # טען את כל הנתונים לחישוב דירוגים מתקדמים
    all_data = load_league_data()
    
    home_rating = get_team_rating(home_team, league_name, all_data)
    away_rating = get_team_rating(away_team, league_name, all_data)
    
    home_stats = analyze_team_performance(home_team, df, is_home=True, league_name=league_name)
    away_stats = analyze_team_performance(away_team, df, is_home=False, league_name=league_name)
    
    rating_diff = home_rating - away_rating
    base_home_advantage = 0.15
    
    if home_stats and away_stats and home_stats['games_played'] >= 5 and away_stats['games_played'] >= 5:
        historical_weight = 0.4
        rating_weight = 0.6
        
        hist_home_goals = home_stats['avg_goals_scored'] * 1.1
        hist_away_goals = away_stats['avg_goals_scored'] * 0.9
        
        rating_home_goals = 1.5 + (home_rating - 65) * 0.02
        rating_away_goals = 1.2 + (away_rating - 65) * 0.02
        
        expected_home_goals = (hist_home_goals * historical_weight + 
                             rating_home_goals * rating_weight)
        expected_away_goals = (hist_away_goals * historical_weight + 
                             rating_away_goals * rating_weight)
        
        hist_home_win_rate = home_stats['win_rate']
        hist_away_win_rate = away_stats['win_rate']
        
        prob_adjustment = (hist_home_win_rate - hist_away_win_rate) * 0.3
        
    else:
        expected_home_goals = 1.5 + (home_rating - 65) * 0.02 + base_home_advantage
        expected_away_goals = 1.2 + (away_rating - 65) * 0.02
        prob_adjustment = rating_diff * 0.01
    
    expected_home_goals = max(0.3, min(4.0, expected_home_goals))
    expected_away_goals = max(0.3, min(4.0, expected_away_goals))
    
    max_goals = 6
    home_win = draw = away_win = 0.0
    
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = poisson.pmf(i, expected_home_goals) * poisson.pmf(j, expected_away_goals)
            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p
    
    home_win += prob_adjustment
    away_win -= prob_adjustment
    
    total_prob = home_win + draw + away_win
    if total_prob > 0:
        home_win /= total_prob
        draw /= total_prob
        away_win /= total_prob
    
    total_corners = 10.0 + (home_rating + away_rating - 130) * 0.05
    
    return {
        "home_win": round(max(0.05, min(0.85, home_win)), 3),
        "draw": round(max(0.05, min(0.50, draw)), 3),
        "away_win": round(max(0.05, min(0.85, away_win)), 3),
        "total_goals": round(expected_home_goals + expected_away_goals, 1),
        "total_corners": round(total_corners, 1),
        "home_rating": home_rating,
        "away_rating": away_rating,
        "has_historical_data": home_stats is not None and away_stats is not None,
        "home_stats": home_stats,
        "away_stats": away_stats
    }

def display_data_quality(df, league_name):
    """הצגת איכות הנתונים"""
    if df is None or df.empty:
        st.error(f"❌ אין נתונים זמינים עבור {league_name}")
        return False
    
    st.success(f"✅ נטענו {len(df)} משחקים מהליגה")
    
    required_cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.warning(f"⚠️ עמודות חסרות: {missing_cols}")
        st.info("החיזוי יתבסס על דירוגי קבוצות בלבד")
        return False
    
    try:
        df = clean_numeric_columns(df)
        
        valid_games = df[(df['FTHG'].notna()) & (df['FTAG'].notna()) & 
                        (df['FTHG'] >= 0) & (df['FTAG'] >= 0)]
        
        if len(valid_games) < len(df) * 0.8:
            st.warning(f"⚠️ רק {len(valid_games)} מתוך {len(df)} משחקים עם נתונים תקינים")
        
        teams_in_data = set(df['HomeTeam'].unique()) | set(df['AwayTeam'].unique())
        st.info(f"📊 הנתונים כוללים {len(teams_in_data)} קבוצות")
        
        european_leagues = ['Champions League', 'Europa League', 'Conference League']
        if league_name not in european_leagues:
            sample_teams = list(teams_in_data)[:5]
            st.info(f"🔍 דוגמאות לשמות קבוצות בנתונים: {', '.join(sample_teams)}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ שגיאה בעיבוד הנתונים: {e}")
        return False

# ----------------------------
# ממשק משתמש משופר
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
st.markdown("### 🏟️ בחר תחרות ומשחק - עונת 2025/26")

selected_category = st.selectbox("בחר קטגוריה", options=list(league_categories.keys()))
available_leagues = league_categories[selected_category]
selected_league = st.selectbox("בחר ליגה/תחרות", options=available_leagues)

# הצגת איכות הנתונים
if selected_league in data:
    data_quality = display_data_quality(data[selected_league], selected_league)
else:
    st.warning(f"⚠️ לא נמצאו נתונים היסטוריים עבור {selected_league}")
    st.info("החיזוי יתבסס על דירוגי קבוצות ונתונים היסטוריים חכמים")

if selected_league in LEAGUE_TEAMS:
    teams = LEAGUE_TEAMS[selected_league]
    
    # הצגת מידע על קבוצות חדשות
    if selected_league == 'Premier League':
        st.success("🆕 **קבוצות חדשות**: Leeds United, Burnley, Sunderland")
        st.warning("⬇️ **קבוצות שירדו**: Sheffield United, Luton Town, Nottingham Forest")
    elif selected_league == 'La Liga':
        st.success("🆕 **קבוצות חדשות**: Levante, Elche, Real Oviedo")
        st.warning("⬇️ **קבוצות שירדו**: Granada, Almeria, Cadiz")
    elif selected_league == 'Serie A':
        st.success("🆕 **קבוצות חדשות**: Parma, Como, Venezia")
        st.warning("⬇️ **קבוצות שירדו**: Frosinone, Salernitana, Sassuolo")
    elif selected_league == 'Bundesliga':
        st.success("🆕 **קבוצות חדשות**: FC Koln, Hamburger SV, St Pauli")
        st.warning("⬇️ **קבוצות שירדו**: Darmstadt, Koln, Union Berlin")
    elif selected_league == 'Ligue 1':
        st.success("🆕 **קבוצות חדשות**: FC Lorient, Paris FC, FC Metz")
        st.warning("⬇️ **קבוצות שירדו**: Clermont Foot, Toulouse FC, Le Havre")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 קבוצה ביתית", options=teams)
    
    with col2:
        away_team = st.selectbox("✈️ קבוצה אורחת", options=[t for t in teams if t != home_team])
    
    if st.button("🔮 חשב חיזוי", type="primary"):
        
        df = data.get(selected_league, pd.DataFrame())
        prediction = predict_match_advanced(home_team, away_team, df, selected_league)
        
        st.markdown("---")
        st.subheader("🎯 תוצאות החיזוי")
        
        # הצגת דירוגים
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"⭐ **דירוג {home_team}**: {prediction['home_rating']}/100")
        with col2:
            st.success(f"⭐ **דירוג {away_team}**: {prediction['away_rating']}/100")
        
        # הצגת הסתברויות
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
        
        # הצגת נתונים היסטוריים אם זמינים
        european_leagues = ['Champions League', 'Europa League', 'Conference League']
        if selected_league not in european_leagues and prediction.get('has_historical_data'):
            st.markdown("---")
            st.subheader("📈 נתונים היסטוריים")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{home_team} (בית):**")
                home_stats = prediction['home_stats']
                if home_stats:
                    st.write(f"• משחקים: {home_stats['games_played']}")
                    st.write(f"• ניצחונות: {home_stats['win_rate']:.1%}")
                    st.write(f"• ממוצע שערים: {home_stats['avg_goals_scored']:.1f}")
                    st.write(f"• ממוצע נגד: {home_stats['avg_goals_conceded']:.1f}")
            
            with col2:
                st.markdown(f"**{away_team} (חוץ):**")
                away_stats = prediction['away_stats']
                if away_stats:
                    st.write(f"• משחקים: {away_stats['games_played']}")
                    st.write(f"• ניצחונות: {away_stats['win_rate']:.1%}")
                    st.write(f"• ממוצע שערים: {away_stats['avg_goals_scored']:.1f}")
                    st.write(f"• ממוצע נגד: {away_stats['avg_goals_conceded']:.1f}")
        
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
        
        # אמינות החיזוי
        rating_diff = abs(prediction['home_rating'] - prediction['away_rating'])
        if selected_league in european_leagues:
            if rating_diff > 15:
                st.info("🔥 **אמינות גבוהה** - הפרש דירוגים משמעותי")
            else:
                st.info("📊 **אמינות טובה** - מבוסס על דירוגי קבוצות מתקדמים")
        else:
            if rating_diff > 15:
                st.info("🔥 **אמינות גבוהה** - הפרש דירוגים משמעותי")
            elif prediction.get('has_historical_data'):
                st.info("📊 **אמינות טובה** - מבוסס על נתונים היסטוריים ודירוגים חכמים")
            else:
                st.info("⚠️ **אמינות בינונית** - מבוסס על דירוגי קבוצות ונתונים היסטוריים")
        
        # מידע על קבוצות חדשות
        new_teams_all = ['Leeds United', 'Levante', 'Elche', 'Real Oviedo', 'Parma', 'Como', 'Venezia', 
                        'FC Koln', 'Hamburger SV', 'St Pauli', 'FC Lorient', 'Paris FC', 'FC Metz']
        
        if home_team in new_teams_all or away_team in new_teams_all:
            st.info("🆕 **קבוצה חדשה במשחק** - החיזוי מבוסס על נתונים היסטוריים חכמים וביצועים בליגה הנמוכה")

# מידע נוסף
with st.expander("ℹ️ אודות השיטה והחדשות"):
    st.markdown("""
    ### 🔧 שיטת החיזוי המתקדמת החדשה:
    
    **🎯 חיזוי משולב מתוקן עם נתונים היסטוריים:**
    - 📊 שילוב נתונים היסטוריים עם דירוגי קבוצות מחושבים
    - ⚖️ משקל של 40% לנתונים היסטוריים, 60% לדירוגים
    - 🧠 **חדש**: דירוגים מחושבים לקבוצות עולות על בסיס ביצועים בליגה הקודמת
    - 🎯 חיזוי מדויק יותר כשיש מספיק נתונים
    
    **📈 ניתוח מתקדם לקבוצות חדשות:**
    - 📊 ניתוח ביצועי קבוצות בכל הליגות ההיסטוריות
    - 🏆 חישוב בונוס ביצועים על בסיס אחוז ניצחונות ויחס שערים
    - ⚽ התחשבות בהתקפיות וביצועים הגנתיים
    - 🔄 עדכון דירוגים בזמן אמת עבור קבוצות ללא דירוג קבוע
    
    **🔍 מקורות הנתונים המתוקנים:**
    - **ליגות מקומיות**: נתונים היסטוריים מ-3+ עונות כולל עונות 22/23, 23/24, 24/25
    - **ליגות אירופיות**: דירוגי קבוצות מבוססי ביצועים
    - **קבוצות עולות**: חישוב דירוג מבוסס ביצועים היסטוריים בכל הליגות
    - **עדכון אוטומטי**: הנתונים נטענים מהמאגר ב-GitHub עם טיפול בשגיאות
    
    **🆕 עדכונים לעונת 2025/26:**
    - **Premier League**: Leeds United, Burnley, Sunderland עלו
    - **La Liga**: Levante, Elche, Real Oviedo עלו | Granada, Almeria, Cadiz ירדו
    - **Serie A**: Parma, Como, Venezia עלו | Frosinone, Salernitana, Sassuolo ירדו
    - **Bundesliga**: FC Koln, Hamburger SV, St Pauli עלו | Darmstadt, Koln, Union Berlin ירדו
    - **Ligue 1**: FC Lorient, Paris FC, FC Metz עלו | Clermont Foot, Toulouse FC, Le Havre ירדו
    
    **📋 רמות אמינות משופרות:**
    - 🔥 **גבוהה**: הפרש דירוגים >15 + נתונים היסטוריים עשירים
    - 📊 **טובה**: נתונים היסטוריים מ-5+ משחקים או דירוג מחושב חכם
    - ⚠️ **בינונית**: מבוסס על דירוגי קבוצות ונתונים חלקיים
    
    **🎲 מודל החיזוי המשופר:**
    - מודל פואסון מתקדם לחישוב הסתברויות
    - יתרון בית משתנה לפי סוג הליגה ורמת הקבוצות
    - התחשבות ביכולת התקפית והגנתית מנתונים אמיתיים
    - **חדש**: חישוב דירוגים דינמי לקבוצות ללא דירוג קבוע
    - נורמליזציה של הסתברויות לתוצאות הגיוניות
    
    **🧮 חישוב דירוג לקבוצות עולות:**
    - דירוג בסיס לפי רמת הליגה (60-63 נקודות)
    - בונוס עד 18 נקודות על בסיס ביצועים היסטוריים:
      • אחוז ניצחונות (עד 12 נקודות)
      • יחס שערים (עד 10 נקודות) 
      • התקפיות (עד 4 נקודות)
    - דירוג מקסימלי 78 נקודות לקבוצה עולה
    - הצגת פירוט החישוב בזמן אמת
    
    **🔧 תיקונים טכניים:**
    - תיקון URLs לא פעילים והחלפתם במקורות נתונים אמינים
    - שיפור הטיפול בשגיאות טעינת נתונים
    - מערכת fallback חכמה כשנתונים חסרים
    - אופטימיזציה של ביצועי האפליקציה
    """)

# הצגת טבלת דירוגים
with st.expander("📊 טבלת דירוגים - עונת 2025/26"):
    selected_league_for_ratings = st.selectbox(
        "בחר ליגה לצפייה בדירוגים:",
        options=['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
    )
    
    if selected_league_for_ratings in LEAGUE_TEAMS:
        teams_ratings = []
        all_data_for_ratings = load_league_data()
        
        for team in LEAGUE_TEAMS[selected_league_for_ratings]:
            rating = get_team_rating(team, selected_league_for_ratings, all_data_for_ratings)
            teams_ratings.append((team, rating))
        
        teams_ratings.sort(key=lambda x: x[1], reverse=True)
        
        st.markdown(f"### 🏆 {selected_league_for_ratings} - דירוגים")
        
        for i, (team, rating) in enumerate(teams_ratings, 1):
            # סמן קבוצות חדשות
            new_teams_by_league = {
                'Premier League': ['Leeds United', 'Burnley', 'Sunderland'],
                'La Liga': ['Levante', 'Elche', 'Real Oviedo'],
                'Serie A': ['Parma', 'Como', 'Venezia'],
                'Bundesliga': ['FC Koln', 'Hamburger SV', 'St Pauli'],
                'Ligue 1': ['FC Lorient', 'Paris FC', 'FC Metz']
            }
            
            is_new_team = team in new_teams_by_league.get(selected_league_for_ratings, [])
            new_indicator = " 🆕" if is_new_team else ""
            
            if i <= 4:
                st.success(f"{i}. **{team}** - {rating}/100{new_indicator}")
            elif i <= 10:
                st.info(f"{i}. **{team}** - {rating}/100{new_indicator}")
            else:
                st.write(f"{i}. **{team}** - {rating}/100{new_indicator}")

# הצגת נתונים על קבוצות חדשות
with st.expander("🆕 מידע על קבוצות חדשות ודירוגים מחושבים"):
    st.markdown("""
    ### 📈 קבוצות עולות ודירוגים חכמים
    
    **🔄 איך מחושב הדירוג לקבוצות חדשות:**
    
    1. **דירוג בסיס לפי ליגה**:
       - Premier League: 62 נקודות
       - Bundesliga: 63 נקודות  
       - Serie A: 61 נקודות
       - La Liga: 60 נקודות
       - Ligue 1: 59 נקודות
    
    2. **ניתוח ביצועים היסטוריים** (מינימום 15 משחקים):
       - סריקת כל הנתונים ההיסטוריים מכל הליגות
       - חישוב אחוז ניצחונות, יחס שערים, התקפיות
    
    3. **חישוב בונוס ביצועים**:
       - **אחוז ניצחונות גבוה**: עד 12 נקודות
       - **יחס שערים חיובי**: עד 10 נקודות
       - **התקפיות גבוהה**: עד 4 נקודות
    
    4. **דירוג סופי**: בסיס + בונוס (מקסימום 78)
    
    **📊 דוגמאות להשפעה**:
    - קבוצה עם 65% ניצחונות ויחס שערים +1.2: בונוס ~15 נקודות
    - קבוצה עם 45% ניצחונות ויחס שערים +0.3: בונוס ~6 נקודות  
    - קבוצה עם 35% ניצחונות ויחס שערים שלילי: בונוס ~2 נקודות
    
    **🎯 יתרונות השיטה**:
    - דירוג מדויק יותר מאשר הערכה סטטית
    - התחשבות בכוח אמיתי של הקבוצה
    - עדכון אוטומטי בהתבסס על נתונים אמיתיים
    - שקיפות מלאה בחישוב הדירוג
    
    **🔧 תיקונים טכניים**:
    - תיקון URLs שלא עבדו במערכת הקודמת
    - שיפור הטיפול בשגיאות טעינת נתונים
    - אופטימיזציה של ביצועי האפליקציה
    - מערכת fallback משופרת לנתונים חסרים
    """)

st.markdown("---")
st.markdown("*⚽ Football Predictor Pro - עונת 2025/26 | גרסה מתוקנת עם נתונים היסטוריים חכמים + דירוגי קבוצות דינמיים*")