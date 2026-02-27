/**
 * SRE.SPACE | Enterprise APM Controller
 * Logic for Real-Time OODA Progress and High-Density Feed
 */

let currentSSE = null;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    connectSRELoop();
});

/* --- UI CONTROLS --- */
window.toggleDrawer = () => {
    document.getElementById('onboarding-drawer').classList.toggle('collapsed');
};

window.startSandbox = () => {
    addLog("PROVISIONING: Initializing local container strata...", "SYSTEM");
    showToast("Sandbox Environment Initializing...");
    setTimeout(() => {
        addLog("SYSTEM: Local Simulation Protocol Activated.", "SYSTEM");
    }, 1000);
};

window.initializeCloud = async () => {
    const provider = document.getElementById('cloud-provider').value;
    const stack = document.getElementById('stack-type').value;

    addLog(`INIT: Initiating Credential Handshake with ${provider.toUpperCase()}...`, "SYSTEM");
    showToast(`Establishing ${provider.toUpperCase()} Connection...`);

    await new Promise(r => setTimeout(r, 1500));
    addLog(`AUTH: Handshake Successful. Role: SRE-Control-Plane.`, "SYSTEM");

    await new Promise(r => setTimeout(r, 1000));
    addLog(`STACK: Detected Target [${stack.toUpperCase()}]. Starting monitoring handshake...`, "SYSTEM");

    showToast("Enterprise Control Plane Online.");
    toggleDrawer();
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
            }
            if (data.memories) {
                updateMemories(data.memories);
            }
        } catch (err) { }
    };
}

function updateOODAPress(msg) {
    const stages = ['OBSERVE', 'ORIENT', 'DECIDE', 'ACT'];
    let currentStage = -1;

    if (msg.includes('OBSERVE')) currentStage = 0;
    else if (msg.includes('REASONING') || msg.includes('ORIENT')) currentStage = 1;
    else if (msg.includes('DECIDE')) currentStage = 2;
    else if (msg.includes('ACT') || msg.includes('FIXER')) currentStage = 3;

    if (currentStage >= 0) {
        for (let i = 0; i <= currentStage; i++) {
            const stage = stages[i].toLowerCase();
            const bar = document.getElementById(`progress-${stage}`);
            const label = document.getElementById(`status-${stage}`);
            if (bar) bar.style.width = '100%';
            if (label) {
                label.innerText = 'ACTIVE';
                label.className = 'stage-status text-emerald-500';
            }
        }
    }

    if (msg.includes('NOMINAL') || msg.includes('COMPLETE')) {
        setTimeout(resetOODA, 3000);
    }
}

function resetOODA() {
    const stages = ['observe', 'orient', 'decide', 'act'];
    stages.forEach(s => {
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
    entry.className = "log-entry";

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    const agentColor = agent?.toLowerCase() === 'scout' ? 'text-blue-500' : 'text-purple-500';

    entry.innerHTML = `
        <span class="log-ts">${time}</span>
        <span class="${agentColor} font-bold">[${agent.toUpperCase()}]</span>
        <span class="log-msg">${msg}</span>
    `;

    logContainer.prepend(entry); // APM standard: Newest on top
}

function showThought(thought) {
    const bubble = document.getElementById('thought-bubble');
    bubble.classList.remove('hidden');
    bubble.innerHTML = `<p class="text-[13px] font-bold text-blue-900 leading-relaxed italic">"${thought.trim()}"</p>`;
}

function updateMemories(memories) {
    const container = document.getElementById('memory-list');
    if (!memories.length) return;

    container.innerHTML = memories.map(m => `
        <div class="memory-card animate-entrance">
            <div class="memory-match">
                <span class="text-[10px] font-bold uppercase text-slate-400">Match Pattern</span>
                <span class="match-score">${Math.round(m.score * 100)}% Match</span>
            </div>
            <p class="text-[11px] font-medium text-slate-700">${m.metadata?.title || 'Unknown Incident'}</p>
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
    toast.className = "bg-slate-900 text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-4 animate-entrance";
    toast.innerHTML = `<i data-lucide="info" class="w-4 h-4 text-blue-400"></i> <span class="text-[10px] font-bold uppercase tracking-widest">${msg}</span>`;
    container.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-10');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
};
