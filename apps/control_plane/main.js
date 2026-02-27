/**
 * SRE.SPACE | Cognitive Reliability Engine v6.0
 * Logic for Real-Time OODA Progress, Vector Memory, and Stratum Onboarding
 */

let currentSSE = null;
let currentProvider = 'local';
const TERMINAL_STORAGE_KEY = 'sre_terminal_logs';

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    loadTerminalFromStorage();
    connectSRELoop();
});

/* --- UI CONTROLS --- */
window.toggleDrawer = () => {
    document.getElementById('onboarding-drawer').classList.toggle('collapsed');
};

/* --- WIZARD LOGIC --- */
window.setProvider = (provider) => {
    currentProvider = provider;
    document.getElementById('step-dot-1').className = 'w-2 h-2 rounded-full bg-emerald-500';
    gotoStep(2);

    // Toggle input visibility
    document.getElementById('inputs-aws').classList.toggle('hidden', provider !== 'aws');
    document.getElementById('inputs-local').classList.toggle('hidden', provider !== 'local');
};

window.gotoStep = (step) => {
    for (let i = 1; i <= 4; i++) {
        const el = document.getElementById(`wizard-step-${i}`);
        if (el) el.classList.add('hidden');
        const dot = document.getElementById(`step-dot-${i}`);
        if (dot) dot.className = i < step ? 'w-2 h-2 rounded-full bg-emerald-500' : (i === step ? 'w-2 h-2 rounded-full bg-blue-600' : 'w-2 h-2 rounded-full bg-slate-200');
    }
    document.getElementById(`wizard-step-${step}`).classList.remove('hidden');
};

window.validateWizard = async () => {
    gotoStep(3);
    const spinner = document.getElementById('validating-spinner');
    const success = document.getElementById('validation-success');
    const error = document.getElementById('validation-error');

    spinner.classList.remove('hidden');
    success.classList.add('hidden');
    error.classList.add('hidden');

    try {
        if (currentProvider === 'local') {
            await new Promise(r => setTimeout(r, 800));
            showValidationSuccess("LOCAL_SANDBOX_STABLE");
        } else if (currentProvider === 'aws') {
            const ak = document.getElementById('aws-ak').value;
            const sk = document.getElementById('aws-sk').value;

            const res = await fetch('/api/v1/validate/aws', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accessKey: ak, secretKey: sk })
            });
            const data = await res.json();

            if (data.status === 'success') {
                showValidationSuccess(data.arn || data.account);
            } else {
                showValidationError(data.message);
            }
        } else {
            // Placeholder for K8S/GCP
            await new Promise(r => setTimeout(r, 1000));
            showValidationSuccess("K8S_NATIVE_CLUSTER");
        }
    } catch (err) {
        showValidationError("Network correlation failure.");
    }
};

function showValidationSuccess(identity) {
    document.getElementById('validating-spinner').classList.add('hidden');
    document.getElementById('validation-success').classList.remove('hidden');
    document.getElementById('auth-identity').innerText = identity;
}

function showValidationError(msg) {
    document.getElementById('validating-spinner').classList.add('hidden');
    const errorDiv = document.getElementById('validation-error');
    errorDiv.classList.remove('hidden');
    document.getElementById('error-message').innerText = msg;
}

window.finalizeWizard = () => {
    toggleDrawer();
    showToast(`Enterprise Mode Activated: ${currentProvider.toUpperCase()}`);
    addLog(`SYSTEM: Handover complete. ${currentProvider.toUpperCase()} Strata is now monitored.`, "SYSTEM");
};

window.copyCode = () => {
    const text = document.getElementById('deployment-code').innerText;
    navigator.clipboard.writeText(text);
    showToast("Command copied to clipboard.");
};

/* --- CORE SRE LOOP (SSE) --- */
function connectSRELoop() {
    if (currentSSE) currentSSE.close();
    currentSSE = new EventSource(`/api/sre-loop?simulation=true`);

    currentSSE.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            if (data.message) {
                if (data.message.includes('REASONING:')) {
                    const thought = data.message.replace('REASONING:', '');
                    showThought(thought);
                } else {
                    addLog(data.message, data.agent || 'SCOUT');
                }
                updateOODAPress(data.message);
                updatePills(data.message, data.agent);
            }
            if (data.top_incidents) {
                updateMemories(data.top_incidents);
            }
        } catch (err) { }
    };
}

function updatePills(msg, agent) {
    const sensory = document.getElementById('pill-sensory');
    const brain = document.getElementById('pill-brain');
    const fixer = document.getElementById('pill-fixer');

    if (msg.includes('ANOMALY')) {
        sensory.classList.add('active');
        sensory.querySelector('.pill-dot').classList.add('pulse');
    }

    if (agent === 'brain') {
        brain.classList.add('active');
        brain.querySelector('.pill-dot').classList.add('pulse');
        brain.innerText = "Brain: Thinking";
    } else if (brain.classList.contains('active') && !msg.includes('REASONING')) {
        brain.querySelector('.pill-dot').classList.remove('pulse');
        brain.innerText = "Brain: Idle";
    }

    if (agent === 'fixer') {
        fixer.classList.add('active');
        fixer.querySelector('.pill-dot').classList.add('pulse');
    }
}

function updateOODAPress(msg) {
    const stages = ['observe', 'orient', 'decide', 'act'];
    let currentStage = -1;

    if (msg.includes('OBSERVE') || msg.includes('INIT')) currentStage = 0;
    else if (msg.includes('REASONING') || msg.includes('ORIENT')) currentStage = 1;
    else if (msg.includes('DECIDE')) currentStage = 2;
    else if (msg.includes('ACT') || msg.includes('FIXER') || msg.includes('CURATOR')) currentStage = 3;

    if (currentStage >= 0) {
        for (let i = 0; i <= currentStage; i++) {
            const stage = stages[i];
            const bar = document.getElementById(`progress-${stage}`);
            const label = document.getElementById(`status-${stage}`);
            if (bar) bar.style.width = '100%';
            if (label) {
                label.innerText = 'ACTIVE';
                label.className = 'stage-status text-emerald-500';
            }
        }
    }

    if (msg.includes('END OF LOOP') || msg.includes('COMPLETE')) {
        setTimeout(resetOODA, 5000);
    }
}

function resetOODA() {
    ['observe', 'orient', 'decide', 'act'].forEach(s => {
        const bar = document.getElementById(`progress-${s}`);
        const label = document.getElementById(`status-${s}`);
        if (bar) bar.style.width = '0%';
        if (label) {
            label.innerText = 'IDLE';
            label.className = 'stage-status text-slate-400';
        }
    });
    document.getElementById('thought-bubble').classList.add('hidden');
}

function addLog(msg, agent) {
    const logContainer = document.getElementById('event-log');
    const entry = document.createElement('div');
    entry.className = "log-entry animate-entrance";

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    const agentColor = agent?.toLowerCase() === 'scout' ? 'text-blue-500' : (agent?.toLowerCase() === 'brain' ? 'text-purple-500' : 'text-slate-400');

    entry.innerHTML = `
        <span class="log-ts">${time}</span>
        <span class="${agentColor} font-bold uppercase min-w-[60px]">[${agent || 'SYS'}]</span>
        <span class="log-msg">${msg}</span>
    `;

    logContainer.prepend(entry);
    saveTerminalToStorage();
}

function saveTerminalToStorage() {
    const logs = document.getElementById('event-log').innerHTML;
    localStorage.setItem(TERMINAL_STORAGE_KEY, logs);
}

function loadTerminalFromStorage() {
    const saved = localStorage.getItem(TERMINAL_STORAGE_KEY);
    if (saved) {
        document.getElementById('event-log').innerHTML = saved;
    }
}

function showThought(thought) {
    const bubble = document.getElementById('thought-bubble');
    bubble.classList.remove('hidden');
    document.getElementById('thought-text').innerText = `"${thought.trim()}"`;
}

function updateMemories(memories) {
    const container = document.getElementById('memory-list');
    if (!memories || !memories.length) return;

    container.innerHTML = memories.map(m => `
        <div class="memory-card animate-entrance">
            <div class="memory-match">
                <span class="text-[10px] font-bold uppercase text-slate-400">Pattern Match</span>
                <span class="match-score">${Math.round((m.score || 0.95) * 100)}% Confidence</span>
            </div>
            <p class="text-[11px] font-medium text-slate-700 font-mono">${m.root_cause || 'Detected Anomaly Signature'}</p>
            <div class="mt-2 text-[10px] text-emerald-600 font-bold uppercase">Fix: ${m.remediation || 'Restart Service'}</div>
        </div>
    `).join('');
}

/* --- CHAOS CONTROLS --- */
window.triggerChaos = async (fault) => {
    showToast(`Injecting Anomaly: ${fault}`);
    resetOODA();
    await fetch('/demo/chaos/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fault })
    });
};

window.showToast = (msg) => {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = "bg-slate-900 text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-4 animate-entrance border border-white/10";
    toast.innerHTML = `<i data-lucide="info" class="w-4 h-4 text-blue-400"></i> <span class="text-[10px] font-bold uppercase tracking-widest">${msg}</span>`;
    container.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-10');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
};
