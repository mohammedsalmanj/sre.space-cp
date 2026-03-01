/**
 * SRE-SPACE | Orbital Control Logic v5.1.0
 * Handles real-time telemetry streaming, navigation, and failure injections.
 */

// --- Deployment Bridge ---
const API_BASE_URL = window.NEXT_PUBLIC_API_URL;

// --- DOM Elements ---
const logsFeed = document.getElementById('logs-feed');
const incidentList = document.getElementById('incident-list');
const activePRsCount = document.getElementById('active-prs');
const lastSync = document.getElementById('last-sync');
const pageTitle = document.getElementById('page-title');

// Health Dots
const healthScout = document.getElementById('health-scout');
const healthBrain = document.getElementById('health-brain');
const healthFixer = document.getElementById('health-fixer');

/**
 * Navigation Logic
 */
function switchTab(tab) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById(`nav-${tab}`)?.classList.add('active');

    document.querySelectorAll('.tab-panel').forEach(el => el.classList.add('hidden'));

    if (['dashboard', 'chaos'].includes(tab)) {
        document.getElementById(`tab-${tab}`).classList.remove('hidden');
        pageTitle.innerText = tab === 'dashboard' ? "Orbital Control" : "Chaos Lab";
        document.getElementById('metrics-bar').classList.remove('hidden');
    } else {
        document.getElementById('tab-placeholder').classList.remove('hidden');
        document.getElementById('placeholder-title').innerText = tab.toUpperCase();
        pageTitle.innerText = tab.toUpperCase();
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
        updateHealthStatus(data.message);

        if (data.final_state) {
            currentEventSource.close();
            resetHealthStatus();
            fetchGitVeracity();
            setTimeout(() => connectToAgentStream(false), 8000);
        }
    };

    currentEventSource.onerror = () => {
        currentEventSource.close();
        setTimeout(() => connectToAgentStream(false), 15000);
    };
}

function addLog(message) {
    if (!logsFeed) return;
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
    logsFeed.innerHTML = '<div class="log-entry" style="opacity:0.5; font-style:italic;">Logs cleared. Awaiting telemetry...</div>';
}

function updateHealthStatus(msg) {
    if (msg.includes('[SCOUT]')) healthScout.className = 'status-dot ONLINE';
    if (msg.includes('[BRAIN]')) healthBrain.className = 'status-dot ONLINE';
    if (msg.includes('[FIXER]')) healthFixer.className = 'status-dot ONLINE';
}

function resetHealthStatus() {
    healthScout.className = 'status-dot ONLINE';
    healthBrain.className = 'status-dot ONLINE';
    healthFixer.className = 'status-dot IDLE';
}

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
                        <p>${pr.head.sha.substring(0, 7)} | 🤖 ${pr.user.login}</p>
                    </div>
                    <div class="status-badge ${pr.state}">${pr.state}</div>
                </div>
            `).join('');
        } else {
            activePRsCount.innerText = "0";
            incidentList.innerHTML = '<div style="padding:20px; text-align:center; opacity:0.5;">No active incidents. System stable.</div>';
        }
    } catch (err) {
        activePRsCount.innerText = "!";
    }
}

async function triggerChaos(type) {
    addLog(`/// INITIATING CHAOS: ${type.toUpperCase()} ///`);
    try {
        await fetch(`${API_BASE_URL}/demo/inject-failure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type })
        });
        switchTab('dashboard');
        connectToAgentStream(true);
        document.getElementById('metric-resilience').innerText = "88.4%";
        document.getElementById('metric-resilience').style.color = "var(--danger)";
        setTimeout(() => {
            document.getElementById('metric-resilience').innerText = "99.8%";
            document.getElementById('metric-resilience').style.color = "var(--success)";
        }, 20000);
    } catch (err) {
        addLog(`[SYSTEM] Injection failed: ${err.message}`);
    }
}

function simulateMetricDrift() {
    const mttr = (3.8 + Math.random() * 0.4).toFixed(1);
    const el = document.getElementById('metric-mttr');
    if (el) el.innerText = `${mttr}m`;
}

window.switchTab = switchTab;
window.triggerChaos = triggerChaos;
window.clearLogs = clearLogs;

connectToAgentStream(false);
fetchGitVeracity();
setInterval(fetchGitVeracity, 60000);
setInterval(simulateMetricDrift, 10000);

