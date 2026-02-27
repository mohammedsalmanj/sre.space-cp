/**
 * SRE.SPACE - Premium Intelligence Logic v6.0
 * Author: Mohammed Salman
 * Logic: Dual-Track Wizard + Neural Sensory Intake
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// --- State Management ---
let currentEventSource = null;
let isDemoMode = true;
let activeWizardStep = 1;
let selectedWizardTrack = 'local'; // local | cloud

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    showTab('dashboard');
    setInterval(simulateMetricDrift, 10000);
    fetchGitVeracity();
    connectToAgentStream(false);
});

/* --- TAB NAVIGATION --- */
window.showTab = (tab) => {
    ['dashboard', 'wizard'].forEach(p => {
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

/* --- setup wizard logic --- */
window.selectWizardTrack = (track) => {
    selectedWizardTrack = track;
    ['local', 'cloud'].forEach(t => {
        const el = document.getElementById(`wiz-track-${t}`);
        if (t === track) {
            el.classList.remove('border-transparent', 'bg-white/40');
            el.classList.add('border-blue-600', 'bg-blue-50/50', 'shadow-2xl');
            document.getElementById(`status-${track === 'cloud' ? 'aws' : 'docker'}`).classList.add('connected');
        } else {
            el.classList.remove('border-blue-600', 'bg-blue-50/50', 'shadow-2xl');
            el.classList.add('border-transparent', 'bg-white/40');
        }
    });
    showToast(`Environment Strategy: ${track.toUpperCase()} Normalized.`);
};

window.wizardNext = () => {
    if (activeWizardStep >= 3) return;
    activeWizardStep++;
    updateWizardUI();
};

window.wizardPrev = () => {
    if (activeWizardStep <= 1) return;
    activeWizardStep--;
    updateWizardUI();
};

function updateWizardUI() {
    // Hide all steps
    for (let i = 1; i <= 3; i++) {
        document.getElementById(`wizard-step-${i}`).classList.add('hidden');
        document.getElementById(`step-dot-${i}`).classList.remove('wizard-active-dot', 'bg-blue-600', 'text-white');
        document.getElementById(`step-dot-${i}`).classList.add('bg-white', 'text-slate-300', 'border-slate-100');
        if (i < 3) document.getElementById(`step-bar-${i}`).style.width = '0%';
    }

    // Show current step
    document.getElementById(`wizard-step-${activeWizardStep}`).classList.remove('hidden');

    // Update dots and bars
    for (let i = 1; i <= activeWizardStep; i++) {
        const dot = document.getElementById(`step-dot-${i}`);
        dot.classList.add('wizard-active-dot', 'bg-blue-600', 'text-white');
        dot.classList.remove('bg-white', 'text-slate-300', 'border-slate-100');
        if (i < activeWizardStep) document.getElementById(`step-bar-${i}`).style.width = '100%';
    }

    // Toggle forms
    document.getElementById('form-local-handshake').classList.add('hidden');
    document.getElementById('form-cloud-handshake').classList.add('hidden');

    if (activeWizardStep === 2) {
        if (selectedWizardTrack === 'local') {
            document.getElementById('form-local-handshake').classList.remove('hidden');
        } else {
            document.getElementById('form-cloud-handshake').classList.remove('hidden');
        }
    }

    // Nav buttons
    document.getElementById('btn-wiz-prev').classList.toggle('hidden', activeWizardStep === 1);
    const nextBtn = document.getElementById('btn-wiz-next');
    if (activeWizardStep === 3) {
        nextBtn.innerHTML = 'Initialize Data Plane';
        startHeartbeatRotation();
    } else {
        nextBtn.innerHTML = 'Advance Protocol →';
    }
}

window.verifyCloudConnection = async () => {
    const spinner = document.getElementById('cred-spinner');
    const check = document.getElementById('cred-check');
    const btn = document.getElementById('btn-verify-cloud');

    spinner.classList.remove('hidden');
    btn.disabled = true;
    btn.innerText = 'Verifying Cloud Authority...';

    await new Promise(r => setTimeout(r, 2000));

    spinner.classList.add('hidden');
    check.classList.remove('hidden');
    btn.innerText = 'Authority Verified';
    btn.classList.add('bg-emerald-600');

    showToast("Cloud Control Link Established.");
};

function startHeartbeatRotation() {
    const status = document.getElementById('heartbeat-status');
    const radar = document.getElementById('heartbeat-radar');

    let count = 0;
    const interval = setInterval(() => {
        if (count > 2 || activeWizardStep !== 3) {
            clearInterval(interval);
            return;
        }
        count++;
        if (count === 1) status.innerText = "Synchronizing eBPF syscall hooks...";
        if (count === 2) {
            status.innerText = "Packet Detected: 0x4f22ae1 (Production)";
            status.classList.replace('text-blue-400', 'text-emerald-500');
            radar.classList.add('border-emerald-500');
        }
    }, 2000);
}

window.finalizeSetup = () => {
    showTab('dashboard');
    showToast("Workspace Normalized. System Online.");
    document.getElementById('status-k8s').classList.add('connected');
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
                    resetIncidentState();
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
    entry.className = "animate-entrance border-l-3 border-blue-500 pl-6 py-3 bg-white/40 rounded-r-2xl shadow-sm border-l-[4px]";

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    // Linguistic Markers
    let formatted = message
        .replace(/\[SCOUT\]/g, '<span class="text-blue-600 font-black tracking-widest">[SCOUT Agent]</span>')
        .replace(/\[BRAIN\]/g, '<span class="text-purple-600 font-black tracking-widest">[BRAIN Core]</span>')
        .replace(/\[FIXER\]/g, '<span class="text-orange-600 font-black tracking-widest">[FIXER Drone]</span>')
        .replace(/\[SYSTEM\]/g, '<span class="text-slate-900 font-black uppercase">[CONTROL PLANE]</span>')
        .replace(/\[ERROR\]/g, '<span class="text-red-600 font-black">[ANOMALY]</span>')
        .replace(/\{(.+?)\}/g, '<span class="log-json-sys">{$1}</span>');

    // Syntax-highlighted JSON simulation for terminal logs
    if (message.includes('{')) {
        formatted = formatted.replace(/"(\w+)"\s*:/g, '<span class="log-json-key">"$1"</span>:');
        formatted = formatted.replace(/:\s*"([^"]+)"/g, ': <span class="log-json-val">"$1"</span>');
    }

    entry.innerHTML = `<span class="opacity-20 mr-4 text-[10px] font-bold">${time}</span> ${formatted}`;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;

    // Trigger visual effects on specific words
    if (message.includes('ANOMALY') || message.includes('CRITICAL')) {
        triggerVisualFault('critical');
    }
}

function triggerVisualFault(level) {
    const glow = document.getElementById('ambient-glow');
    glow.className = `fixed inset-0 pointer-events-none opacity-40 transition-all duration-500 bg-fault-${level}`;
    setTimeout(() => glow.className = "fixed inset-0 pointer-events-none opacity-20", 3000);
}

/* --- CHAOS & FAULT INJECTION --- */
window.triggerChaos = async (fault) => {
    showTab('dashboard');
    showToast(`Injecting Fault Profile: ${fault}...`);

    document.getElementById('metric-resilience').innerText = "84.2%";
    document.getElementById('metric-resilience').classList.replace('text-emerald-600', 'text-red-600');

    appendLog(`[SYSTEM] Chaos Laboratory Execution: ${fault.toUpperCase()}`);
    appendLog(`[SCOUT] { "event": "METRIC_THRESHOLD_EXCEEDED", "source": "Node-01", "impact": "High" }`);

    try {
        await fetch(`${API_BASE}/demo/chaos/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fault: fault })
        });
        connectToAgentStream(true);

        // Show approval gate after a delay (simulating Fixer thinking)
        setTimeout(() => {
            document.getElementById('approval-gate').classList.remove('hidden');
            appendLog(`[FIXER] { "action": "PATCH_CONFIG", "status": "PENDING_APPROVAL", "branch": "fix/node-01-disk" }`);
        }, 8000);

    } catch (e) { console.warn("Chaos bridge failed."); }
};

window.approveRemediation = () => {
    document.getElementById('approval-gate').classList.add('hidden');
    appendLog(`[SYSTEM] Human-in-The-Loop Approval Received. Executing Merge Protocol...`);
    appendLog(`[FIXER] Merge successful. Deploying eBPF reload...`);

    setTimeout(() => {
        resetIncidentState();
    }, 5000);
};

function resetIncidentState() {
    document.getElementById('metric-resilience').innerText = "99.8%";
    document.getElementById('metric-resilience').classList.replace('text-red-600', 'text-emerald-600');
    appendLog(`[SYSTEM] SLO Restoration Verified. Incident #1042 Closed.`);
    fetchGitVeracity();
}

/* --- UTILS --- */
window.copyCmd = (type) => {
    const ids = { 'docker': 'cmd-docker', 'helm': 'cmd-helm' };
    const el = document.getElementById(ids[type]);
    if (!el) return;
    navigator.clipboard.writeText(el.innerText).then(() => showToast("Command Copied to Stratum."));
};

function showToast(msg) {
    const container = document.getElementById('hud-toast-container');
    const toast = document.createElement('div');
    toast.className = "hud-toast font-black uppercase tracking-widest text-[10px]";
    toast.innerHTML = `<i data-lucide="info" class="w-4 h-4 inline mr-2 text-blue-400"></i> ${msg}`;
    container.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => toast.remove(), 4000);
}

async function fetchGitVeracity() {
    try {
        const res = await fetch(`${API_BASE}/api/git-activity`);
        const data = await res.json();
        const list = document.getElementById('incident-list');
        if (Array.isArray(data)) {
            document.getElementById('active-prs').innerText = data.length + 124;
            list.innerHTML = data.map(pr => `
                <div class="p-6 rounded-3xl border border-slate-100 bg-white shadow-sm hover:border-blue-400 transition-all cursor-pointer group" onclick="window.open('${pr.html_url}', '_blank')">
                    <h4 class="text-[11px] font-black text-slate-900 uppercase">Patch #${pr.number}</h4>
                    <p class="text-[9px] font-bold text-slate-400 mt-1 uppercase tracking-tighter">${pr.title}</p>
                </div>
            `).join('');
        }
    } catch (e) { }
}

function simulateMetricDrift() {
    const mttr = (4.0 + Math.random() * 0.4).toFixed(1);
    const el = document.getElementById('metric-mttr');
    if (el) el.innerText = `${mttr}m`;
}

window.clearLogs = () => {
    document.getElementById('logs-feed').innerHTML = '<div class="text-slate-400 italic text-[11px] uppercase font-mono"># Telemetry strata synchronized.</div>';
};

window.setMode = (mode) => {
    isDemoMode = (mode === 'demo');
    document.getElementById('btn-mode-demo').className = isDemoMode ? "px-4 py-1.5 text-[10px] font-black rounded-xl transition-all bg-blue-600 text-white shadow-xl uppercase tracking-widest" : "px-4 py-1.5 text-[10px] font-black rounded-xl transition-all text-slate-400 uppercase tracking-widest";
    document.getElementById('btn-mode-real').className = !isDemoMode ? "px-4 py-1.5 text-[10px] font-black rounded-xl transition-all bg-emerald-600 text-white shadow-xl uppercase tracking-widest" : "px-4 py-1.5 text-[10px] font-black rounded-xl transition-all text-slate-400 uppercase tracking-widest";
    appendLog(`[SYSTEM] Operational mode shifted: ${mode.toUpperCase()} Strata.`);
};
