/**
 * SRE.SPACE - Premium Intelligence Logic
 * Author: Mohammed Salman
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// State
let eventSource = null;
let currentBackoff = 1000;

document.addEventListener('DOMContentLoaded', () => {
    // Dynamic Social Links
    lucide.createIcons();

    // Auto-detect adapter mode
    const adapterBadge = document.getElementById('status-adapter-val');
    if (IS_LOCAL) {
        adapterBadge.innerText = 'LOCAL_SIM_RUNTIME';
        adapterBadge.classList.replace('text-blue-600', 'text-purple-600');
    }

    // Set About link dynamically
    const aboutLink = document.getElementById('about-link');
    if (aboutLink && API_BASE && API_BASE.startsWith('http')) {
        aboutLink.href = `${API_BASE}/about`;
    }

    // First visit initialization
    if (!sessionStorage.getItem('space_initialized')) {
        startInitialization();
    } else {
        connectSSE();
        fetchHealth();
    }
});

/* --- SPACE INITIALIZATION WIZARD --- */

window.startInitialization = () => {
    const wizard = document.getElementById('init-wizard');
    wizard.classList.remove('hidden');

    // Step 1 -> 2
    setTimeout(() => {
        document.getElementById('w-step-1').classList.add('hidden');
        document.getElementById('w-step-2').classList.remove('hidden');

        // Step 2 -> 3
        setTimeout(() => {
            document.getElementById('w-step-2').classList.add('hidden');
            document.getElementById('w-step-3').classList.remove('hidden');
        }, 1800);
    }, 1500);
};

window.finalizeInitialization = () => {
    sessionStorage.setItem('space_initialized', 'true');
    document.getElementById('init-wizard').classList.add('hidden');
    connectSSE();
    fetchHealth();
    appendLog("SYSTEM: Control link established. Neural strata synchronized.");
};

/* --- CORE AUTONOMIC LOOP --- */

function connectSSE(isAnomaly = false) {
    if (eventSource) eventSource.close();

    const indicator = document.getElementById('sse-indicator');
    const url = `${API_BASE}/api/sre-loop?anomaly=${isAnomaly}`;

    eventSource = new EventSource(url);

    eventSource.onopen = () => {
        indicator.innerText = "SSE: Connected";
        indicator.className = "text-[9px] font-black text-emerald-500 uppercase";
        currentBackoff = 1000;
    };

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.message) {
                appendLog(data.message);

                // Pulsing agent dots in the HUD
                if (data.agent) pulseAgent(data.agent);

                // Anomaly status tracking
                if (data.final_state === 'Resolved') setStatus('NOMINAL');
            }
        } catch (e) {
            console.error("Parse Error:", e);
        }
    };

    eventSource.onerror = () => {
        indicator.innerText = "SSE: Retrying...";
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
    const entry = document.createElement('div');
    entry.className = "animate-entrance";

    if (message.startsWith('REASONING:')) {
        const cleanMsg = message.replace('REASONING:', '').trim();
        entry.innerHTML = `<div class="reasoning-stream"><span class="font-bold text-blue-600 mr-2">THOUGHT</span> ${cleanMsg}</div>`;
    } else {
        const time = new Date().toLocaleTimeString('en-US', { hour12: false });
        // Style specific tags
        let formatted = message
            .replace(/\[SCOUT\]/g, '<span class="text-blue-600 font-bold">[SCOUT]</span>')
            .replace(/\[BRAIN\]/g, '<span class="text-purple-600 font-bold">[BRAIN]</span>')
            .replace(/\[FIXER\]/g, '<span class="text-orange-600 font-bold">[FIXER]</span>')
            .replace(/\[ERROR\]/g, '<span class="text-red-600 font-bold">[ERROR]</span>');

        entry.innerHTML = `<span class="opacity-30 mr-2">${time}</span> ${formatted}`;
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
        label.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span> ANOMALY DETECTED`;
    }
}

async function fetchHealth() {
    try {
        const res = await fetch(`${API_BASE}/api/health`);
        const data = await res.json();
        // Sync provider badge if it changed
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

        if (res.ok) {
            // Force SSE reconnect in anomaly mode
            connectSSE(true);
        }
    } catch (e) {
        appendLog(`[ERROR] Chaos injection failed. Check backend connectivity.`);
    }
};

window.clearLogs = () => {
    document.getElementById('logs').innerHTML = '<div class="text-slate-400 italic font-mono text-[10px]"># Terminal buffer cleared. Waiting for next OODA cycle...</div>';
};
