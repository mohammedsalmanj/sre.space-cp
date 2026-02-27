/**
 * SRE.SPACE - Enterprise Orchestration v6.5
 * Author: Mohammed Salman
 * Logic: 5-Step Guarded Wizard + Real-Time Telemetry Strata
 */

const API_BASE = import.meta.env?.VITE_API_BASE || '';
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// --- Global State ---
let wizardState = {
    step: 1,
    provider: 'aws',
    stack: 'ec2',
    credentials: {},
    isValidated: false
};

let telemetryStream = null;
let oodaStream = null;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    initializeTelemetry();
    connectOODAStream(false);
});

// --- Tab Controller ---
window.showTab = (tabId) => {
    ['dashboard', 'provisioning', 'governance'].forEach(id => {
        const el = document.getElementById(`content-${id}`);
        const tab = document.getElementById(`tab-${id}`);
        if (!el || !tab) return;

        if (id === tabId) {
            el.classList.remove('hidden');
            tab.className = "pb-4 text-[11px] font-black tracking-[0.3em] border-b-2 border-blue-600 text-slate-900 uppercase";
        } else {
            el.classList.add('hidden');
            tab.className = "pb-4 text-[11px] font-black tracking-[0.3em] border-b-2 border-transparent text-slate-400 hover:text-slate-900 uppercase transition-all";
        }
    });

    if (tabId === 'dashboard') initializeTelemetry();
};

// --- Wizard Navigation ---
window.goToStep = (step) => {
    if (step > wizardState.step && !wizardState.isValidated && wizardState.step === 2) {
        alert("SECURITY GATE: Complete credential validation before proceeding.");
        return;
    }

    // UI Transitions
    for (let i = 1; i <= 5; i++) {
        const pane = document.getElementById(`wizard-step-${i}`);
        const node = document.getElementById(`step-node-${i}`);
        if (!pane || !node) continue;

        if (i === step) {
            pane.classList.remove('hidden');
            node.className = "w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center font-black relative z-10 cursor-pointer shadow-lg shadow-blue-500/30 transition-all";
        } else {
            pane.classList.add('hidden');
            if (i < step) {
                node.className = "w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center font-black relative z-10 cursor-pointer transition-all";
            } else {
                node.className = "w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center font-black relative z-10 transition-all";
            }
        }
    }

    // Update progress line
    const progressMap = { 1: '0%', 2: '25%', 3: '50%', 4: '75%', 5: '100%' };
    document.getElementById('wizard-line').style.width = progressMap[step];

    wizardState.step = step;
    lucide.createIcons();
};

// --- STEP 1: Provider Selection ---
window.selectProvider = (provider) => {
    wizardState.provider = provider;
    ['aws', 'gcp', 'kubernetes', 'local'].forEach(p => {
        const card = document.getElementById(`prov-card-${p}`);
        if (p === provider) {
            card.classList.add('border-blue-600', 'bg-blue-50/50', 'ring-4', 'ring-blue-500/10');
        } else {
            card.classList.remove('border-blue-600', 'bg-blue-50/50', 'ring-4', 'ring-blue-500/10');
        }
    });

    // Toggle field visibility for Step 2
    document.getElementById('fields-aws').classList.toggle('hidden', provider !== 'aws');
    document.getElementById('fields-gcp').classList.toggle('hidden', provider !== 'gcp');

    // Auto-proceed to credentials except for sandbox
    if (provider === 'local') {
        wizardState.isValidated = true;
        goToStep(3);
    } else {
        goToStep(2);
    }
};

// --- STEP 2: Credential Validation (Gated) ---
window.handleGCPUpload = (input) => {
    const file = input.files[0];
    if (file) {
        document.getElementById('gcp-json-text').innerText = `IDENTIFIED: ${file.name}`;
        const reader = new FileReader();
        reader.onload = (e) => {
            wizardState.credentials = { jsonKey: e.target.result };
        };
        reader.readAsText(file);
    }
};

window.validateStep2 = async () => {
    const btn = document.getElementById('btn-validate-creds');
    const status = document.getElementById('validate-status');
    btn.disabled = true;
    btn.innerText = "VERIFYING SECURITY TOKENS...";
    status.innerText = "";

    try {
        let endpoint = `${API_BASE}/api/v1/validate/${wizardState.provider}`;
        let payload = {};

        if (wizardState.provider === 'aws') {
            payload = {
                accessKey: document.getElementById('aws-ak').value,
                secretKey: document.getElementById('aws-sk').value,
                region: document.getElementById('aws-region').value
            };
            wizardState.credentials = payload;
        } else {
            payload = wizardState.credentials;
        }

        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.status === 'success') {
            btn.className = "w-full py-5 bg-emerald-600 text-white rounded-2xl font-black uppercase tracking-widest";
            btn.innerText = "CREDENTIAL VALIDATION: SUCCESS";
            status.innerHTML = `<span class="text-emerald-600">AUTH GRANTED: ${data.account || data.project_id}</span>`;
            wizardState.isValidated = true;

            // Sync summary
            document.getElementById('sum-provider').innerText = wizardState.provider.toUpperCase();
            if (wizardState.provider === 'aws') document.getElementById('sum-region').innerText = payload.region;

            setTimeout(() => goToStep(3), 1500);
        } else {
            btn.disabled = false;
            btn.innerText = "VALIDATION FAILED - RETRY";
            status.innerHTML = `<span class="text-red-500">${data.message}</span>`;
        }
    } catch (e) {
        btn.disabled = false;
        btn.innerText = "SYSTEM ERROR - SEC-CORE UNREACHABLE";
    }
};

// --- STEP 3: Stack Selection ---
window.selectStack = (stack) => {
    if (stack !== 'ec2') return; // Enterprise locked
    wizardState.stack = stack;
    appendLog(`[SYSTEM] Architecture profile locked: ${stack.toUpperCase()}`);
};

// --- STEP 5: Live Execution Stream ---
window.startProvisioning = () => {
    goToStep(5);
    const logContainer = document.getElementById('provision-logs');
    const progressBar = document.getElementById('provision-bar');
    const progressLabel = document.getElementById('provision-status-label');
    const progressPercent = document.getElementById('provision-percent');

    logContainer.innerHTML = `<div class="text-blue-400"># Synthesis Engine Initiated...</div>`;

    const source = new EventSource(`${API_BASE}/api/v1/provision/execute?provider=${wizardState.provider}&stack=${wizardState.stack}`);

    source.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.message) {
            const div = document.createElement('div');
            div.innerText = `> ${data.message}`;
            logContainer.appendChild(div);
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        if (data.status) {
            progressLabel.innerText = data.status;
            if (data.progress) {
                progressBar.style.width = `${data.progress}%`;
                progressPercent.innerText = `${Math.round(data.progress)}%`;
            }
        }

        if (data.final) {
            source.close();
            document.getElementById('provision-success-actions').classList.remove('hidden');
            // Persist stack type
            fetch(`${API_BASE}/api/config/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ STACK_TYPE: wizardState.provider })
            });
        }
    };

    source.onerror = () => {
        const div = document.createElement('div');
        div.className = "text-red-500 font-bold";
        div.innerText = "!! CRITICAL FAILURE: SYNTHESIS CHAIN BROKEN. INITIATING AUTO-ROLLBACK.";
        logContainer.appendChild(div);
        source.close();
    };
};

// --- Real-Time Telemetry Management ---
function initializeTelemetry() {
    if (telemetryStream) telemetryStream.close();

    const cpuEl = document.getElementById('telemetry-cpu');
    const cpuBar = document.getElementById('telemetry-cpu-bar');
    const memEl = document.getElementById('telemetry-mem');
    const memBar = document.getElementById('telemetry-mem-bar');
    const diskEl = document.getElementById('telemetry-disk');
    const diskBar = document.getElementById('telemetry-disk-bar');

    telemetryStream = new EventSource(`${API_BASE}/api/v1/telemetry/stream`);

    telemetryStream.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (cpuEl) {
            cpuEl.innerText = `${data.cpu}%`;
            cpuBar.style.width = `${data.cpu}%`;
            cpuEl.className = data.cpu > 80 ? "text-5xl font-black text-red-600 mt-3 font-mono" : "text-5xl font-black text-slate-900 mt-3 font-mono";
        }
        if (memEl) {
            memEl.innerText = `${data.memory}%`;
            memBar.style.width = `${data.memory}%`;
        }
        if (diskEl) {
            diskEl.innerText = `${data.disk}%`;
            diskBar.style.width = `${data.disk}%`;
        }
    };
}

// --- OODA Neural Stream (SSE) ---
function connectOODAStream(isAnomaly = false) {
    if (oodaStream) oodaStream.close();

    const url = `${API_BASE}/api/sre-loop?anomaly=${isAnomaly}&simulation=true`;
    oodaStream = new EventSource(url);

    oodaStream.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.message) appendLog(data.message);
    };
}

window.appendLog = (message) => {
    const container = document.getElementById('logs-feed');
    if (!container) return;

    const div = document.createElement('div');
    div.className = "animate-entrance border-l-2 border-slate-200 pl-4 py-1";

    let formatted = message
        .replace(/\[SCOUT\]/g, '<span class="text-blue-600 font-bold">[SCOUT]</span>')
        .replace(/\[BRAIN\]/g, '<span class="text-purple-600 font-bold">[BRAIN]</span>')
        .replace(/\[FIXER\]/g, '<span class="text-orange-600 font-bold">[FIXER]</span>')
        .replace(/\[ERROR\]/g, '<span class="text-red-600 font-bold">[ERROR]</span>');

    div.innerHTML = `<span class="opacity-30 mr-3 text-[9px] font-mono">${new Date().toLocaleTimeString()}</span> ${formatted}`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
};

window.triggerChaos = () => {
    const fault = 'AWS_EC2_DISK_FULL';
    appendLog(`[SYSTEM] Chaos profile injected: ${fault}`);
    showTab('dashboard');
    connectOODAStream(true);
};

window.clearLogs = () => {
    document.getElementById('logs-feed').innerHTML = '<div class="text-slate-400 italic"># Telemetry strata synchronized.</div>';
};
