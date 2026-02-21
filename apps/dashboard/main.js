/**
 * SRE.SPACE | Mission Control Logic v4.7
 * Handles real-time telemetry streaming and GitHub veracity synchronization.
 */

// Deployment Bridge: Automatic detection of backend location
const API_BASE_URL = window.NEXT_PUBLIC_API_URL;

const logsFeed = document.getElementById('logs-feed');
const incidentList = document.getElementById('incident-list');
const activePRsCount = document.getElementById('active-prs');
const envBadge = document.getElementById('env-badge');
const lastSync = document.getElementById('last-sync');

/**
 * Block 1: Real-Time Veracity (Server-Sent Events)
 * Connects to the backend OODA stream to visualize agent reasoning in real-time.
 */
function connectToAgentStream() {
    console.log("🔗 Connecting to Orbital Control Plane...");
    // anomaly=false ensures the loop only triggers detection, not hard mutation during boot
    const eventSource = new EventSource(`${API_BASE_URL}/api/sre-loop?anomaly=false`);

    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);
        const entry = document.createElement('div');
        entry.className = 'log-entry';

        // Semantic color coding for the OODA stages (Observe, Orient, Decide, Act)
        if (data.message.includes('[OBSERVE]')) entry.classList.add('observe');
        if (data.message.includes('[ORIENT]')) entry.classList.add('orient');
        if (data.message.includes('[DECIDE]')) entry.classList.add('decide');
        if (data.message.includes('[ACT]')) entry.classList.add('act');

        entry.innerText = data.message;
        logsFeed.appendChild(entry);

        // Auto-scroll to keep the latest agent reasoning in view
        logsFeed.scrollTop = logsFeed.scrollHeight;
    };

    eventSource.onerror = function () {
        console.warn("Telemetry stream interrupted. Re-bridging in 5s...");
        eventSource.close();
        setTimeout(connectToAgentStream, 5000);
    };
}

/**
 * Block 3: GitHub Integrity Feed
 * Cross-references agent logs with ground-truth reality on GitHub.
 */
async function fetchGitVeracity() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/git-activity`);
        const data = await res.json();

        if (data && !data.error) {
            // Update HUD metrics
            activePRsCount.innerText = data.length;
            lastSync.innerText = new Date().toLocaleTimeString();

            // Generate interactive PR cards
            incidentList.innerHTML = data.map(pr => `
                <div class="incident-card" onclick="window.open('${pr.html_url}', '_blank')" title="View SRE Post-Mortem on GitHub">
                    <div class="incident-info">
                        <h4>PR #${pr.number} - ${pr.title}</h4>
                        <p style="font-family: 'JetBrains Mono'; font-size: 10px; color: #94a3b8;">
                            REF: ${pr.head.sha.substring(0, 7)} | 🕵️ ${pr.user.login}
                        </p>
                    </div>
                    <div class="status-badge ${pr.state}">
                        ${pr.state.toUpperCase()}
                    </div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Veracity synchronization failed:", err);
    }
}

/**
 * Block 2: System Health & Environment Detection
 * Displays the hosting environment (CLOUD/LOCAL) and RAM health.
 */
async function updateSystemState() {
    try {
        const res = await fetch(`${API_BASE_URL}/system/health`);
        const data = await res.json();

        if (data.env) {
            envBadge.innerText = data.env.toUpperCase();
            // Color branding for different deployment nodes
            envBadge.style.background = data.env === 'cloud' ? 'rgba(56, 189, 248, 0.2)' : 'rgba(245, 158, 11, 0.2)';
            envBadge.style.color = data.env === 'cloud' ? '#38bdf8' : '#f59e0b';
        }
    } catch (err) {
        envBadge.innerText = "OFFLINE";
        envBadge.style.background = "rgba(244, 63, 94, 0.2)";
        envBadge.style.color = "#f43f5e";
    }
}

// --- Lifecycle Initialization ---
// Start all veracity loops immediately on page load
connectToAgentStream();
fetchGitVeracity();
updateSystemState();

// Periodic synchronization (10s for Git, 5s for Health)
setInterval(fetchGitVeracity, 10000);
setInterval(updateSystemState, 5000);
