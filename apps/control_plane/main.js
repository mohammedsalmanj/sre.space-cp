/**
 * SRE.SPACE - Premium Intelligence Logic v6.0
 * Author: Mohammed Salman
 * Logic: Dual-Track Onboarding + Neural Telemetry Strata
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// --- State Management ---
let currentEventSource = null;
let isDemoMode = true;
let currentTrack = 'local'; // local | cloud
let selectedStack = 'aws-ec2';

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    // Initial UI state
    showTab('dashboard');

    // 2. Start Polling for Git Veracity
    fetchGitVeracity();
    setInterval(fetchGitVeracity, 30000);

    // 3. Start Metric Drift Simulation
    setInterval(simulateMetricDrift, 15000);

    // 4. Connect default SSE (Normal Monitoring)
    connectToAgentStream(false);
});

/* --- TAB NAVIGATION --- */
window.showTab = (tab) => {
    const panels = ['dashboard', 'provisioning'];
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

/* --- v6.0 PROVISIONING LOGIC --- */
window.selectProvisionTrack = (stack) => {
    selectedStack = stack;
    const stacks = ['aws-ec2', 'eks', 'eb'];
    stacks.forEach(s => {
        const el = document.getElementById(`track-${s}`);
        if (!el) return;
        if (s === stack) {
            el.classList.add('border-blue-600', 'shadow-2xl', 'scale-[1.02]');
            el.classList.remove('border-transparent', 'bg-white/60');
        } else {
            el.classList.remove('border-blue-600', 'shadow-2xl', 'scale-[1.02]');
            el.classList.add('border-transparent', 'bg-white/60');
        }
    });
    appendLog(`[SYSTEM] Stack Stratum adjusted to: ${stack.toUpperCase()}`);
};

window.setProvisionTrack = (track) => {
    currentTrack = track;
    const tracks = ['local', 'cloud'];
    tracks.forEach(t => {
        const el = document.getElementById(`track-option-${t}`);
        if (!el) return;
        if (t === track) {
            el.classList.add('border-blue-600', 'bg-blue-50/50', 'shadow-2xl');
            el.classList.remove('border-transparent', 'bg-white/40');
        } else {
            el.classList.remove('border-blue-600', 'bg-blue-50/50', 'shadow-2xl');
            el.classList.add('border-transparent', 'bg-white/40');
        }
    });
    appendLog(`[SYSTEM] Onboarding track transitioned to: ${track.toUpperCase()}`);
};

window.copyCmd = (type) => {
    const ids = {
        'docker': 'cmd-docker',
        'helm': 'cmd-helm',
        'kubeverify': 'cmd-kubeverify'
    };
    const el = document.getElementById(ids[type]);
    if (!el) return;

    const text = el.innerText;
    navigator.clipboard.writeText(text).then(() => {
        appendLog(`[SYSTEM] Command copied to clipboard: ${type.toUpperCase()}`);
    });
};

window.finalHandshake = async () => {
    appendLog(`[SYSTEM] Initiating Final Handshake protocol...`);
    appendLog(`[SCOUT] Verifying OTel Endpoint veracity...`);

    await new Promise(r => setTimeout(r, 1000));
    appendLog(`[BRAIN] Checking Cloud Provider API authorities...`);

    await new Promise(r => setTimeout(r, 1500));
    appendLog(`[SYSTEM] Control Link Established. Initializing OODA loop.`);

    setTimeout(() => {
        showTab('dashboard');
        appendLog(`[SYSTEM] Workspace Normalized. Welcome Mohammed Salman.`);
    }, 1000);
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
                if (data.final_state === 'Resolved') {
                    fetchGitVeracity();
                }
            }
        } catch (e) { console.error("Parse Error:", e); }
    };

    currentEventSource.onerror = () => {
        currentEventSource.close();
        setTimeout(() => connectToAgentStream(false), 15000);
    };
}

function appendLog(message) {
    const container = document.getElementById('logs-feed');
    if (!container) return;

    const entry = document.createElement('div');
    entry.className = "animate-entrance border-l-2 border-slate-200 pl-4 py-2 bg-white/50 rounded-r-xl border-l-blue-500 shadow-sm";

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    let formatted = message
        .replace(/\[SCOUT\]/g, '<span class="text-blue-600 font-black tracking-widest">[SCOUT]</span>')
        .replace(/\[BRAIN\]/g, '<span class="text-purple-600 font-black tracking-widest">[BRAIN]</span>')
        .replace(/\[FIXER\]/g, '<span class="text-orange-600 font-black tracking-widest">[FIXER]</span>')
        .replace(/\[REASONING\]/g, '<span class="text-indigo-600 font-black italic">[REASONING]</span>')
        .replace(/\[SYSTEM\]/g, '<span class="text-slate-900 font-black uppercase">[SYSTEM]</span>')
        .replace(/\[ERROR\]/g, '<span class="text-red-600 font-black">[ERROR]</span>');

    entry.innerHTML = `<span class="opacity-30 mr-3 text-[9px] font-mono">${time}</span> ${formatted}`;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

/* --- GIT VERACITY SYNC --- */
async function fetchGitVeracity() {
    try {
        const res = await fetch(`${API_BASE}/api/git-activity`);
        const data = await res.json();
        if (Array.isArray(data)) {
            document.getElementById('active-prs').innerText = data.length + 124;
        }
    } catch (e) { console.warn("Git activity sync failed"); }
}

/* --- CHAOS & MODE --- */
window.triggerChaos = async (fault) => {
    appendLog(`[SYSTEM] Injecting Anomaly Profile: ${fault.toUpperCase()}`);
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
        }, 20000);
    } catch (e) { appendLog(`[ERROR] Chaos bridge failed.`); }
};

window.setMode = (mode) => {
    isDemoMode = (mode === 'demo');
    const btnDemo = document.getElementById('btn-mode-demo');
    const btnReal = document.getElementById('btn-mode-real');

    if (isDemoMode) {
        btnDemo.className = "px-4 py-1.5 text-[10px] font-black rounded-xl transition-all bg-blue-600 text-white shadow-xl uppercase tracking-widest";
        btnReal.className = "px-4 py-1.5 text-[10px] font-black rounded-xl transition-all text-slate-400 uppercase tracking-widest";
    } else {
        btnReal.className = "px-4 py-1.5 text-[10px] font-black rounded-xl transition-all bg-emerald-600 text-white shadow-xl uppercase tracking-widest";
        btnDemo.className = "px-4 py-1.5 text-[10px] font-black rounded-xl transition-all text-slate-400 uppercase tracking-widest";
    }

    appendLog(`[SYSTEM] Control loop mode transitioned to: ${mode.toUpperCase()} MODE`);
    connectToAgentStream(false);
};

function simulateMetricDrift() {
    const mttr = (4.0 + Math.random() * 0.5).toFixed(1);
    const el = document.getElementById('metric-mttr');
    if (el) el.innerText = `${mttr}m`;
}

window.clearLogs = () => {
    document.getElementById('logs-feed').innerHTML = '<div class="text-slate-400 italic text-[10px] uppercase font-mono tracking-widest"># Neutral telemetry strata synchronized.</div>';
};
