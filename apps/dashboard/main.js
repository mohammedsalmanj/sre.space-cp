// API Configuration
const API_BASE_URL = window.NEXT_PUBLIC_API_URL || "https://sre-space-cp.onrender.com";

// Simulate Real-time data fetching
const incidentList = document.getElementById('incident-list');


async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE_URL}/system/health`);
        const data = await res.json();
        const badge = document.getElementById('env-badge');
        if (data.env) {
            badge.innerText = data.env.toUpperCase();
            badge.className = data.env === 'cloud'
                ? 'px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest bg-blue-500/10 text-blue-400 border border-blue-500/20'
                : 'px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest bg-amber-500/10 text-amber-500 border border-amber-500/20';
        }
    } catch (err) {
        document.getElementById('env-badge').innerText = 'OFFLINE';
    }
}

async function fetchIncidents() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/git-activity`);
        const data = await res.json();

        if (!data || data.error) throw new Error("API Error");

        incidentList.innerHTML = data.map(inc => `
            <div class="incident-card" onclick="window.open('${inc.html_url}', '_blank')">
                <div class="number-tag">#${inc.number}</div>
                <div class="incident-info">
                    <h4>${inc.title}</h4>
                    <p>Status: ${inc.state.toUpperCase()}</p>
                    <div class="agent-badges">
                        <span class="a-badge scout">SCOUT</span>
                        <span class="a-badge brain">BRAIN</span>
                        <span class="a-badge fixer">FIXER</span>
                    </div>
                </div>
                <div class="status-check">${inc.state === 'open' ? '⚡ ACTIVE' : '✓ RESOLVED'}</div>
            </div>
        `).join('');
    } catch (err) {
        console.error("Dashboard Sync Failed:", err);
        incidentList.innerHTML = `<div class="error">Agent Stream Disconnected. Retrying...</div>`;
    }
}

// Initial Render and Polling
checkHealth();
fetchIncidents();
setInterval(checkHealth, 5000);
setInterval(fetchIncidents, 8000);

// Add interactive hover effect or some "live" feel
setInterval(() => {
    const onlineBadges = document.querySelectorAll('.online .tag');
    onlineBadges.forEach(badge => {
        badge.style.opacity = Math.random() > 0.5 ? '1' : '0.7';
    });
}, 500);
