/**
 * SRE.SPACE v6.0 - THE HARD RESET
 * Logic Inspired by v4.0 (Commit 40bfc41)
 * Functional Onboarding, System Health, and Chaos Controls
 */

let activeEnv = 'local';
let currentSSE = null;
let currentTourStep = 0;

const tourSteps = [
    {
        title: "Phase 1: Scout",
        desc: "The Senses Layer — OpenTelemetry Intake. Scout monitors for metric drift and anomalous traces without creating alert fatigue.",
        icon: "binoculars"
    },
    {
        title: "Phase 2: Brain",
        desc: "The Cognitive Layer. Performs LLM-driven Root Cause Analysis (RCA) by correlating high-cardinality data with historical memory.",
        icon: "brain"
    },
    {
        title: "Phase 3: Guardrail",
        desc: "Deterministic Safety. Validates proposed fixes against production safety policies before any code is pushed.",
        icon: "shield-alert"
    },
    {
        title: "Phase 4: Fixer",
        desc: "Autonomous Remediation. Generates GitOps patches and executes canary deployments to restore Service Level Objectives (SLOs).",
        icon: "wrench"
    }
];

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    connectSRELoop();
});

/* --- ENVIRONMENT & PROVISIONING --- */
window.setEnv = (env) => {
    activeEnv = env;
    const isLocal = env === 'local';

    document.getElementById('btn-env-local').className = `wizard-track-btn ${isLocal ? 'active' : 'border-transparent bg-white shadow-sm border border-slate-100'}`;
    document.getElementById('btn-env-cloud').className = `wizard-track-btn ${!isLocal ? 'active' : 'border-transparent bg-white shadow-sm border border-slate-100'}`;

    document.getElementById('setup-local-desc').classList.toggle('hidden', !isLocal);
    document.getElementById('setup-cloud-desc').classList.toggle('hidden', isLocal);

    showToast(`Environment Strategy: ${env.toUpperCase()} Normalized.`);
};

window.provisionCloud = async () => {
    const stack = document.querySelector('input[name="cloud-stack"]:checked').value;
    showToast(`Provisioning ${stack.toUpperCase()} Infrastructure...`);

    // Simulate legacy progress
    appendReasoning(`Initiating Cloud Handshake for ${stack.toUpperCase()}`, 'SYSTEM');
    await new Promise(r => setTimeout(r, 1000));
    appendReasoning("Validating IAM Role SRE-Space-ControlPlane", 'SYSTEM');
    await new Promise(r => setTimeout(r, 1000));
    appendReasoning("Infrastructure Ready. Agent Hot-Link Established.", 'SYSTEM');

    showToast(`${stack.toUpperCase()} Provisioning Complete.`);
};

/* --- SYSTEM INITIALIZATION --- */
window.initializeSpace = async () => {
    const btn = document.getElementById('btn-initialize');
    btn.disabled = true;

    const steps = [
        "1. Scanning OTel Strata...",
        "2. Verifying Pinecone Memory...",
        "3. Synchronizing Cloud Drivers...",
        "4. Status: NOMINAL"
    ];

    for (const msg of steps) {
        btn.innerText = msg;
        appendReasoning(msg, 'SYSTEM');
        await new Promise(r => setTimeout(r, 800));
    }

    btn.innerText = "SPACE INITIALIZED";
    btn.classList.add('!bg-emerald-600');
    showToast("Control Plane Online. Authority Granted.");
};

/* --- TOUR LOGIC --- */
window.startTour = () => {
    currentTourStep = 0;
    document.getElementById('tour-modal').classList.remove('hidden');
    updateTourUI();
};

window.closeTour = () => {
    document.getElementById('tour-modal').classList.add('hidden');
};

window.nextTour = () => {
    if (currentTourStep < tourSteps.length - 1) {
        currentTourStep++;
        updateTourUI();
    } else {
        closeTour();
        showToast("Initialization Tour Complete.");
    }
};

function updateTourUI() {
    const step = tourSteps[currentTourStep];
    document.getElementById('tour-step-title').innerText = step.title;
    document.getElementById('tour-step-desc').innerText = step.desc;
    document.getElementById('tour-step-icon').innerHTML = `<i data-lucide="${step.icon}" class="w-8 h-8"></i>`;

    // Dots
    const dots = document.getElementById('tour-dots');
    dots.innerHTML = tourSteps.map((_, i) => `
        <div class="w-2 h-2 rounded-full ${i === currentTourStep ? 'bg-blue-600' : 'bg-slate-200'}"></div>
    `).join('');

    document.getElementById('btn-next-tour').innerText = currentTourStep === tourSteps.length - 1 ? "Finish Tour" : "Next Protocol";

    lucide.createIcons();
}

/* --- CORE SRE LOOP (SSE) --- */
function connectSRELoop() {
    if (currentSSE) currentSSE.close();
    currentSSE = new EventSource(`/api/sre-loop?simulation=true`);

    currentSSE.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            if (data.message) {
                if (data.message.includes('REASONING:')) {
                    appendReasoning(data.message.replace('REASONING:', ''), data.agent || 'BRAIN');
                } else {
                    appendLog(data.message, data.agent || 'SCOUT');
                }
            }
        } catch (err) { }
    };
}

function appendLog(msg, agent) {
    const container = document.getElementById('terminal-feed');
    const entry = document.createElement('div');
    entry.className = "terminal-entry animate-entrance";
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    const agentClass = `agent-${agent?.toLowerCase() || 'system'}`;
    entry.innerHTML = `
        <span class="terminal-timestamp">${time}</span>
        <span class="terminal-agent ${agentClass}">${agent}</span>
        <span class="text-slate-600">${msg}</span>
    `;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function appendReasoning(thought, agent) {
    const container = document.getElementById('terminal-feed');
    const entry = document.createElement('div');
    entry.className = "terminal-entry animate-entrance border-l-2 border-blue-600 pl-4 my-4 bg-blue-50/20 py-3 rounded-r-xl";
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    entry.innerHTML = `
        <div class="flex items-center gap-2 mb-1">
            <span class="text-[9px] font-black text-blue-600 uppercase tracking-widest italic">${agent} THOUGHT</span>
        </div>
        <p class="text-slate-800 font-medium italic text-xs">"${thought.trim()}"</p>
    `;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

/* --- ACTIONS --- */
window.triggerChaos = async (fault) => {
    showToast(`Injecting Fault: ${fault}`);
    const status = document.getElementById('sys-status');
    status.className = "px-3 py-1 bg-red-50 text-red-600 rounded-full text-[9px] font-black uppercase tracking-widest border border-red-100 flex items-center gap-2";
    status.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-red-600 animate-pulse"></span> ANOMALY DETECTED`;

    await fetch('/demo/chaos/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fault })
    });

    // Auto-restore after 30s
    setTimeout(() => {
        status.className = "px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-[9px] font-black uppercase tracking-widest border border-emerald-100 flex items-center gap-2";
        status.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span> NOMINAL`;
    }, 30000);
};

window.clearTerminal = () => {
    document.getElementById('terminal-feed').innerHTML = '<div class="italic text-slate-400 text-[11px]"># Cache flushed. Strata normalized.</div>';
};

window.showToast = (msg) => {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = "bg-slate-900/90 backdrop-blur-md text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-4 animate-entrance border border-white/10";
    toast.innerHTML = `<i data-lucide="info" class="w-5 h-5 text-blue-400"></i> <span class="text-[10px] font-black uppercase tracking-widest">${msg}</span>`;
    container.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-10');
        setTimeout(() => toast.remove(), 500);
    }, 4000);
};
