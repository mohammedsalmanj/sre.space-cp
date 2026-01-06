// Simulate Real-time data fetching
const incidentList = document.getElementById('incident-list');

const mockIncidents = [
    {
        id: 5,
        title: "[INCIDENT] Critical Failure Detected by Scout",
        description: "Scout Agent detected a health check failure (Simulation).",
        severity: "HIGH",
        agents: ["scout", "brain", "memory", "fixer"],
        status: "RESOLVED"
    },
    {
        id: 4,
        title: "[INCIDENT] Latency Spike in Backend",
        description: "MTTR improved by Brain Agent suggesting a container restart.",
        severity: "MEDIUM",
        agents: ["scout", "brain", "fixer"],
        status: "RESOLVED"
    }
];

function renderIncidents() {
    incidentList.innerHTML = mockIncidents.map(inc => `
        <div class="incident-card">
            <div class="number-tag">#${inc.id}</div>
            <div class="incident-info">
                <h4>${inc.title}</h4>
                <p>${inc.description}</p>
                <div class="agent-badges">
                    ${inc.agents.map(a => `<span class="a-badge ${a}">${a.toUpperCase()}</span>`).join('')}
                </div>
            </div>
            <div class="status-check">✓ ${inc.status}</div>
        </div>
    `).join('');
}

// Initial Render
setTimeout(() => {
    renderIncidents();
}, 800);

// Add interactive hover effect or some "live" feel
setInterval(() => {
    const onlineBadges = document.querySelectorAll('.online .tag');
    onlineBadges.forEach(badge => {
        badge.style.opacity = Math.random() > 0.5 ? '1' : '0.7';
    });
}, 500);
