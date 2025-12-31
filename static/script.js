const ALL_TEAMS = [
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
];

const ALL_POSITIONS = ["C", "1B", "2B", "3B", "SS", "RF", "CF", "LF", "DH", "SP", "RP", "CP"];

let allPlayers = [], filteredPlayers = [];

function loadTeams() {
    const select = document.getElementById('team-filter');
    ALL_TEAMS.forEach(team => {
        const opt = document.createElement('option');
        opt.value = team;
        opt.textContent = team;
        select.appendChild(opt);
    });
}

function loadPositions() {
    const select = document.getElementById('position-filter');
    ALL_POSITIONS.forEach(pos => {
        const opt = document.createElement('option');
        opt.value = pos;
        opt.textContent = pos;
        select.appendChild(opt);
    });
}

async function loadPlayers() {
    const loading = document.getElementById('loading');
    loading.style.display = 'block';
    
    try {
        const res = await fetch('players.json');
        if (!res.ok) throw new Error('Failed to load data');
        const players = await res.json();
        
        const team = document.getElementById('team-filter').value;
        const position = document.getElementById('position-filter').value;
        const minFwar = parseFloat(document.getElementById('min-fwar').value) || 0;
        
        let filtered = players;
        if (team) {
            filtered = filtered.filter(p => 
                p.teams?.some(t => t.toLowerCase().includes(team.toLowerCase()))
            );
        }
        if (position) {
            const posUpper = position.toUpperCase();
            if (posUpper in ["SP", "RP", "CP"]) {
                filtered = filtered.filter(p => 
                    p.positions?.some(pos => ["P", "SP", "RP", "CP"].includes(pos.toUpperCase()))
                );
            } else {
                filtered = filtered.filter(p => 
                    p.positions?.some(pos => pos.toUpperCase() === posUpper)
                );
            }
        }
        if (minFwar > 0) {
            filtered = filtered.filter(p => (p.bwar || 0) >= minFwar || (p.fwar || 0) >= minFwar);
        }
        
        filtered.sort((a, b) => (b.bwar || 0) - (a.bwar || 0));
        
        allPlayers = players;
        filteredPlayers = filtered;
        
        displayPlayers();
        updateStats();
    } catch (e) {
        console.error('Error loading players:', e);
        document.getElementById('players-tbody').innerHTML = 
            '<tr><td colspan="8" style="text-align: center; color: #ff00ff;">Error loading data.</td></tr>';
    } finally {
        loading.style.display = 'none';
    }
}

function displayPlayers() {
    const tbody = document.getElementById('players-tbody');
    
    if (filteredPlayers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No players found.</td></tr>';
        return;
    }
    
    tbody.innerHTML = filteredPlayers.map((p, i) => {
        const teams = Array.isArray(p.teams) ? p.teams : [p.teams].filter(Boolean);
        const positions = Array.isArray(p.positions) ? p.positions : [p.positions].filter(Boolean);
        
        return `
            <tr>
                <td>${i + 1}</td>
                <td><strong>${p.name || 'Unknown'}</strong></td>
                <td>${p.bwar?.toFixed(1) || '0.0'}</td>
                <td>${p.fwar?.toFixed(1) || '0.0'}</td>
                <td>${teams.map(t => `<span class="badge badge-team">${t}</span>`).join('')}</td>
                <td>${positions.map(pos => `<span class="badge badge-position">${pos}</span>`).join('')}</td>
                <td>${p.years_active?.join(', ') || 'N/A'}</td>
                <td><span class="badge ${p.minor_league ? 'badge-yes' : 'badge-no'}">${p.minor_league ? 'Yes' : 'No'}</span></td>
                <td>${p.international_signing ? `<span class="badge badge-yes">${p.signing_country || 'Yes'}</span>` : '<span class="badge badge-no">No</span>'}</td>
            </tr>
        `;
    }).join('');
}

function updateStats() {
    document.getElementById('total-count').textContent = `Total Players: ${allPlayers.length}`;
    document.getElementById('showing-count').textContent = `Showing: ${filteredPlayers.length}`;
}

document.getElementById('apply-filters').addEventListener('click', loadPlayers);
document.getElementById('reset-filters').addEventListener('click', () => {
    document.getElementById('team-filter').value = '';
    document.getElementById('position-filter').value = '';
    document.getElementById('min-fwar').value = '0';
    loadPlayers();
});

loadTeams();
loadPositions();
loadPlayers();
