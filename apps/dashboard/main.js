/**
 * AEGIS | Orbital Control Logic v5.0
 * Handles real-time telemetry streaming, navigation, and failure injections.
 */

// --- Deployment Bridge ---
const API_BASE_URL = window.NEXT_PUBLIC_API_URL;

// --- DOM Elements ---
const logsFeed = document.getElementById('logs-feed');
const incidentList = document.getElementById('incident-list');
const activePRsCount = document.getElementById('active-prs');
const envBadge = document.getElementById('env-badge');
const lastSync = document.getElementById('last-sync');
const pageTitle = document.getElementById('page-title');

// Health Dots
const healthScout = document.getElementById('health-scout');
const healthBrain = document.getElementById('health-brain');
const healthFixer = document.getElementById('health-fixer');

/**
 * Navigation Logic: Tab Switching
 */
function switchTab(tab) {
    // Update Nav UI
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`nav-${tab}`)?.classList.add('active');

    // Update Panes
    document.querySelectorAll('.tab-panel').forEach(el => el.classList.add('hidden'));

    if (['dashboard', 'chaos'].includes(tab)) {
        document.getElementById(`tab-${tab}`).classList.remove('hidden');
        pageTitle.innerText = tab.charAt(0).toUpperCase() + tab.slice(1) + " Control";
        document.getElementById('metrics-bar').classList.remove('hidden');
    } else {
        document.getElementById('tab-placeholder').classList.remove('hidden');
        document.getElementById('placeholder-title').innerText = tab.charAt(0).toUpperCase() + tab.slice(1);
        pageTitle.innerText = tab.charAt(0).toUpperCase() + tab.slice(1);
        document.getElementById('metrics-bar').classList.add('hidden');
    }
}

/**
 * Telemetry Stream (SSE)
 */
let currentEventSource = null;

function connectToAgentStream(isAnomaly = false) {
    if (currentEventSource) currentEventSource.close();

    console.log(`🔗 Connecting to SRE Loop (Anomaly: ${isAnomaly})...`);
    currentEventSource = new EventSource(`${API_BASE_URL}/api/sre-loop?anomaly=${isAnomaly}`);

    currentEventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);
        addLog(data.message);

        // Update Health Dots based on active agent
        updateHealthStatus(data.message);

        if (data.final_state) {
            currentEventSource.close();
            resetHealthStatus();
            fetchGitVeracity(); // Sync PRs after a possible fix

            // Continuous Observability: Restart normal polling after 5 seconds
            console.log("Cycle complete. Next sensory audit in 5s...");
            setTimeout(() => connectToAgentStream(false), 5000);
        }
    };

    currentEventSource.onerror = function () {
        console.warn("Stream break detected. Re-bridging...");
        currentEventSource.close();
        setTimeout(() => connectToAgentStream(false), 10000);
    };
}

function addLog(message) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';

    if (message.includes('[SCOUT]')) entry.classList.add('observe');
    if (message.includes('[BRAIN]')) entry.classList.add('orient');
    if (message.includes('[GUARDRAIL]')) entry.classList.add('decide');
    if (message.includes('[FIXER]')) entry.classList.add('act');
    if (message.includes('[CURATOR]')) entry.classList.add('decide');

    entry.innerText = message;
    logsFeed.appendChild(entry);
    logsFeed.scrollTop = logsFeed.scrollHeight;
}

function clearLogs() {
    logsFeed.innerHTML = '<div class="log-entry italic">Logs cleared. Awaiting sensory intake...</div>';
}

/**
 * Health Indicators logic
 */
function updateHealthStatus(msg) {
    if (msg.includes('[SCOUT]')) {
        healthScout.className = 'status-dot ONLINE';
    } else if (msg.includes('[BRAIN]')) {
        healthBrain.className = 'status-dot ONLINE';
    } else if (msg.includes('[FIXER]')) {
        healthFixer.className = 'status-dot ONLINE';
    }
}

function resetHealthStatus() {
    healthScout.className = 'status-dot ONLINE';
    healthBrain.className = 'status-dot ONLINE';
    healthFixer.className = 'status-dot IDLE';
}

/**
 * GitHub Veracity Sync
 */
async function fetchGitVeracity() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/git-activity`);
        const data = await res.json();

        if (Array.isArray(data)) {
            activePRsCount.innerText = data.length;
            lastSync.innerText = new Date().toLocaleTimeString();

            incidentList.innerHTML = data.map(pr => `
                <div class="incident-card" onclick="window.open('${pr.html_url}', '_blank')">
                    <div class="incident-info">
                        <h4>PR #${pr.number} - ${pr.title}</h4>
                        <p>REF: ${pr.head.sha.substring(0, 7)} | 🕵️ ${pr.user.login}</p>
                    </div>
                    <div class="status-badge ${pr.state}">${pr.state}</div>
                </div>
            `).join('');
        } else {
            activePRsCount.innerText = "0";
            incidentList.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-secondary);">No active PRs found. System stable.</div>';
        }
    } catch (err) {
        console.error("Git Veracity Error:", err);
        activePRsCount.innerText = "ERR";
    }
}

/**
 * Chaos Engineering
 */
async function triggerChaos(type) {
    addLog(`/// INITIATING CHAOS: ${type.toUpperCase()} ///`);
    try {
        const res = await fetch(`${API_BASE_URL}/demo/inject-failure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type })
        });

        switchTab('dashboard');
        connectToAgentStream(true);

        // Visual indicator on metrics
        document.getElementById('metric-resilience').innerText = "84.2%";
        document.getElementById('metric-resilience').style.color = "var(--danger)";

        setTimeout(() => {
            document.getElementById('metric-resilience').innerText = "99.8%";
            document.getElementById('metric-resilience').style.color = "var(--success)";
        }, 30000);

    } catch (err) {
        addLog(`[SYSTEM] Chaos injection failed: ${err.message}`);
    }
}

/**
 * MTTR Drift (Makes it feel real)
 */
function simulateMetricDrift() {
    const mttr = (4.0 + Math.random() * 0.5).toFixed(1);
    document.getElementById('metric-mttr').innerText = `${mttr}m`;
}

// Initializing
window.switchTab = switchTab;
window.triggerChaos = triggerChaos;
window.clearLogs = clearLogs;

connectToAgentStream(false);
fetchGitVeracity();
setInterval(fetchGitVeracity, 30000);
setInterval(simulateMetricDrift, 15000);
