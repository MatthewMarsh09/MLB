const API_BASE = 'http://localhost:8000/api';

let allPlayers = [];
let filteredPlayers = [];

async function loadTeams() {
    try {
        const response = await fetch(`${API_BASE}/teams`);
        const data = await response.json();
        const select = document.getElementById('team-filter');
        data.teams.forEach(team => {
            const option = document.createElement('option');
            option.value = team;
            option.textContent = team;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading teams:', error);
    }
}

async function loadPositions() {
    try {
        const response = await fetch(`${API_BASE}/positions`);
        const data = await response.json();
        const select = document.getElementById('position-filter');
        data.positions.forEach(position => {
            const option = document.createElement('option');
            option.value = position;
            option.textContent = position;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading positions:', error);
    }
}

async function loadPlayers() {
    const loading = document.getElementById('loading');
    loading.style.display = 'block';
    
    try {
        const team = document.getElementById('team-filter').value;
        const position = document.getElementById('position-filter').value;
        const minFwar = parseFloat(document.getElementById('min-fwar').value) || 0;
        
        const params = new URLSearchParams();
        if (team) params.append('team', team);
        if (position) params.append('position', position);
        if (minFwar > 0) params.append('min_fwar', minFwar);
        params.append('limit', 500);
        
        const response = await fetch(`${API_BASE}/players?${params}`);
        const data = await response.json();
        
        allPlayers = data.players || [];
        filteredPlayers = allPlayers;
        
        displayPlayers();
        updateStats();
    } catch (error) {
        console.error('Error loading players:', error);
        document.getElementById('players-tbody').innerHTML = 
            '<tr><td colspan="8" style="text-align: center; color: red;">Error loading data. Make sure the server is running.</td></tr>';
    } finally {
        loading.style.display = 'none';
    }
}

function displayPlayers() {
    const tbody = document.getElementById('players-tbody');
    
    if (filteredPlayers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No players found matching your filters.</td></tr>';
        return;
    }
    
    tbody.innerHTML = filteredPlayers.map((player, index) => {
        const teams = Array.isArray(player.teams) ? player.teams : [player.teams].filter(Boolean);
        const positions = Array.isArray(player.positions) ? player.positions : [player.positions].filter(Boolean);
        
        return `
            <tr>
                <td>${index + 1}</td>
                <td><strong>${player.name || 'Unknown'}</strong></td>
                <td>${player.fwar?.toFixed(1) || '0.0'}</td>
                <td>${teams.map(t => `<span class="badge badge-team">${t}</span>`).join('')}</td>
                <td>${positions.map(p => `<span class="badge badge-position">${p}</span>`).join('')}</td>
                <td>${player.years_active?.join(', ') || 'N/A'}</td>
                <td><span class="badge ${player.minor_league ? 'badge-yes' : 'badge-no'}">${player.minor_league ? 'Yes' : 'No'}</span></td>
                <td>${player.international_signing ? `<span class="badge badge-yes">${player.signing_country || 'Yes'}</span>` : '<span class="badge badge-no">No</span>'}</td>
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

// Load initial data
loadTeams();
loadPositions();
loadPlayers();

