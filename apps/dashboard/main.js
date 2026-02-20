// API Configuration
const API_BASE_URL = window.NEXT_PUBLIC_API_URL || "https://sre-space-cp.onrender.com";

// Simulate Real-time data fetching
const incidentList = document.getElementById('incident-list');


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
fetchIncidents();
setInterval(fetchIncidents, 10000);

// Add interactive hover effect or some "live" feel
setInterval(() => {
    const onlineBadges = document.querySelectorAll('.online .tag');
    onlineBadges.forEach(badge => {
        badge.style.opacity = Math.random() > 0.5 ? '1' : '0.7';
    });
}, 500);
