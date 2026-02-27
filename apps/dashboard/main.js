/**
 * SRE.SPACE - Premium Control Plane Logic
 * High-end Liquid Glass Visuals & OODA Lifecycle
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// DOM Elements
const logsContainer = document.getElementById('logs-container');
const sseIndicator = document.getElementById('sse-indicator');
const globalStatusIndicator = document.getElementById('global-status-indicator');
const globalStatusText = document.getElementById('global-status-text');
const initOverlay = document.getElementById('init-overlay');
const localInitButton = document.getElementById('local-init-button');

// State
let eventSource = null;
let currentBackoff = 1000;
const MAX_BACKOFF = 30000;

document.addEventListener('DOMContentLoaded', () => {
    // Show Local Controls if applicable
    if (IS_LOCAL) {
        if (localInitButton) localInitButton.classList.remove('hidden');
    }

    // Set Dynamic About Link
    const aboutLink = document.getElementById('about-link');
    if (aboutLink && API_BASE) {
        // If API_BASE is absolute (e.g. Render URL), point to its /about
        // Otherwise it stays relative for local use
        if (API_BASE.startsWith('http')) {
            aboutLink.href = `${API_BASE}/about`;
        }
    }

    startInitializationSequence();
});

/**
 * Step-by-Step Space Initialization
 */
async function startInitializationSequence() {
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const step3 = document.getElementById('step-3');
    const progress = document.getElementById('step-1-progress');
    const launchBtn = document.getElementById('launch-button');

    // Step 1: OTel Injection Simulation
    setTimeout(() => { progress.style.width = '100%'; }, 500);

    await new Promise(r => setTimeout(r, 2000));
    step1.classList.replace('step-active', 'step-hidden');
    step2.classList.replace('step-hidden', 'step-active');

    // Step 2: Establish Link
    if (IS_LOCAL) {
        document.getElementById('step-2-url').textContent = "Linking Registry to Brain Agent at localhost:8000...";
    }

    await new Promise(r => setTimeout(r, 1500));
    step2.classList.replace('step-active', 'step-hidden');
    step3.classList.replace('step-hidden', 'step-active');

    // Step 3: Launch
    launchBtn.addEventListener('click', () => {
        initOverlay.classList.add('opacity-0');
        setTimeout(() => {
            initOverlay.classList.add('hidden');
            initializeControlCycle();
        }, 700);
    });
}

/**
 * Core Control Loop Initialization
 */
async function initializeControlCycle() {
    appendLog("🚀 [SPACE_CORE] CALIBRATING NEURAL CHANNELS...");
    appendLog("🔭 [OBSERVER] ATTACHING TO PRODUCTION TELEMETRY STREAM...");

    fetchSystemStatus();
    connectSSE();
}

async function fetchSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();

        // Update UI based on stack
        if (data.env_stack) {
            const stackBadge = document.getElementById('provider-badge');
            stackBadge.textContent = data.env_stack.toUpperCase();

            // Icon transformation
            const stackIcon = document.getElementById('stack-icon');
            if (data.env_stack.toLowerCase() === 'ec2' || data.env_stack.toLowerCase() === 'aws') {
                stackIcon.setAttribute('data-lucide', 'server');
            } else if (data.env_stack.toLowerCase().includes('k8s') || data.env_stack.toLowerCase().includes('kubernetes')) {
                stackIcon.setAttribute('data-lucide', 'target');
            }
            if (window.lucide) lucide.createIcons();
        }

        if (data.has_pinecone) {
            document.getElementById('vector-db-badge').textContent = 'PINECONE_V3';
        } else {
            document.getElementById('vector-db-badge').textContent = 'CHROMADB_LOCAL';
        }

        appendLog(`🩺 [SYSTEM] BASELINE HEALTH: ${data.status.toUpperCase()} | MTTR_TARGET: < 60S`);
    } catch (error) {
        console.error('Status fetch failed', error);
        appendLog(`[ERROR] INFRASTRUCTURE ADAPTER HANDSHAKE FAILED.`);
    }
}

function connectSSE(isAnomaly = false) {
    if (eventSource) eventSource.close();

    const url = `${API_BASE}/api/sre-loop?anomaly=${isAnomaly}`;
    eventSource = new EventSource(url);

    eventSource.onopen = () => {
        sseIndicator.textContent = "SSE LIVE";
        sseIndicator.className = "text-[9px] font-mono font-bold px-3 py-1 rounded-full bg-green-500/20 text-green-400 border border-green-500/30 uppercase tracking-widest";
    };

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.message) {
                appendLog(data.message);
            }
            if (data.final_state) {
                setStatusState(data.final_state === 'Resolved' || data.final_state === 'Stable');
            }
        } catch (e) {
            console.warn('Malformed SSE', e);
        }
    };

    eventSource.onerror = () => {
        sseIndicator.textContent = "SIGNAL DROP";
        sseIndicator.className = "text-[9px] font-mono font-bold px-3 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 uppercase tracking-widest animate-pulse";
        eventSource.close();
        setTimeout(() => connectSSE(false), 5000);
    };
}

function appendLog(message) {
    const entry = document.createElement('div');
    entry.className = "py-1 opacity-0 animate-slide-up";

    const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const timeFull = `<span class="text-slate-600 mr-2 text-[10px]">[${time}]</span>`;

    if (message.includes('[SCOUT]')) {
        entry.innerHTML = `${timeFull}<span class="text-[#00D1FF] font-bold">[SCOUT]</span> <span class="text-slate-400">${message.split('[SCOUT]')[1]}</span>`;
        pulseAgent('scout');
    } else if (message.includes('[BRAIN]')) {
        entry.innerHTML = `${timeFull}<span class="text-indigo-400 font-bold">[BRAIN]</span> <span class="bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-400/20 text-slate-300 font-medium">${message.split('[BRAIN]')[1]}</span>`;
        pulseAgent('brain');
    } else if (message.includes('[FIXER]')) {
        entry.innerHTML = `${timeFull}<span class="text-green-400 font-bold">[FIXER]</span> <span class="text-white font-medium italic">${message.split('[FIXER]')[1]}</span>`;
        pulseAgent('fixer');
    } else if (message.includes('[ERROR]')) {
        entry.innerHTML = `${timeFull}<span class="text-red-500 font-bold uppercase">[FAULT_TRIP]</span> <span class="text-red-400">${message.replace('[ERROR]', '')}</span>`;
    } else if (message.includes('REASONING:')) {
        entry.className += " reasoning-stream";
        entry.innerHTML = `<span class="text-[10px] text-blue-300 font-bold uppercase tracking-tighter">AI_REASONING &gt;&gt;</span> <span class="italic text-slate-300">${message.replace('REASONING:', '')}</span>`;
    } else {
        entry.innerHTML = `${timeFull}<span class="text-slate-500 italic">${message}</span>`;
    }

    logsContainer.appendChild(entry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

function pulseAgent(agent) {
    const dot = document.getElementById(`agent-${agent}-status`);
    if (!dot) return;
    dot.classList.add('animate-ping', 'ring-2', 'ring-white/20');
    setTimeout(() => dot.classList.remove('animate-ping', 'ring-2', 'ring-white/20'), 1500);
}

function setStatusState(isNominal) {
    globalStatusIndicator.className = isNominal ?
        "w-2 h-2 rounded-full bg-green-400 animate-pulse status-glow-green" :
        "w-2 h-2 rounded-full bg-red-500 animate-ping shadow-[0_0_15px_rgba(239,68,68,0.8)]";
    globalStatusText.textContent = isNominal ? "NOMINAL_STATE" : "CRITICAL_ANOMALY";
    globalStatusText.className = isNominal ?
        "text-[10px] font-bold text-slate-300 uppercase tracking-widest" :
        "text-[10px] font-black text-red-500 uppercase tracking-[0.2em]";
}

window.clearLogs = () => {
    logsContainer.innerHTML = '<div class="text-slate-600 italic">Logs purged. Synchronizing neural shards...</div>';
};

window.triggerChaos = async (type) => {
    setStatusState(false);
    appendLog(`[PROTOCOL_X] TRIGGERING VECTOR: ${type}`);
    try {
        const res = await fetch(`${API_BASE}/demo/chaos/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fault: type })
        });
        if (!res.ok) throw new Error(`${res.status}`);
        connectSSE(true);
    } catch (e) {
        appendLog(`[ERROR] FAULT INJECTION DEGRADED: ${e.message}`);
    }
};

