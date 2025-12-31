# MLB fWAR Player Explorer

A web tool to explore players with the highest fWAR (FanGraphs Wins Above Replacement) for every MLB team in history, including minor league players and international signings.

## Features

- **Comprehensive Player Database**: Includes all players associated with MLB teams, even if they only played in minor leagues
- **International Signings**: Tracks players signed from South America and other international locations
- **Advanced Filtering**:
  - Filter by team
  - Filter by position
  - Filter by minimum fWAR
- **Clean UI**: Modern, responsive interface for easy exploration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate sample data (or integrate with real data sources):
```bash
python data_fetcher.py
```

3. Run the server:
```bash
python app.py
```

4. Open your browser to `http://localhost:8000`

## Data Sources

The tool is designed to work with MLB player data. To populate with real data, you'll need to:

1. **FanGraphs**: Access fWAR statistics (may require API access or web scraping with permission)
2. **Baseball Reference**: Historical player data and team affiliations
3. **MLB.com**: Official player records and international signing information
4. **Minor League Baseball**: Data on players who only played in minor leagues

The `data_fetcher.py` module provides a structure for integrating these data sources.

## Project Structure

```
.
├── app.py              # FastAPI backend server
├── data_fetcher.py     # Data fetching and processing module
├── requirements.txt    # Python dependencies
├── data/
│   └── players.json    # Player data (generated)
└── static/
    ├── index.html      # Frontend HTML
    ├── style.css       # Styling
    └── script.js       # Frontend JavaScript
```

## API Endpoints

- `GET /` - Main web interface
- `GET /api/teams` - List all MLB teams
- `GET /api/positions` - List all positions
- `GET /api/players` - Get players with filters (team, position, min_fwar)
- `GET /api/players/by-team` - Get top fWAR player for each team

## Contributing

Contributions are welcome! Feel free to:
- Add data source integrations
- Improve the UI/UX
- Add new filtering options
- Enhance data processing

## License

MIT License - feel free to use and modify as needed.

## Future Enhancements

- Integration with real MLB data APIs
- Export functionality (CSV, JSON)
- Advanced statistics and visualizations
- Player comparison tools
- Historical team rosters

