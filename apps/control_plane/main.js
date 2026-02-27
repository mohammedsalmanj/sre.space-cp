/**
 * SRE.SPACE - Premium Intelligence Logic
 * Author: Mohammed Salman
 * Logic: Restored Max-Content Wizard with Provider/Sub-Stack Awareness
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// State Management
let eventSource = null;
let currentBackoff = 1000;
let selectedProvider = 'local';
let selectedSubStack = null;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    // 1. Fix About Link (Redirect to Backend Render instance to avoid Vercel 404)
    const aboutLink = document.getElementById('about-link');
    if (aboutLink) {
        if (API_BASE && API_BASE.startsWith('http')) {
            aboutLink.href = `${API_BASE}/about`;
        } else {
            // Fallback for relative dev environments
            aboutLink.href = '/about';
        }
    }

    // 2. Launch Control Plane Initialization Immediately
    // If not specifically flagged as done in this session, show it.
    if (!sessionStorage.getItem('space_initialized')) {
        startInitialization();
    } else {
        // Recover state from previous initialization
        const savedProvider = sessionStorage.getItem('active_provider') || 'local';
        selectProvider(savedProvider);
        connectSSE();
        fetchHealth();
    }
});

/* --- WIZARD LOGIC (RESTORED INTERACTIVITY) --- */

window.startInitialization = () => {
    const wizard = document.getElementById('init-wizard');
    wizard.classList.remove('hidden');
    // Ensure we start at Step 0 (Target Selection)
    goToWizardStep(0);
};

window.selectProvider = (provider) => {
    selectedProvider = provider;
    sessionStorage.setItem('active_provider', provider);

    // Header Icon Highlights
    const icons = { aws: 'icon-aws', gcp: 'icon-gcp', k8s: 'icon-k8s', local: 'icon-docker' };
    Object.values(icons).forEach(id => document.getElementById(id).classList.remove('tech-icon-active'));
    document.getElementById(icons[provider]).classList.add('tech-icon-active');

    // UI Feedback for buttons
    document.querySelectorAll('.provider-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`btn-${provider}`).classList.add('active');

    // Show sub-stacks if needed
    const subPanel = document.getElementById('sub-stacks-panel');
    const awsSub = document.getElementById('aws-sub-stacks');
    const gcpSub = document.getElementById('gcp-sub-stacks');

    subPanel.classList.add('hidden');
    awsSub.classList.add('hidden');
    gcpSub.classList.add('hidden');

    if (provider === 'aws') {
        subPanel.classList.remove('hidden');
        awsSub.classList.remove('hidden');
    } else if (provider === 'gcp') {
        subPanel.classList.remove('hidden');
        gcpSub.classList.remove('hidden');
    }

    // Update operational context badge
    const adapterBadge = document.getElementById('status-adapter-val');
    adapterBadge.innerText = provider.toUpperCase() + '_MODE';
};

window.selectSubStack = (sub) => {
    selectedSubStack = sub;
    // Visually mark active sub-stack
    document.querySelectorAll('.sub-stack-btn').forEach(btn => {
        if (btn.innerText.toLowerCase().includes(sub)) btn.classList.add('active');
        else if (!btn.classList.contains('provider-btn')) btn.classList.remove('active');
    });
    appendLog(`[SYSTEM] Target Sub-Stack Profile: ${sub.toUpperCase()}`);
};

window.goToWizardStep = (step) => {
    const steps = ['w-step-0', 'w-step-1', 'w-step-2', 'w-step-3'];
    steps.forEach((s, i) => {
        const el = document.getElementById(s);
        if (i === step) el.classList.remove('hidden');
        else el.classList.add('hidden');
    });

    // Auto-advance Step 1 (Omit credentials if local for speed)
    if (step === 1) {
        setTimeout(() => {
            goToWizardStep(2);
        }, 1500);
    }
};

window.finalizeInitialization = () => {
    sessionStorage.setItem('space_initialized', 'true');
    document.getElementById('init-wizard').classList.add('hidden');

    // Push config to backend optionally
    saveConfig(selectedProvider, selectedSubStack);

    connectSSE();
    fetchHealth();
    appendLog("SYSTEM: Autonomic Control Link Established. SRE Loop Syncing...");
};

async function saveConfig(stack, sub) {
    try {
        await fetch(`${API_BASE}/api/config/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ STACK_TYPE: stack, SUB_STACK: sub })
        });
    } catch (e) {
        console.warn("Config save failed", e);
    }
}

/* --- CORE AUTONOMIC LOOP --- */

function connectSSE(isAnomaly = false) {
    if (eventSource) eventSource.close();

    const indicator = document.getElementById('sse-indicator');
    const url = `${API_BASE}/api/sre-loop?anomaly=${isAnomaly}`;

    eventSource = new EventSource(url);

    eventSource.onopen = () => {
        indicator.innerText = "SSE: LIVE_LINK";
        indicator.className = "text-[9px] font-black text-emerald-500 uppercase";
        currentBackoff = 1000;
    };

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.message) {
                appendLog(data.message);
                if (data.agent) pulseAgent(data.agent);
                if (data.final_state === 'Resolved') setStatus('NOMINAL');
            }
        } catch (e) { console.error(e); }
    };

    eventSource.onerror = () => {
        indicator.innerText = "SSE: OFFLINE_RETRY";
        indicator.className = "text-[9px] font-black text-amber-500 uppercase";
        eventSource.close();
        setTimeout(() => {
            currentBackoff = Math.min(currentBackoff * 1.5, 30000);
            connectSSE(false);
        }, currentBackoff);
    };
}

function appendLog(message) {
    const container = document.getElementById('logs');
    if (!container) return;
    const entry = document.createElement('div');
    entry.className = "animate-entrance";

    if (message.startsWith('REASONING:')) {
        const cleanMsg = message.replace('REASONING:', '').trim();
        entry.innerHTML = `<div class="reasoning-stream"><span class="font-bold text-blue-600 mr-2">LOGIC</span> ${cleanMsg}</div>`;
    } else {
        const time = new Date().toLocaleTimeString('en-US', { hour12: false });
        let formatted = message
            .replace(/\[SCOUT\]/g, '<span class="text-blue-600 font-bold">[SCOUT]</span>')
            .replace(/\[BRAIN\]/g, '<span class="text-purple-600 font-bold">[BRAIN]</span>')
            .replace(/\[FIXER\]/g, '<span class="text-orange-600 font-bold">[FIXER]</span>')
            .replace(/\[ERROR\]/g, '<span class="text-red-600 font-bold">[ERROR]</span>');
        entry.innerHTML = `<span class="opacity-20 mr-2 text-[9px] font-mono">${time}</span> ${formatted}`;
    }

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function pulseAgent(agent) {
    const dot = document.getElementById(`agent-${agent.toLowerCase()}-status`);
    if (dot) {
        dot.classList.add('animate-ping', 'bg-blue-300');
        setTimeout(() => dot.classList.remove('animate-ping', 'bg-blue-300'), 1000);
    }
}

function setStatus(status) {
    const label = document.getElementById('sys-status-label');
    if (status === 'NOMINAL') {
        label.className = "status-badge badge-active flex items-center gap-1.5";
        label.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 pulse-emerald"></span> NOMINAL`;
    } else {
        label.className = "status-badge bg-red-50 text-red-600 border border-red-100 flex items-center gap-1.5";
        label.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span> ANOMALY`;
    }
}

async function fetchHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        if (data.env_stack) {
            document.getElementById('status-adapter-val').innerText = data.env_stack.toUpperCase();
        }
    } catch (e) {
        console.warn("Health sync failed");
    }
}

window.triggerChaos = async (fault) => {
    setStatus('ANOMALY');
    appendLog(`[SYSTEM] Manual chaos injection requested: ${fault}`);
    try {
        const res = await fetch(`${API_BASE}/demo/chaos/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fault: fault })
        });
        if (res.ok) connectSSE(true);
    } catch (e) {
        appendLog(`[ERROR] Chaos injection failed. Check backend connectivity.`);
    }
};

window.clearLogs = () => {
    document.getElementById('logs').innerHTML = '<div class="text-slate-400 italic font-mono text-[10px]"># Terminal buffer cleared. Waiting for OODA sync...</div>';
};
