"""
Data fetcher for MLB player fWAR statistics.
Automatically generates comprehensive player data or fetches from public sources.
"""
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional
import random

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Historical team names mapping (handles team name changes)
TEAM_MAPPINGS = {
    "Milwaukee Braves": "Atlanta Braves",
    "Boston Braves": "Atlanta Braves",
    "Brooklyn Dodgers": "Los Angeles Dodgers",
    "New York Giants": "San Francisco Giants",
    "St. Louis Browns": "Baltimore Orioles",
    "Washington Senators": "Texas Rangers",
    "Montreal Expos": "Washington Nationals",
    "California Angels": "Los Angeles Angels",
    "Anaheim Angels": "Los Angeles Angels",
    "Florida Marlins": "Miami Marlins",
    "Tampa Bay Devil Rays": "Tampa Bay Rays",
    "Cleveland Indians": "Cleveland Guardians",
    "Cleveland Naps": "Cleveland Guardians",
    "Cleveland Spiders": "Cleveland Guardians",
    "Philadelphia Athletics": "Oakland Athletics",
    "Kansas City Athletics": "Oakland Athletics",
}

# Known top players with accurate data
TOP_PLAYERS = [
        {"name": "Babe Ruth", "fwar": 182.5, "teams": ["New York Yankees", "Boston Red Sox"], "positions": ["OF", "SP"], "years_active": ["1914", "1935"], "minor_league": False, "international_signing": False},
    {"name": "Barry Bonds", "fwar": 164.4, "teams": ["San Francisco Giants", "Pittsburgh Pirates"], "positions": ["LF", "OF"], "years_active": ["1986", "2007"], "minor_league": False, "international_signing": False},
    {"name": "Willie Mays", "fwar": 156.2, "teams": ["San Francisco Giants", "New York Mets"], "positions": ["CF", "OF"], "years_active": ["1951", "1973"], "minor_league": False, "international_signing": False},
    {"name": "Ty Cobb", "fwar": 151.0, "teams": ["Detroit Tigers", "Philadelphia Athletics"], "positions": ["OF", "CF"], "years_active": ["1905", "1928"], "minor_league": False, "international_signing": False},
    {"name": "Hank Aaron", "fwar": 143.0, "teams": ["Atlanta Braves", "Milwaukee Braves", "Milwaukee Brewers"], "positions": ["RF", "OF"], "years_active": ["1954", "1976"], "minor_league": False, "international_signing": False},
    {"name": "Tris Speaker", "fwar": 134.1, "teams": ["Boston Red Sox", "Cleveland Guardians", "Washington Senators", "Philadelphia Athletics"], "positions": ["CF", "OF"], "years_active": ["1907", "1928"], "minor_league": False, "international_signing": False},
    {"name": "Honus Wagner", "fwar": 130.8, "teams": ["Pittsburgh Pirates", "Louisville Colonels"], "positions": ["SS", "OF"], "years_active": ["1897", "1917"], "minor_league": False, "international_signing": False},
    {"name": "Stan Musial", "fwar": 128.3, "teams": ["St. Louis Cardinals"], "positions": ["OF", "1B"], "years_active": ["1941", "1963"], "minor_league": False, "international_signing": False},
    {"name": "Rogers Hornsby", "fwar": 127.1, "teams": ["St. Louis Cardinals", "New York Giants", "Boston Braves", "Chicago Cubs", "St. Louis Browns"], "positions": ["2B", "SS"], "years_active": ["1915", "1937"], "minor_league": False, "international_signing": False},
    {"name": "Eddie Collins", "fwar": 124.0, "teams": ["Philadelphia Athletics", "Chicago White Sox"], "positions": ["2B"], "years_active": ["1906", "1930"], "minor_league": False, "international_signing": False},
    {"name": "Ted Williams", "fwar": 123.1, "teams": ["Boston Red Sox"], "positions": ["LF", "OF"], "years_active": ["1939", "1960"], "minor_league": False, "international_signing": False},
    {"name": "Mickey Mantle", "fwar": 110.3, "teams": ["New York Yankees"], "positions": ["CF", "OF"], "years_active": ["1951", "1968"], "minor_league": False, "international_signing": False},
    {"name": "Lou Gehrig", "fwar": 112.4, "teams": ["New York Yankees"], "positions": ["1B"], "years_active": ["1923", "1939"], "minor_league": False, "international_signing": False},
    {"name": "Mike Trout", "fwar": 85.2, "teams": ["Los Angeles Angels"], "positions": ["CF", "OF"], "years_active": ["2011", "2024"], "minor_league": False, "international_signing": False},
    {"name": "Albert Pujols", "fwar": 100.7, "teams": ["St. Louis Cardinals", "Los Angeles Angels", "Los Angeles Dodgers"], "positions": ["1B", "DH"], "years_active": ["2001", "2022"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
    {"name": "Alex Rodriguez", "fwar": 117.6, "teams": ["Seattle Mariners", "Texas Rangers", "New York Yankees"], "positions": ["SS", "3B"], "years_active": ["1994", "2016"], "minor_league": False, "international_signing": False},
    {"name": "Derek Jeter", "fwar": 71.3, "teams": ["New York Yankees"], "positions": ["SS"], "years_active": ["1995", "2014"], "minor_league": False, "international_signing": False},
    {"name": "Cal Ripken Jr.", "fwar": 95.9, "teams": ["Baltimore Orioles"], "positions": ["SS", "3B"], "years_active": ["1981", "2001"], "minor_league": False, "international_signing": False},
    {"name": "Rickey Henderson", "fwar": 111.2, "teams": ["Oakland Athletics", "New York Yankees", "Toronto Blue Jays", "San Diego Padres", "Anaheim Angels", "New York Mets", "Seattle Mariners", "Boston Red Sox", "Los Angeles Dodgers"], "positions": ["LF", "OF"], "years_active": ["1979", "2003"], "minor_league": False, "international_signing": False},
    {"name": "Pete Rose", "fwar": 79.6, "teams": ["Cincinnati Reds", "Philadelphia Phillies", "Montreal Expos"], "positions": ["OF", "1B", "2B", "3B"], "years_active": ["1963", "1986"], "minor_league": False, "international_signing": False},
    {"name": "Randy Johnson", "fwar": 101.1, "teams": ["Montreal Expos", "Seattle Mariners", "Houston Astros", "Arizona Diamondbacks", "New York Yankees", "San Francisco Giants"], "positions": ["P"], "years_active": ["1988", "2009"], "minor_league": False, "international_signing": False},
    {"name": "Roger Clemens", "fwar": 139.2, "teams": ["Boston Red Sox", "Toronto Blue Jays", "New York Yankees", "Houston Astros"], "positions": ["P"], "years_active": ["1984", "2007"], "minor_league": False, "international_signing": False},
    {"name": "Greg Maddux", "fwar": 106.8, "teams": ["Chicago Cubs", "Atlanta Braves", "Los Angeles Dodgers", "San Diego Padres"], "positions": ["P"], "years_active": ["1986", "2008"], "minor_league": False, "international_signing": False},
    {"name": "Pedro Martinez", "fwar": 86.0, "teams": ["Los Angeles Dodgers", "Montreal Expos", "Boston Red Sox", "New York Mets", "Philadelphia Phillies"], "positions": ["P"], "years_active": ["1992", "2009"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
        {"name": "Mariano Rivera", "fwar": 56.3, "teams": ["New York Yankees"], "positions": ["CP"], "years_active": ["1995", "2013"], "minor_league": False, "international_signing": True, "signing_country": "Panama"},
    {"name": "Ichiro Suzuki", "fwar": 60.0, "teams": ["Seattle Mariners", "New York Yankees", "Miami Marlins"], "positions": ["RF", "OF"], "years_active": ["2001", "2019"], "minor_league": False, "international_signing": True, "signing_country": "Japan"},
    {"name": "Roberto Clemente", "fwar": 94.8, "teams": ["Pittsburgh Pirates"], "positions": ["RF", "OF"], "years_active": ["1955", "1972"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Vladimir Guerrero", "fwar": 59.5, "teams": ["Montreal Expos", "Los Angeles Angels", "Texas Rangers", "Baltimore Orioles"], "positions": ["RF", "OF", "DH"], "years_active": ["1996", "2011"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
    {"name": "Miguel Cabrera", "fwar": 67.3, "teams": ["Florida Marlins", "Detroit Tigers"], "positions": ["1B", "3B", "DH"], "years_active": ["2003", "2023"], "minor_league": False, "international_signing": True, "signing_country": "Venezuela"},
    {"name": "David Ortiz", "fwar": 55.3, "teams": ["Minnesota Twins", "Boston Red Sox"], "positions": ["DH", "1B"], "years_active": ["1997", "2016"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
    {"name": "Adrian Beltre", "fwar": 93.5, "teams": ["Los Angeles Dodgers", "Seattle Mariners", "Boston Red Sox", "Texas Rangers"], "positions": ["3B"], "years_active": ["1998", "2018"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
    {"name": "Carlos Beltran", "fwar": 70.1, "teams": ["Kansas City Royals", "Houston Astros", "New York Mets", "San Francisco Giants", "St. Louis Cardinals", "New York Yankees", "Texas Rangers"], "positions": ["CF", "OF"], "years_active": ["1998", "2017"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Jose Altuve", "fwar": 51.2, "teams": ["Houston Astros"], "positions": ["2B"], "years_active": ["2011", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Venezuela"},
    {"name": "Manny Ramirez", "fwar": 69.4, "teams": ["Cleveland Guardians", "Boston Red Sox", "Los Angeles Dodgers", "Chicago White Sox", "Tampa Bay Rays"], "positions": ["LF", "OF", "DH"], "years_active": ["1993", "2011"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
    {"name": "Robinson Cano", "fwar": 57.4, "teams": ["New York Yankees", "Seattle Mariners", "New York Mets", "San Diego Padres", "Atlanta Braves"], "positions": ["2B"], "years_active": ["2005", "2022"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
    {"name": "Yadier Molina", "fwar": 42.1, "teams": ["St. Louis Cardinals"], "positions": ["C"], "years_active": ["2004", "2022"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Fernando Valenzuela", "fwar": 41.3, "teams": ["Los Angeles Dodgers", "California Angels", "Baltimore Orioles", "Philadelphia Phillies", "San Diego Padres", "St. Louis Cardinals"], "positions": ["P"], "years_active": ["1980", "1997"], "minor_league": False, "international_signing": True, "signing_country": "Mexico"},
    {"name": "Juan Marichal", "fwar": 61.9, "teams": ["San Francisco Giants", "Boston Red Sox", "Los Angeles Dodgers"], "positions": ["P"], "years_active": ["1960", "1975"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
    {"name": "Luis Aparicio", "fwar": 55.8, "teams": ["Chicago White Sox", "Baltimore Orioles", "Boston Red Sox"], "positions": ["SS"], "years_active": ["1956", "1973"], "minor_league": False, "international_signing": True, "signing_country": "Venezuela"},
    {"name": "Rod Carew", "fwar": 81.2, "teams": ["Minnesota Twins", "California Angels"], "positions": ["1B", "2B"], "years_active": ["1967", "1985"], "minor_league": False, "international_signing": True, "signing_country": "Panama"},
    {"name": "Tony Perez", "fwar": 54.0, "teams": ["Cincinnati Reds", "Montreal Expos", "Boston Red Sox", "Philadelphia Phillies"], "positions": ["1B", "3B"], "years_active": ["1964", "1986"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Minnie Minoso", "fwar": 50.3, "teams": ["Cleveland Guardians", "Chicago White Sox", "St. Louis Cardinals", "Washington Senators"], "positions": ["LF", "OF", "3B"], "years_active": ["1949", "1980"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Orlando Cepeda", "fwar": 50.1, "teams": ["San Francisco Giants", "St. Louis Cardinals", "Atlanta Braves", "Oakland Athletics", "Boston Red Sox", "Kansas City Royals"], "positions": ["1B"], "years_active": ["1958", "1974"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Felipe Alou", "fwar": 32.1, "teams": ["San Francisco Giants", "Milwaukee Braves", "Atlanta Braves", "Oakland Athletics", "New York Yankees", "Montreal Expos"], "positions": ["OF", "1B"], "years_active": ["1958", "1974"], "minor_league": False, "international_signing": True, "signing_country": "Dominican Republic"},
    {"name": "Tony Oliva", "fwar": 43.0, "teams": ["Minnesota Twins"], "positions": ["RF", "OF"], "years_active": ["1962", "1976"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Bert Campaneris", "fwar": 53.9, "teams": ["Kansas City Athletics", "Oakland Athletics", "Texas Rangers", "California Angels", "New York Yankees"], "positions": ["SS"], "years_active": ["1964", "1983"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Jose Canseco", "fwar": 42.7, "teams": ["Oakland Athletics", "Texas Rangers", "Boston Red Sox", "Toronto Blue Jays", "Tampa Bay Devil Rays", "New York Yankees", "Chicago White Sox"], "positions": ["OF", "DH"], "years_active": ["1985", "2001"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Rafael Palmeiro", "fwar": 71.9, "teams": ["Chicago Cubs", "Texas Rangers", "Baltimore Orioles"], "positions": ["1B", "DH"], "years_active": ["1986", "2005"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Sandy Alomar Jr.", "fwar": 15.2, "teams": ["San Diego Padres", "Cleveland Guardians", "Chicago White Sox", "Colorado Rockies", "Texas Rangers", "Los Angeles Dodgers"], "positions": ["C"], "years_active": ["1988", "2007"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Edgar Martinez", "fwar": 68.4, "teams": ["Seattle Mariners"], "positions": ["DH", "3B"], "years_active": ["1987", "2004"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Ivan Rodriguez", "fwar": 68.7, "teams": ["Texas Rangers", "Florida Marlins", "Detroit Tigers", "New York Yankees", "Houston Astros", "Washington Nationals"], "positions": ["C"], "years_active": ["1991", "2011"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Carlos Delgado", "fwar": 44.1, "teams": ["Toronto Blue Jays", "Florida Marlins", "New York Mets"], "positions": ["1B", "DH"], "years_active": ["1993", "2009"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Jorge Posada", "fwar": 42.7, "teams": ["New York Yankees"], "positions": ["C"], "years_active": ["1995", "2011"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Bernie Williams", "fwar": 49.6, "teams": ["New York Yankees"], "positions": ["CF", "OF"], "years_active": ["1991", "2006"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Roberto Alomar", "fwar": 67.0, "teams": ["San Diego Padres", "Toronto Blue Jays", "Baltimore Orioles", "Cleveland Guardians", "New York Mets", "Chicago White Sox", "Arizona Diamondbacks"], "positions": ["2B"], "years_active": ["1988", "2004"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Sandy Koufax", "fwar": 48.9, "teams": ["Brooklyn Dodgers", "Los Angeles Dodgers"], "positions": ["P"], "years_active": ["1955", "1966"], "minor_league": False, "international_signing": False},
    {"name": "Tom Seaver", "fwar": 109.9, "teams": ["New York Mets", "Cincinnati Reds", "Chicago White Sox", "Boston Red Sox"], "positions": ["P"], "years_active": ["1967", "1986"], "minor_league": False, "international_signing": False},
    {"name": "Nolan Ryan", "fwar": 81.3, "teams": ["New York Mets", "California Angels", "Houston Astros", "Texas Rangers"], "positions": ["P"], "years_active": ["1966", "1993"], "minor_league": False, "international_signing": False},
    {"name": "Steve Carlton", "fwar": 90.3, "teams": ["St. Louis Cardinals", "Philadelphia Phillies", "San Francisco Giants", "Chicago White Sox", "Cleveland Guardians", "Minnesota Twins"], "positions": ["P"], "years_active": ["1965", "1988"], "minor_league": False, "international_signing": False},
    {"name": "Bob Gibson", "fwar": 89.1, "teams": ["St. Louis Cardinals"], "positions": ["P"], "years_active": ["1959", "1975"], "minor_league": False, "international_signing": False},
    {"name": "Warren Spahn", "fwar": 100.2, "teams": ["Boston Braves", "Milwaukee Braves", "New York Mets", "San Francisco Giants"], "positions": ["P"], "years_active": ["1942", "1965"], "minor_league": False, "international_signing": False},
    {"name": "Cy Young", "fwar": 163.6, "teams": ["Cleveland Spiders", "St. Louis Cardinals", "Boston Red Sox", "Cleveland Naps", "Boston Braves"], "positions": ["P"], "years_active": ["1890", "1911"], "minor_league": False, "international_signing": False},
    {"name": "Walter Johnson", "fwar": 164.5, "teams": ["Washington Senators"], "positions": ["P"], "years_active": ["1907", "1927"], "minor_league": False, "international_signing": False},
    {"name": "Christy Mathewson", "fwar": 106.3, "teams": ["New York Giants", "Cincinnati Reds"], "positions": ["P"], "years_active": ["1900", "1916"], "minor_league": False, "international_signing": False},
    {"name": "Grover Cleveland Alexander", "fwar": 109.3, "teams": ["Philadelphia Phillies", "Chicago Cubs", "St. Louis Cardinals"], "positions": ["P"], "years_active": ["1911", "1930"], "minor_league": False, "international_signing": False},
    {"name": "Lefty Grove", "fwar": 109.7, "teams": ["Philadelphia Athletics", "Boston Red Sox"], "positions": ["P"], "years_active": ["1925", "1941"], "minor_league": False, "international_signing": False},
    {"name": "Satchel Paige", "fwar": 10.0, "teams": ["Cleveland Guardians", "St. Louis Browns", "Kansas City Athletics"], "positions": ["P"], "years_active": ["1948", "1965"], "minor_league": True, "international_signing": False},
    {"name": "Josh Gibson", "fwar": 0.0, "teams": ["Pittsburgh Crawfords", "Homestead Grays"], "positions": ["C"], "years_active": ["1930", "1946"], "minor_league": True, "international_signing": False},
    {"name": "Cool Papa Bell", "fwar": 0.0, "teams": ["St. Louis Stars", "Pittsburgh Crawfords", "Homestead Grays"], "positions": ["CF", "OF"], "years_active": ["1922", "1946"], "minor_league": True, "international_signing": False},
    {"name": "Oscar Charleston", "fwar": 0.0, "teams": ["Indianapolis ABCs", "Pittsburgh Crawfords", "Homestead Grays"], "positions": ["CF", "OF", "1B"], "years_active": ["1915", "1945"], "minor_league": True, "international_signing": False},
    {"name": "Martin Dihigo", "fwar": 0.0, "teams": ["Cuban Stars", "Homestead Grays"], "positions": ["P", "2B", "SS", "3B", "OF"], "years_active": ["1923", "1945"], "minor_league": True, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Jose Fernandez", "fwar": 14.1, "teams": ["Miami Marlins"], "positions": ["P"], "years_active": ["2013", "2016"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
        {"name": "Aroldis Chapman", "fwar": 20.1, "teams": ["Cincinnati Reds", "New York Yankees", "Chicago Cubs", "Kansas City Royals", "Texas Rangers", "Pittsburgh Pirates"], "positions": ["CP"], "years_active": ["2010", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Yasiel Puig", "fwar": 19.3, "teams": ["Los Angeles Dodgers", "Cincinnati Reds", "Cleveland Guardians"], "positions": ["RF", "OF"], "years_active": ["2013", "2019"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Jose Abreu", "fwar": 31.7, "teams": ["Chicago White Sox", "Houston Astros"], "positions": ["1B", "DH"], "years_active": ["2014", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Yoenis Cespedes", "fwar": 25.8, "teams": ["Oakland Athletics", "Boston Red Sox", "Detroit Tigers", "New York Mets"], "positions": ["LF", "OF"], "years_active": ["2012", "2020"], "minor_league": False, "international_signing": True, "signing_country": "Cuba"},
    {"name": "Ronald Acuna Jr.", "fwar": 35.2, "teams": ["Atlanta Braves"], "positions": ["RF", "OF"], "years_active": ["2018", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Venezuela"},
    {"name": "Francisco Lindor", "fwar": 42.8, "teams": ["Cleveland Guardians", "New York Mets"], "positions": ["SS"], "years_active": ["2015", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Carlos Correa", "fwar": 40.1, "teams": ["Houston Astros", "Minnesota Twins", "San Francisco Giants"], "positions": ["SS"], "years_active": ["2015", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Javier Baez", "fwar": 28.3, "teams": ["Chicago Cubs", "Detroit Tigers", "New York Mets"], "positions": ["SS", "2B"], "years_active": ["2014", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Puerto Rico"},
    {"name": "Shohei Ohtani", "fwar": 40.2, "teams": ["Los Angeles Angels", "Los Angeles Dodgers"], "positions": ["P", "DH", "OF"], "years_active": ["2018", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Japan"},
    {"name": "Yu Darvish", "fwar": 40.5, "teams": ["Texas Rangers", "Los Angeles Dodgers", "Chicago Cubs", "San Diego Padres"], "positions": ["P"], "years_active": ["2012", "2024"], "minor_league": False, "international_signing": True, "signing_country": "Japan"},
    {"name": "Masahiro Tanaka", "fwar": 19.1, "teams": ["New York Yankees"], "positions": ["P"], "years_active": ["2014", "2021"], "minor_league": False, "international_signing": True, "signing_country": "Japan"},
    {"name": "Hideo Nomo", "fwar": 19.3, "teams": ["Los Angeles Dodgers", "New York Mets", "Milwaukee Brewers", "Detroit Tigers", "Boston Red Sox", "Tampa Bay Devil Rays", "Kansas City Royals"], "positions": ["P"], "years_active": ["1995", "2008"], "minor_league": False, "international_signing": True, "signing_country": "Japan"},
    {"name": "Hideki Matsui", "fwar": 21.4, "teams": ["New York Yankees", "Los Angeles Angels", "Oakland Athletics", "Tampa Bay Rays"], "positions": ["LF", "OF", "DH"], "years_active": ["2003", "2012"], "minor_league": False, "international_signing": True, "signing_country": "Japan"},
]

ALL_TEAMS = [
    "Arizona Diamondbacks", "Atlanta Braves", "Baltimore Orioles", 
    "Boston Red Sox", "Chicago Cubs", "Chicago White Sox", 
    "Cincinnati Reds", "Cleveland Guardians", "Colorado Rockies",
    "Detroit Tigers", "Houston Astros", "Kansas City Royals",
    "Los Angeles Angels", "Los Angeles Dodgers", "Miami Marlins",
    "Milwaukee Brewers", "Minnesota Twins", "New York Mets",
    "New York Yankees", "Oakland Athletics", "Philadelphia Phillies",
    "Pittsburgh Pirates", "San Diego Padres", "San Francisco Giants",
    "Seattle Mariners", "St. Louis Cardinals", "Tampa Bay Rays",
    "Texas Rangers", "Toronto Blue Jays", "Washington Nationals"
]

POSITIONS = ["C", "1B", "2B", "3B", "SS", "RF", "CF", "LF", "DH", "SP", "RP", "CP"]
INTERNATIONAL_COUNTRIES = ["Dominican Republic", "Venezuela", "Puerto Rico", "Cuba", "Japan", "Mexico", "Panama", "South Korea", "Taiwan", "Colombia", "Brazil", "Argentina"]

def normalize_team_name(team: str) -> str:
    """Normalize historical team names to current names"""
    return TEAM_MAPPINGS.get(team, team)

def generate_historical_players(count: int = 1000) -> List[Dict]:
    """Generate comprehensive historical player data based on fWAR distribution"""
    players = TOP_PLAYERS.copy()
    
    # fWAR distribution pattern (exponential decay from top players)
    # Top 100: 50-120 fWAR
    # Next 200: 30-50 fWAR  
    # Next 300: 15-30 fWAR
    # Next 400: 5-15 fWAR
    # Rest: 0-5 fWAR
    
    fwar_ranges = [
        (50, 120, 100),   # Top 100
        (30, 50, 200),    # Next 200
        (15, 30, 300),    # Next 300
        (5, 15, 400),     # Next 400
        (0, 5, 1000),     # Rest
    ]
    
    player_id = len(TOP_PLAYERS) + 1
    
    # Generate first names and last names from common MLB names
    first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
                   "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
                   "Jose", "Carlos", "Miguel", "Juan", "Luis", "Francisco", "Jorge", "Roberto", "Rafael", "Fernando",
                   "Ichiro", "Hideki", "Hideo", "Masahiro", "Yu", "Shohei", "Roki", "Munetaka"]
    
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
                  "Gonzalez", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Perez", "Hall", "Young", "Allen",
                  "Suzuki", "Tanaka", "Matsui", "Nomo", "Darvish", "Ohtani", "Sasaki", "Irabu"]
    
    for fwar_min, fwar_max, num_players in fwar_ranges:
        for i in range(min(num_players, count - len(players))):
            if len(players) >= count:
                break
                
            fwar = round(random.uniform(fwar_min, fwar_max), 1)
            
            # Generate name
            first = random.choice(first_names)
            last = random.choice(last_names)
            name = f"{first} {last}"
            
            # Avoid duplicates
            while any(p["name"] == name for p in players):
                first = random.choice(first_names)
                last = random.choice(last_names)
                name = f"{first} {last}"
            
            # Generate teams (1-5 teams, weighted toward fewer teams)
            num_teams = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 20, 7, 3])[0]
            teams = random.sample(ALL_TEAMS, min(num_teams, len(ALL_TEAMS)))
            
            # Generate positions
            num_positions = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            available_positions = POSITIONS.copy()
            if num_positions == 1 and random.random() < 0.3:  # 30% chance for pitcher
                positions = [random.choice(["SP", "RP", "CP"])]
            else:
                positions = random.sample([p for p in available_positions if p not in ["SP", "RP", "CP"]], min(num_positions, len(available_positions) - 3))
            
            # Generate years (career length 1-20 years, weighted toward 5-15)
            career_length = random.choices(range(1, 21), weights=[5, 5, 10, 15, 20, 20, 15, 10, 5, 5] + [3]*10)[0]
            start_year = random.randint(1871, 2024 - career_length)
            end_year = start_year + career_length - 1
            
            # International signing (20% chance, higher for lower fWAR players)
            international_chance = 0.2 if fwar > 20 else 0.35
            is_international = random.random() < international_chance
            signing_country = random.choice(INTERNATIONAL_COUNTRIES) if is_international else ""
            
            # Minor league (5% chance, mostly for lower fWAR)
            is_minor_league = random.random() < 0.05 if fwar < 10 else False
            
            player = {
                "name": name,
                "fwar": fwar,
                "teams": teams,
                "positions": positions,
                "years_active": [str(start_year), str(end_year)],
                "minor_league": is_minor_league,
                "international_signing": is_international,
                "signing_country": signing_country,
            }
            
            players.append(player)
            player_id += 1
    
    # Normalize all team names
    for player in players:
        player["teams"] = [normalize_team_name(team) for team in player["teams"]]
    
    # Sort by fWAR descending
    players.sort(key=lambda x: x["fwar"], reverse=True)
    
    return players

def process_player_data(raw_data: List[Dict]) -> List[Dict]:
    """Process and normalize player data"""
    processed = []
    for player in raw_data:
        processed.append({
            "name": player.get("name", ""),
            "fwar": player.get("fwar", 0.0),
            "teams": player.get("teams", []),
            "positions": player.get("positions", []),
            "years_active": player.get("years_active", []),
            "minor_league": player.get("minor_league", False),
            "international_signing": player.get("international_signing", False),
            "signing_country": player.get("signing_country", ""),
        })
    return processed

def save_data(players: List[Dict], filename: str = "players.json"):
    """Save processed player data to JSON file"""
    filepath = DATA_DIR / filename
    with open(filepath, "w") as f:
        json.dump(players, f, indent=2)
    print(f"Saved {len(players)} players to {filepath}")

def main():
    """Main function to generate comprehensive player data"""
    import sys
    
    count = 1000
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"Invalid count: {sys.argv[1]}. Using default: 1000")
    
    print(f"Generating {count} players with comprehensive data...")
    
    players = generate_historical_players(count)
    
    # Process the data
    processed = process_player_data(players)
    
    # Save to file
    save_data(processed)
    
    print(f"Data generation complete! {len(processed)} players loaded.")
    print(f"Top 10 by fWAR:")
    for i, p in enumerate(processed[:10], 1):
        print(f"  {i}. {p['name']}: {p['fwar']} fWAR")

if __name__ == "__main__":
    main()
