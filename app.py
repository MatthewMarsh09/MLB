from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Optional
import json
from pathlib import Path

app = FastAPI(title="MLB fWAR Player Explorer")
app.mount("/static", StaticFiles(directory="static"), name="static")

DATA_FILE = Path("data/players.json")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

@app.get("/api/teams")
async def get_teams():
    teams = [
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
    return {"teams": teams}

@app.get("/api/positions")
async def get_positions():
    return {"positions": ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "OF", "DH", "UTIL"]}

@app.get("/api/players")
async def get_players(
    team: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    min_fwar: Optional[float] = Query(0),
    limit: Optional[int] = Query(100)
):
    if not DATA_FILE.exists():
        return {"players": [], "message": "No data file found."}
    
    with open(DATA_FILE, "r") as f:
        players = json.load(f)
    
    filtered = players
    if team:
        filtered = [p for p in filtered if team.lower() in [t.lower() for t in p.get("teams", [])]]
    if position:
        filtered = [p for p in filtered if position.upper() in [pos.upper() for pos in p.get("positions", [])]]
    if min_fwar:
        filtered = [p for p in filtered if p.get("fwar", 0) >= min_fwar]
    
    filtered.sort(key=lambda x: x.get("fwar", 0), reverse=True)
    return {"players": filtered[:limit], "total": len(filtered)}

@app.get("/api/players/by-team")
async def get_players_by_team():
    if not DATA_FILE.exists():
        return {"by_team": {}}
    
    with open(DATA_FILE, "r") as f:
        players = json.load(f)
    
    by_team = {}
    for player in players:
        for team in player.get("teams", []):
            if team not in by_team or player.get("fwar", 0) > by_team[team].get("fwar", 0):
                by_team[team] = player
    
    return {"by_team": by_team}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
