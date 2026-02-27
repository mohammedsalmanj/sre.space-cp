/**
 * SRE Control Plane - Dashboard Application
 * Enterprise minimal UI logic
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';

// DOM Elements
const logsContainer = document.getElementById('logs-container');
const errorBanner = document.getElementById('error-banner');
const errorTitle = document.getElementById('error-title');
const errorMessage = document.getElementById('error-message');
const sseIndicator = document.getElementById('sse-indicator');
const globalStatusIndicator = document.getElementById('global-status-indicator');
const globalStatusText = document.getElementById('global-status-text');

// State
let eventSource = null;
let sseReconnectTimer = null;
let currentBackoff = 1000;
const MAX_BACKOFF = 30000;

// Global Error Handler
window.addEventListener("unhandledrejection", (event) => {
    showError('Unhandled Promise Rejection', event.reason?.message || 'Unknown error occurred in execution flow.');
});

window.addEventListener("error", (event) => {
    showError('UI Runtime Error', event.message || 'An unexpected error occurred.');
});

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    fetchSystemStatus();
    connectSSE();
});

// Display Error
function showError(title, message) {
    errorBanner.classList.remove('hidden');
    errorTitle.textContent = title;
    errorMessage.textContent = message;

    // Auto-hide after 10s if not persistent
    setTimeout(() => {
        errorBanner.classList.add('hidden');
    }, 10000);
}

// Fetch Initial Status
async function fetchSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();

        if (data.env_stack) {
            document.getElementById('provider-badge').textContent = data.env_stack.toUpperCase();
        }
    } catch (error) {
        showError('Backend Unreachable', 'Failed to fetch system status from Control Plane.');
        setStatusNominal(false);
    }
}

// Status Updates
function setStatusNominal(isNominal) {
    if (isNominal) {
        globalStatusIndicator.className = "w-2.5 h-2.5 rounded-full bg-green-400";
        globalStatusText.textContent = "NOMINAL";
        globalStatusText.className = "text-sm font-medium text-white uppercase tracking-wider";
    } else {
        globalStatusIndicator.className = "w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse";
        globalStatusText.textContent = "ANOMALY";
        globalStatusText.className = "text-sm font-bold text-red-200 uppercase tracking-wider";
    }
}

// SSE Connection (resilient)
function connectSSE(isAnomaly = false) {
    if (eventSource) {
        eventSource.close();
    }

    try {
        const url = `${API_BASE}/api/sre-loop?anomaly=${isAnomaly}`;
        eventSource = new EventSource(url);

        sseIndicator.textContent = "SSE CONNECTED";
        sseIndicator.className = "text-xs font-mono font-medium px-2 py-1 rounded bg-green-100 text-green-800 border border-green-200";
        currentBackoff = 1000; // Reset backoff on successful connect

        eventSource.onopen = () => {
            console.log("SSE Connection established");
            sseIndicator.textContent = "SSE LIVE";
            sseIndicator.className = "text-xs font-mono font-medium px-2 py-1 rounded bg-green-100 text-green-800 border border-green-200";
        };

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.message) {
                    appendLog(data.message);
                }

                if (data.final_state) {
                    setStatusNominal(data.final_state === 'Resolved' || data.final_state === 'Stable');
                }
            } catch (e) {
                console.warn('Failed to parse SSE message', e);
            }
        };

        eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            eventSource.close();

            sseIndicator.textContent = "SSE RECONNECTING";
            sseIndicator.className = "text-xs font-mono font-medium px-2 py-1 rounded bg-yellow-100 text-yellow-800 border border-yellow-200 animate-pulse";

            // Exponential backoff
            clearTimeout(sseReconnectTimer);
            sseReconnectTimer = setTimeout(() => {
                currentBackoff = Math.min(currentBackoff * 1.5, MAX_BACKOFF);
                connectSSE(false);
            }, currentBackoff);
        };

    } catch (e) {
        showError('SSE Init Failed', e.message);
    }
}

// Append logs with enterprise formatting
function appendLog(message) {
    const entry = document.createElement('div');
    entry.className = "py-1 border-b border-gray-100/50 last:border-0";

    // Format timestamp
    const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const timeSpan = `<span class="text-gray-400 mr-2">[${time}]</span>`;

    // Classify log type
    if (message.includes('[SCOUT]')) {
        entry.innerHTML = `${timeSpan}<span class="text-blue-600 font-semibold text-[11px] bg-blue-50 border border-blue-100 px-1 rounded mr-2">SCOUT</span> <span class="text-gray-700">${message.split('[SCOUT]')[1]}</span>`;
        pulseAgent('scout');
    } else if (message.includes('[BRAIN]')) {
        entry.innerHTML = `${timeSpan}<span class="text-indigo-600 font-semibold text-[11px] bg-indigo-50 border border-indigo-100 px-1 rounded mr-2">BRAIN</span> <span class="text-gray-700">${message.split('[BRAIN]')[1]}</span>`;
        pulseAgent('brain');
    } else if (message.includes('[FIXER]')) {
        entry.innerHTML = `${timeSpan}<span class="text-orange-600 font-semibold text-[11px] bg-orange-50 border border-orange-100 px-1 rounded mr-2">FIXER</span> <span class="text-gray-800 font-medium">${message.split('[FIXER]')[1]}</span>`;
        pulseAgent('fixer');
    } else if (message.includes('[ERROR]')) {
        entry.innerHTML = `${timeSpan}<span class="text-red-600 font-semibold text-[11px] bg-red-50 border border-red-100 px-1 rounded mr-2">ERROR</span> <span class="text-red-700">${message.replace('[ERROR]', '')}</span>`;
    } else if (message.includes('///')) {
        entry.innerHTML = `<div class="my-2 border-t border-gray-300"></div><span class="text-gray-500 font-bold text-xs tracking-wider">${message}</span>`;
    } else {
        entry.innerHTML = `${timeSpan}<span class="text-gray-600">${message}</span>`;
    }

    logsContainer.appendChild(entry);
    logsContainer.scrollTop = logsContainer.scrollHeight;
}

// Agent Indicator Pulsing
function pulseAgent(agent) {
    const dot = document.getElementById(`agent-${agent}-status`);
    if (!dot) return;

    const colors = { scout: 'bg-blue-400', brain: 'bg-indigo-400', fixer: 'bg-orange-400' };
    const shadow = { scout: 'shadow-[0_0_8px_rgba(96,165,250,0.8)]', brain: 'shadow-[0_0_8px_rgba(129,140,248,0.8)]', fixer: 'shadow-[0_0_8px_rgba(251,146,60,0.8)]' };

    const originalClass = dot.className;
    dot.className = `w-2 h-2 rounded-full ${colors[agent]} ${shadow[agent]} animate-ping`;

    setTimeout(() => {
        dot.className = `w-2 h-2 rounded-full bg-${agent === 'scout' ? 'blue' : agent === 'brain' ? 'indigo' : 'orange'}-500`;
    }, 1000);
}

// Exposed Functions
window.clearLogs = () => {
    logsContainer.innerHTML = '<div class="text-gray-400 italic mb-2">Logs cleared. Waiting for telemetry data...</div>';
};

window.triggerChaos = async (type) => {
    setStatusNominal(false);
    appendLog(`/// CHAOS INJECTION PROTOCOL: ${type} ///`);

    try {
        const response = await fetch(`${API_BASE}/demo/chaos/trigger`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fault: type })
        });

        if (!response.ok) {
            throw new Error(`Execution Failed (${response.status})`);
        }

        connectSSE(true); // Reconnect SSE emphasizing anomaly mode
    } catch (e) {
        showError('Chaos Injection Failed', `Could not trigger ${type}: ${e.message}`);
        appendLog(`[ERROR] Chaos injection failed endpoint connectivity lost.`);
    }
};
