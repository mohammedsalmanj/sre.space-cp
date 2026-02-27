/**
 * SRE.SPACE - Premium Intelligence Logic
 * Author: Mohammed Salman
 * Logic: Synchronized with Cyber-Insurance functional requirements + Liquid Glass UI
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// --- State Management ---
let currentEventSource = null;
let currentBackoff = 1000;
let isDemoMode = true;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    // 1. Initial State Check
    checkSystemReadiness();

    // 2. Start Polling for Git Veracity
    fetchGitVeracity();
    setInterval(fetchGitVeracity, 30000);

    // 3. Start Metric Drift Simulation (Legacy requirement)
    setInterval(simulateMetricDrift, 15000);

    // 4. Connect default SSE (Normal Monitoring)
    connectToAgentStream(false);
});

async function checkSystemReadiness() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        // If stack isn't configured, show the Orbital Setup
        if (!data.env_stack && !sessionStorage.getItem('skip_onboarding')) {
            document.getElementById('onboarding-modal').classList.remove('hidden');
        } else {
            document.getElementById('onboarding-modal').classList.add('hidden');
            if (data.env_stack) {
                document.getElementById('env-badge').innerText = data.env_stack.toUpperCase();
            }
        }
    } catch (e) {
        console.warn("Readiness check failed, showing setup.");
        document.getElementById('onboarding-modal').classList.remove('hidden');
    }
}

/* --- TAB NAVIGATION --- */
window.showTab = (tab) => {
    const panels = ['dashboard', 'marketplace', 'deploy'];
    panels.forEach(p => {
        const el = document.getElementById(`content-${p}`);
        const btn = document.getElementById(`tab-${p}`);
        if (p === tab) {
            el.classList.remove('hidden');
            btn.classList.add('border-blue-600', 'text-slate-800');
            btn.classList.remove('border-transparent', 'text-slate-400');
        } else {
            el.classList.add('hidden');
            btn.classList.remove('border-blue-600', 'text-slate-800');
            btn.classList.add('border-transparent', 'text-slate-400');
        }
    });
};

/* --- MODE TOGGLE --- */
window.setMode = (mode) => {
    isDemoMode = (mode === 'demo');
    const btnDemo = document.getElementById('btn-mode-demo');
    const btnReal = document.getElementById('btn-mode-real');

    if (isDemoMode) {
        btnDemo.className = "px-3 py-1 text-[10px] font-black rounded-lg transition-all bg-blue-600 text-white shadow-sm";
        btnReal.className = "px-3 py-1 text-[10px] font-black rounded-lg transition-all text-slate-400";
    } else {
        btnReal.className = "px-3 py-1 text-[10px] font-black rounded-lg transition-all bg-emerald-600 text-white shadow-sm";
        btnDemo.className = "px-3 py-1 text-[10px] font-black rounded-lg transition-all text-slate-400";
    }

    appendLog(`[SYSTEM] Mode switched to: ${mode.toUpperCase()}`);
};

/* --- CORE AUTONOMIC LOOP (SSE) --- */
function connectToAgentStream(isAnomaly = false) {
    if (currentEventSource) currentEventSource.close();

    const url = `${API_BASE}/api/sre-loop?anomaly=${isAnomaly}&simulation=${isDemoMode}`;
    currentEventSource = new EventSource(url);

    currentEventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.message) {
                appendLog(data.message);
                updateHealthDots(data.message);

                if (data.final_state === 'Resolved') {
                    setStatus('NOMINAL');
                    fetchGitVeracity(); // Refresh PRs
                }
            }
        } catch (e) {
            console.error("Parse Error:", e);
        }
    };

    currentEventSource.onerror = () => {
        currentEventSource.close();
        setTimeout(() => connectToAgentStream(false), 10000);
    };
}

function appendLog(message) {
    const container = document.getElementById('logs-feed');
    if (!container) return;

    const entry = document.createElement('div');
    entry.className = "animate-entrance border-l-2 border-slate-100 pl-3 py-1";

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    // Style specific agent tags
    let formatted = message
        .replace(/\[SCOUT\]/g, '<span class="text-blue-600 font-bold">[SCOUT]</span>')
        .replace(/\[BRAIN\]/g, '<span class="text-purple-600 font-bold">[BRAIN]</span>')
        .replace(/\[FIXER\]/g, '<span class="text-orange-600 font-bold">[FIXER]</span>')
        .replace(/\[REASONING\]/g, '<span class="text-indigo-600 font-bold italic">[REASONING]</span>')
        .replace(/\[ERROR\]/g, '<span class="text-red-600 font-bold">[ERROR]</span>');

    entry.innerHTML = `<span class="opacity-30 mr-2 text-[9px]">${time}</span> ${formatted}`;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function updateHealthDots(msg) {
    const scout = document.getElementById('health-scout');
    const brain = document.getElementById('health-brain');
    const fixer = document.getElementById('health-fixer');

    if (msg.includes('[SCOUT]')) {
        scout.className = "w-2 h-2 rounded-full bg-blue-500 animate-ping";
        setTimeout(() => scout.className = "w-2 h-2 rounded-full bg-emerald-500", 1000);
    } else if (msg.includes('[BRAIN]')) {
        brain.className = "w-2 h-2 rounded-full bg-purple-500 animate-ping";
        setTimeout(() => brain.className = "w-2 h-2 rounded-full bg-emerald-500", 1000);
    } else if (msg.includes('[FIXER]')) {
        fixer.className = "w-2 h-2 rounded-full bg-orange-500 animate-ping";
        setTimeout(() => fixer.className = "w-2 h-2 rounded-full bg-emerald-500", 1000);
    }
}

/* --- GIT VERACITY SYNC --- */
async function fetchGitVeracity() {
    const incidentContainer = document.getElementById('incident-list');
    try {
        const res = await fetch(`${API_BASE}/api/git-activity`);
        const data = await res.json();

        if (Array.isArray(data)) {
            document.getElementById('active-prs').innerText = data.length + 122; // Legacy baseline
            incidentContainer.innerHTML = data.map(pr => `
                <div class="p-4 rounded-xl border border-slate-100 bg-white/50 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group" onclick="window.open('${pr.html_url}', '_blank')">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="text-[11px] font-black text-slate-800 uppercase">PR #${pr.number}</h4>
                            <p class="text-[9px] text-slate-500 mt-1 uppercase">${pr.title}</p>
                        </div>
                        <span class="text-[8px] font-black px-2 py-0.5 rounded border ${pr.state === 'open' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-emerald-50 text-emerald-600 border-emerald-100'} uppercase">${pr.state}</span>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.warn("Git activity sync failed");
    }
}

/* --- CHAOS & METRICS --- */
window.triggerChaos = async (fault = 'K8S_POD_CRASH') => {
    appendLog(`[SYSTEM] Initiating chaos injection: ${fault.toUpperCase()}`);
    showTab('dashboard');

    // Simulate immediate metric impact
    document.getElementById('metric-resilience').innerText = "84.2%";
    document.getElementById('metric-resilience').classList.replace('text-emerald-600', 'text-red-600');

    try {
        await fetch(`${API_BASE}/demo/chaos/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fault: fault })
        });
        connectToAgentStream(true);

        // Restore metrics after recovery (mock)
        setTimeout(() => {
            document.getElementById('metric-resilience').innerText = "99.8%";
            document.getElementById('metric-resilience').classList.replace('text-red-600', 'text-emerald-600');
        }, 15000);
    } catch (e) {
        appendLog(`[ERROR] Chaos bridge failed.`);
    }
};

function simulateMetricDrift() {
    const mttr = (4.0 + Math.random() * 0.5).toFixed(1);
    document.getElementById('metric-mttr').innerText = `${mttr}m`;
}

/* --- ONBOARDING --- */
window.selectStack = async (stack) => {
    try {
        await fetch(`${API_BASE}/api/config/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ STACK_TYPE: stack })
        });
        document.getElementById('onboarding-modal').classList.add('hidden');
        document.getElementById('env-badge').innerText = stack.toUpperCase();
        appendLog(`[SYSTEM] Environment strata configured: ${stack.toUpperCase()}`);
    } catch (e) {
        skipOnboarding();
    }
};

window.skipOnboarding = () => {
    sessionStorage.setItem('skip_onboarding', 'true');
    document.getElementById('onboarding-modal').classList.add('hidden');
};

window.clearLogs = () => {
    document.getElementById('logs-feed').innerHTML = '<div class="text-slate-400 italic text-[10px]"># Neutral strata synchronized. Awaiting sensory intake...</div>';
};
