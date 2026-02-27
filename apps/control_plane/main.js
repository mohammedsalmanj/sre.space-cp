/**
 * SRE.SPACE - Premium Intelligence Logic
 * Author: Mohammed Salman
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// State
let eventSource = null;
let currentBackoff = 1000;
let isDemoMode = true;
let selectedDeploy = 'aws';
let currentTourStep = 0;

// On Load
document.addEventListener('DOMContentLoaded', () => {
    // Dynamic Branding
    const aboutLink = document.getElementById('about-link');
    if (aboutLink && API_BASE && API_BASE.startsWith('http')) {
        aboutLink.href = `${API_BASE}/about`;
    }

    // Determine Mode
    if (IS_LOCAL) {
        document.getElementById('badge-local').classList.remove('hidden');
    }

    // Start Premium Sync Sequence (Optional, but user liked it)
    // We only show it if first visit in session
    if (!sessionStorage.getItem('init_complete')) {
        startInitializationSequence();
    } else {
        connectSSE();
        fetchSystemStatus();
    }

    lucide.createIcons();
});

/* --- INITIALIZATION OVERLAY LOGIC --- */
function startInitializationSequence() {
    const overlay = document.getElementById('initialization-overlay');
    overlay.classList.remove('hidden');

    setTimeout(() => {
        document.getElementById('init-step-1').classList.replace('step-active', 'step-hidden');
        document.getElementById('init-step-2').classList.replace('step-hidden', 'step-active');

        setTimeout(() => {
            document.getElementById('init-step-2').classList.replace('step-active', 'step-hidden');
            document.getElementById('init-step-3').classList.replace('step-hidden', 'step-active');
        }, 1800);
    }, 1500);
}

window.finalizeInit = () => {
    sessionStorage.setItem('init_complete', 'true');
    document.getElementById('initialization-overlay').classList.add('hidden');
    connectSSE();
    fetchSystemStatus();
    appendLog("SYSTEM: Neural architecture synchronized. Control link stable.");
};

/* --- CORE CONTROL PLANE LOGIC --- */

async function fetchSystemStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        if (data.env_stack) {
            updateProviderBadge(data.env_stack);
        }
    } catch (e) {
        console.warn("Health check failed", e);
    }
}

function updateProviderBadge(stack) {
    const badge = document.getElementById('status-adapter-val');
    if (badge) badge.innerText = stack.toUpperCase();
}

// SSE Connection
function connectSSE(isAnomaly = false) {
    if (eventSource) eventSource.close();

    const url = `${API_BASE}/api/sre-loop?anomaly=${isAnomaly}`;
    eventSource = new EventSource(url);

    const indicator = document.getElementById('sse-indicator');

    eventSource.onopen = () => {
        indicator.innerText = "SSE: LIVE";
        indicator.classList.add('text-cyan-400');
        currentBackoff = 1000;
    };

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.message) appendLog(data.message);
        if (data.agent) pulseAgent(data.agent);
    };

    eventSource.onerror = () => {
        indicator.innerText = "SSE: RETRYING";
        eventSource.close();
        setTimeout(connectSSE, currentBackoff);
        currentBackoff = Math.min(currentBackoff * 1.5, 30000);
    };
}

function appendLog(message) {
    const logs = document.getElementById('logs');
    const entry = document.createElement('div');
    entry.className = "log-entry";

    if (message.startsWith('REASONING:')) {
        entry.className += " reasoning-stream";
        entry.innerHTML = `<span class="opacity-70">${message.replace('REASONING:', '')}</span>`;
    } else {
        const time = new Date().toLocaleTimeString('en-US', { hour12: false });
        entry.innerHTML = `<span class="opacity-40 text-[9px] mr-2">[${time}]</span> ${message}`;
    }

    logs.appendChild(entry);
    logs.scrollTop = logs.scrollHeight;
}

function pulseAgent(agent) {
    const dot = document.getElementById(`agent-${agent}-status`);
    if (dot) {
        dot.classList.add('animate-ping', 'shadow-[0_0_10px_#fff]');
        setTimeout(() => dot.classList.remove('animate-ping', 'shadow-[0_0_10px_#fff]'), 1000);
    }
}

window.clearLogs = () => {
    document.getElementById('logs').innerHTML = '<div class="text-slate-600 italic">... Terminal Recalibrated ...</div>';
};

window.triggerChaos = async (type) => {
    appendLog(`CRITICAL: INJECTING CHAOS VECTOR [${type}]`);
    try {
        await fetch(`${API_BASE}/demo/chaos/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fault: type })
        });
        connectSSE(true);
    } catch (e) {
        appendLog(`ERROR: Chaos injection failed: ${e.message}`);
    }
};

/* --- DEPLOIMENT WIZARD LOGIC (RESTORED) --- */

window.deployControlPlane = () => {
    document.getElementById('deploy-overlay').classList.remove('hidden');
    goToStep(1);
};

window.closeDeploy = () => {
    document.getElementById('deploy-overlay').classList.add('hidden');
};

window.goToStep = (step) => {
    [1, 2, 3, 4].forEach(s => {
        const el = document.getElementById(`wizard-step-${s}`);
        if (el) el.classList.add('hidden');
    });
    document.getElementById(`wizard-step-${step}`).classList.remove('hidden');

    if (step > 1) {
        const prog = document.getElementById(`prog-${step}`);
        if (prog) prog.classList.add('text-cyan-400', 'bg-cyan-500/20', 'px-2', 'py-1', 'rounded', 'border', 'border-cyan-500/40');
    }

    if (step === 2) {
        ['aws', 'gcp', 'docker'].forEach(p => document.getElementById(`setup-instructions-${p}`).classList.add('hidden'));
        document.getElementById(`setup-instructions-${selectedDeploy}`).classList.remove('hidden');
    }
    if (step === 3) {
        ['aws', 'gcp', 'docker'].forEach(p => document.getElementById(`infra-${p}`).classList.add('hidden'));
        document.getElementById(`infra-${selectedDeploy}`).classList.remove('hidden');
    }
};

window.selectDeploy = (platform) => {
    selectedDeploy = platform;
    ['aws', 'gcp', 'docker'].forEach(p => {
        const el = document.getElementById(`dep-${p}`);
        if (p === platform) {
            el.className = "p-5 border border-cyan-500 bg-cyan-500/10 rounded-xl cursor-pointer transition-all flex items-center justify-between group";
        } else {
            el.className = "p-5 border border-white/10 bg-white/5 hover:border-cyan-500/50 hover:bg-white/10 rounded-xl cursor-pointer transition-all flex items-center justify-between group";
        }
    });
};

window.validateCredentials = async () => {
    const btn = document.getElementById('btn-validate');
    btn.innerText = "AUTHENTICATING...";
    await new Promise(r => setTimeout(r, 1500));
    btn.innerText = "VALIDATED ✔";
    btn.classList.add('bg-green-600');
    setTimeout(() => {
        btn.classList.remove('bg-green-600');
        btn.innerText = "VALIDATE";
        goToStep(3);
    }, 1000);
};

window.executeProvisioning = async () => {
    const btn = document.getElementById('btn-provision');
    btn.innerText = "PROVISIONING...";
    await new Promise(r => setTimeout(r, 2000));
    goToStep(4);
};

window.switchToOperationalMode = () => {
    closeDeploy();
    appendLog("SYSTEM: Operational phase initiated. Real-mode sensors active.");
};

/* --- GUIDED TOUR --- */
const tourSteps = [
    { icon: '🔭', title: 'Phase 1: Scout', desc: 'Observe layer. OpenTelemetry Intake.' },
    { icon: '🧠', title: 'Phase 2: Brain', desc: 'Orient layer. LLM-driven RCA.' },
    { icon: '🛠️', title: 'Phase 3: Fixer', desc: 'Act layer. GitOps Remediation.' }
];

window.startTour = () => {
    currentTourStep = 0;
    document.getElementById('tour-overlay').classList.remove('hidden');
    updateTourUI();
};

window.closeTour = () => document.getElementById('tour-overlay').classList.add('hidden');

window.nextTour = () => {
    currentTourStep++;
    if (currentTourStep >= tourSteps.length) closeTour();
    else updateTourUI();
};

function updateTourUI() {
    const step = tourSteps[currentTourStep];
    document.getElementById('tour-icon').innerText = step.icon;
    document.getElementById('tour-title').innerText = step.title;
    document.getElementById('tour-desc').innerText = step.desc;
}

window.updateProvider = (val) => {
    selectedDeploy = val;
    appendLog(`SYSTEM: Switched target environment to ${val.toUpperCase()}`);
    if (val === 'local') {
        document.getElementById('badge-local').classList.remove('hidden');
        document.getElementById('badge-cloud').classList.add('hidden');
    } else {
        document.getElementById('badge-local').classList.add('hidden');
        document.getElementById('badge-cloud').classList.remove('hidden');
    }
};
