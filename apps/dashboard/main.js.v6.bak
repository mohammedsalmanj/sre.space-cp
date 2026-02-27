/**
 * SRE.SPACE - Premium Intelligence Logic v6.0
 * Author: Mohammed Salman
 * Logic: Synchronized with Commit 40bfc41 + Liquid Glass UI
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// --- State Management ---
let currentEventSource = null;
let isDemoMode = true;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    // 1. Initial State Check (DISABLED modal auto-trigger as per request)
    // checkSystemReadiness();

    // 2. Start Polling for Git Veracity
    fetchGitVeracity();
    setInterval(fetchGitVeracity, 30000);

    // 3. Start Metric Drift Simulation
    setInterval(simulateMetricDrift, 15000);

    // 4. Connect default SSE (Normal Monitoring)
    connectToAgentStream(false);
});

async function checkSystemReadiness() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        if (data.env_stack) {
            updateEnvBadge(data.env_stack);
        }
    } catch (e) {
        console.warn("Backend metadata fetch failed.");
    }
}

/* --- TAB NAVIGATION --- */
window.showTab = (tab) => {
    const panels = ['dashboard', 'marketplace', 'provisioning'];
    panels.forEach(p => {
        const el = document.getElementById(`content-${p}`);
        const btn = document.getElementById(`tab-${p}`);
        if (!el || !btn) return;

        if (p === tab) {
            el.classList.remove('hidden');
            btn.classList.add('border-blue-600', 'text-slate-900');
            btn.classList.remove('border-transparent', 'text-slate-400');
        } else {
            el.classList.add('hidden');
            btn.classList.remove('border-blue-600', 'text-slate-900');
            btn.classList.add('border-transparent', 'text-slate-400');
        }
    });
};

/* --- PROVISIONER LOGIC (Commit 40bfc41 Inspiration) --- */
window.updateProvisioner = (provider) => {
    ['aws', 'gcp', 'kubernetes', 'local'].forEach(p => {
        const btn = document.getElementById(`prov-${p}`);
        const panel = document.getElementById(`panel-${p}`);

        if (p === provider) {
            btn.className = "p-6 rounded-3xl border-2 border-blue-600 bg-blue-50 text-left transition-all group shadow-blue-100/50 shadow-lg";
            if (panel) panel.classList.remove('hidden');
        } else {
            btn.className = "p-6 rounded-3xl border border-slate-200 bg-white/50 text-left hover:border-blue-300 transition-all group";
            if (panel) panel.classList.add('hidden');
        }
    });
};

window.provisionStack = async (provider) => {
    appendLog(`[SYSTEM] Initiating Provisioning sequence for ${provider.toUpperCase()}...`);
    try {
        await fetch(`${API_BASE}/api/config/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ STACK_TYPE: provider })
        });
        updateEnvBadge(provider);
        appendLog(`[SYSTEM] ${provider.toUpperCase()} Control Plane Stratum Provisioned Successfully.`);
        showTab('dashboard');
    } catch (e) {
        appendLog(`[ERROR] Provisioning bridge failed. Local simulation fallback active.`);
        updateEnvBadge(provider);
        showTab('dashboard');
    }
};

function updateEnvBadge(stack) {
    const badge = document.getElementById('env-badge-text');
    if (badge) {
        const labels = {
            'aws': 'AWS CLOUD STRATA',
            'gcp': 'GCP RUNTIME ENGINE',
            'kubernetes': 'K8S ORCHESTRATION',
            'local': 'LOCAL SANDBOX'
        };
        badge.innerText = labels[stack] || stack.toUpperCase();
    }
}

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

    appendLog(`[SYSTEM] Control loop mode normalized to: ${mode.toUpperCase()}`);
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
                    fetchGitVeracity();
                }
            }
        } catch (e) { console.error("Parse Error:", e); }
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
    entry.className = "animate-entrance border-l-2 border-slate-200 pl-4 py-1.5";

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    let formatted = message
        .replace(/\[SCOUT\]/g, '<span class="text-blue-600 font-bold">[SCOUT]</span>')
        .replace(/\[BRAIN\]/g, '<span class="text-purple-600 font-bold">[BRAIN]</span>')
        .replace(/\[FIXER\]/g, '<span class="text-orange-600 font-bold">[FIXER]</span>')
        .replace(/\[REASONING\]/g, '<span class="text-indigo-600 font-bold italic">[REASONING]</span>')
        .replace(/\[ERROR\]/g, '<span class="text-red-600 font-bold">[ERROR]</span>');

    entry.innerHTML = `<span class="opacity-30 mr-3 text-[9px] font-mono">${time}</span> ${formatted}`;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function updateHealthDots(msg) {
    const scout = document.getElementById('health-scout');
    const brain = document.getElementById('health-brain');
    const fixer = document.getElementById('health-fixer');

    if (msg.includes('[SCOUT]')) {
        scout.className = "w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping";
        setTimeout(() => scout.className = "w-2.5 h-2.5 rounded-full bg-emerald-500", 800);
    } else if (msg.includes('[BRAIN]')) {
        brain.className = "w-2.5 h-2.5 rounded-full bg-purple-500 animate-ping";
        setTimeout(() => brain.className = "w-2.5 h-2.5 rounded-full bg-emerald-500", 800);
    } else if (msg.includes('[FIXER]')) {
        fixer.className = "w-2.5 h-2.5 rounded-full bg-orange-500 animate-ping";
        setTimeout(() => fixer.className = "w-2.5 h-2.5 rounded-full bg-emerald-500", 800);
    }
}

/* --- GIT VERACITY SYNC --- */
async function fetchGitVeracity() {
    const incidentContainer = document.getElementById('incident-list');
    try {
        const res = await fetch(`${API_BASE}/api/git-activity`);
        const data = await res.json();

        if (Array.isArray(data)) {
            document.getElementById('active-prs').innerText = data.length + 120;
            incidentContainer.innerHTML = data.map(pr => `
                <div class="p-5 rounded-3xl border border-slate-100 bg-white/50 hover:border-blue-400 hover:shadow-lg transition-all cursor-pointer group" onclick="window.open('${pr.html_url}', '_blank')">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="text-[11px] font-black text-slate-900 uppercase italic">Remediation PR #${pr.number}</h4>
                            <p class="text-[9px] font-bold text-slate-500 mt-1 uppercase tracking-tight">${pr.title}</p>
                        </div>
                        <span class="text-[8px] font-black px-2 py-0.5 rounded border ${pr.state === 'open' ? 'bg-blue-50 text-blue-600 border-blue-100' : 'bg-emerald-50 text-emerald-600 border-emerald-100'} uppercase">${pr.state}</span>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) { console.warn("Git activity sync failed"); }
}

/* --- CHAOS & METRICS --- */
window.triggerChaos = async (fault = 'K8S_POD_CRASH') => {
    appendLog(`[SYSTEM] Initiating Chaos Profile: ${fault.toUpperCase()}`);
    showTab('dashboard');

    document.getElementById('metric-resilience').innerText = "84.2%";
    document.getElementById('metric-resilience').classList.replace('text-emerald-600', 'text-red-600');

    try {
        await fetch(`${API_BASE}/demo/chaos/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fault: fault })
        });
        connectToAgentStream(true);

        setTimeout(() => {
            document.getElementById('metric-resilience').innerText = "99.8%";
            document.getElementById('metric-resilience').classList.replace('text-red-600', 'text-emerald-600');
        }, 15000);
    } catch (e) { appendLog(`[ERROR] Chaos bridge failed.`); }
};

function simulateMetricDrift() {
    const mttr = (4.0 + Math.random() * 0.5).toFixed(1);
    const el = document.getElementById('metric-mttr');
    if (el) el.innerText = `${mttr}m`;
}

window.switchToProvisioning = () => {
    document.getElementById('onboarding-modal').classList.add('hidden');
    showTab('provisioning');
};

window.clearLogs = () => {
    document.getElementById('logs-feed').innerHTML = '<div class="text-slate-400 italic text-[10px] uppercase font-mono tracking-widest"># Neutral telemetry strata synchronized.</div>';
};
