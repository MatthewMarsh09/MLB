const API_BASE = 'http://localhost:8000/api';
let allPlayers = [], filteredPlayers = [];

async function loadTeams() {
    try {
        const res = await fetch(`${API_BASE}/teams`);
        const data = await res.json();
        const select = document.getElementById('team-filter');
        data.teams.forEach(team => {
            const opt = document.createElement('option');
            opt.value = team;
            opt.textContent = team;
            select.appendChild(opt);
        });
    } catch (e) { console.error('Error loading teams:', e); }
}

async function loadPositions() {
    try {
        const res = await fetch(`${API_BASE}/positions`);
        const data = await res.json();
        const select = document.getElementById('position-filter');
        data.positions.forEach(pos => {
            const opt = document.createElement('option');
            opt.value = pos;
            opt.textContent = pos;
            select.appendChild(opt);
        });
    } catch (e) { console.error('Error loading positions:', e); }
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
        
        const res = await fetch(`${API_BASE}/players?${params}`);
        const data = await res.json();
        
        allPlayers = data.players || [];
        filteredPlayers = allPlayers;
        
        displayPlayers();
        updateStats();
    } catch (e) {
        console.error('Error loading players:', e);
        document.getElementById('players-tbody').innerHTML = 
            '<tr><td colspan="8" style="text-align: center; color: red;">Error loading data.</td></tr>';
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
