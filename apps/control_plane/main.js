/**
 * SRE.SPACE v6.0 - THE HARD RESET
 * Core Orchestration & Neural sensory intakes
 */

const API_BASE = '';
let activeStep = 1;
let selectedProvider = null;
let currentSSE = null;
let isStrictMode = false;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    showTab('dashboard');
    connectTelemetry();
    connectSRELoop(false);
});

/* --- TAB NAVIGATION --- */
window.showTab = (tab) => {
    ['dashboard', 'wizard'].forEach(p => {
        const el = document.getElementById(`content-${p}`);
        const btn = document.getElementById(`tab-${p}`);
        if (!el || !btn) return;
        el.classList.toggle('hidden', p !== tab);
        if (p === tab) {
            btn.classList.add('border-blue-600', 'text-slate-900');
            btn.classList.remove('text-slate-400');
        } else {
            btn.classList.remove('border-blue-600', 'text-slate-900');
            btn.classList.add('text-slate-400');
        }
    });
};

/* --- 4-STEP WIZARD STATE MACHINE --- */
window.selectProvider = (provider) => {
    selectedProvider = provider;
    document.querySelectorAll('.provider-card').forEach(card => card.classList.remove('selected', 'border-slate-900'));
    event.currentTarget.classList.add('selected', 'border-slate-900');

    // Configure Step 2 Labels
    const labels = {
        aws: ["AWS Access Key ID", "AWS Secret Access Key"],
        gcp: ["GCP Project ID", "Service Account JSON Key"],
        k8s: ["Cluster Context Name", "Kubeconfig String"],
        local: ["Docker Desktop Instance", "Sandbox UUID"]
    };
    document.getElementById('label-cred-1').innerText = labels[provider][0];
    document.getElementById('label-cred-2').innerText = labels[provider][1];

    wizardNext();
};

window.wizardNext = async () => {
    if (activeStep === 2 && !window.isValidated) {
        showToast("Authority Validation Required.");
        return;
    }
    if (activeStep < 4) {
        activeStep++;
        updateWizardUI();
    }
};

window.wizardPrev = () => {
    if (activeStep > 1) {
        activeStep--;
        updateWizardUI();
    }
};

async function updateWizardUI() {
    for (let i = 1; i <= 4; i++) {
        document.getElementById(`wiz-step-${i}`).classList.add('hidden');
        const dot = document.getElementById(`step-${i}-dot`);
        dot.className = `w-12 h-12 rounded-full flex items-center justify-center font-black text-xl transition-all ${i <= activeStep ? 'bg-slate-900 text-white shadow-xl' : 'bg-white border-2 border-slate-100 text-slate-300'}`;
    }
    document.getElementById(`wiz-step-${activeStep}`).classList.remove('hidden');
    document.getElementById('wiz-progress-bar').style.width = `${((activeStep - 1) / 3) * 100}%`;
    document.getElementById('btn-wiz-prev').classList.toggle('hidden', activeStep === 1);
    document.getElementById('btn-wiz-next').classList.toggle('hidden', activeStep === 4 || activeStep === 1);

    if (activeStep === 3) {
        const res = await fetch('/api/v1/provision/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider: selectedProvider, stack: 'standalone' })
        });
        const data = await res.json();
        document.getElementById('instrument-snippet').innerText = data.asset || '# Failed to generate snippet.';
    }
}

window.validateAuthority = async () => {
    const btn = document.getElementById('btn-validate');
    const ak = document.getElementById('input-cred-1').value;
    const sk = document.getElementById('input-cred-2').value;

    btn.innerText = "Executing Background Validation Task...";
    btn.disabled = true;

    try {
        const endpoint = selectedProvider === 'aws' ? '/api/v1/validate/aws' : '/api/v1/validate/gcp';
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ accessKey: ak, secretKey: sk, jsonKey: sk }) // Mocking mapping
        });
        const data = await res.json();

        if (data.status === 'success') {
            window.isValidated = true;
            btn.innerText = "AUTH_SUCCESS: AUTHORITY GRANTED";
            btn.classList.replace('bg-slate-900', 'bg-emerald-600');
            showToast("Cloud Authority Handshake Verified.");
            setTimeout(wizardNext, 1000);
        } else {
            btn.innerText = "AUTH_FAILURE: REJECTED";
            btn.classList.add('bg-red-600');
            setTimeout(() => {
                btn.innerText = "Verify Handshake";
                btn.classList.remove('bg-red-600');
                btn.disabled = false;
            }, 2000);
        }
    } catch (e) {
        showToast("System Error during validation.");
        btn.disabled = false;
    }
};

window.finalizePromotion = () => {
    isStrictMode = document.getElementById('strict-toggle').checked;
    showTab('dashboard');
    showToast(`System Promoted: STRICT_MODE=${isStrictMode}`);
    document.getElementById(`status-${selectedProvider}`).style.opacity = "1";
    document.getElementById(`status-${selectedProvider}`).classList.remove('grayscale');
};

/* --- TELEMETRY & SRE LOOP (SSE) --- */
function connectTelemetry() {
    const stream = new EventSource('/api/v1/telemetry/stream');
    stream.onmessage = (e) => {
        const data = JSON.parse(e.data);
        // Metric bars update could go here
    };
}

function connectSRELoop(isAnomaly = false) {
    if (currentSSE) currentSSE.close();
    const url = `/api/sre-loop?anomaly=${isAnomaly}`;
    currentSSE = new EventSource(url);

    currentSSE.onmessage = (e) => {
        const data = JSON.parse(e.data);

        if (data.message) {
            if (data.message.includes("REASONING: Thought:")) {
                appendReasoning(data.message.replace("REASONING: Thought:", ""), data.agent);
            } else {
                appendRawLog(data.message, data.agent);
            }
        }

        if (data.top_incidents) {
            updateRecallSidebar(data.top_incidents);
        }
    };
}

function appendRawLog(msg, agent) {
    const container = document.getElementById('logs-raw');
    const entry = document.createElement('div');
    entry.className = "log-entry animate-entrance";
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    let agentClass = `agent-${agent?.toLowerCase() || 'system'}`;
    entry.innerHTML = `
        <span class="log-timestamp text-[9px]">${time}</span>
        <span class="log-agent ${agentClass}">${agent || 'INFRA'}</span>
        <span class="log-text">${msg}</span>
    `;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function appendReasoning(thought, agent) {
    const container = document.getElementById('logs-reasoning');
    const block = document.createElement('div');
    block.className = "reasoning-thought animate-entrance";
    block.innerHTML = `
        <span class="reasoning-header">${agent || 'BRAIN'} LOGIC</span>
        <p class="text-slate-800 leading-relaxed italic">"${thought.trim()}"</p>
    `;
    container.appendChild(block);
    container.scrollTop = container.scrollHeight;
}

function updateRecallSidebar(incidents) {
    const container = document.getElementById('recall-list');
    container.innerHTML = incidents.map(inc => `
        <div class="recall-item animate-entrance">
            <div class="flex justify-between items-start mb-2">
                <span class="text-[8px] font-black text-blue-600 uppercase tracking-widest">${inc.stack_type} Match</span>
                <span class="recall-score">${(inc.score * 100).toFixed(0)}% Match</span>
            </div>
            <p class="text-[10px] font-bold text-slate-900 leading-tight mb-2">${inc.root_cause}</p>
            <div class="p-3 bg-slate-50 rounded-xl border border-slate-100 text-[9px] text-slate-500 font-mono">
                FIX: ${inc.remediation}
            </div>
        </div>
    `).join('');
}

/* --- ACTIONS --- */
window.triggerChaos = async (fault) => {
    showToast(`Injecting Fault: ${fault}`);
    await fetch('/demo/chaos/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fault })
    });
    connectSRELoop(true);
};

window.clearLogs = () => {
    document.getElementById('logs-raw').innerHTML = '<div class="italic text-slate-400"># Logs flushed.</div>';
    document.getElementById('logs-reasoning').innerHTML = '<div class="italic text-slate-300"># Reasoning cache cleared.</div>';
};

function showToast(msg) {
    const container = document.getElementById('hud-toast-container');
    const toast = document.createElement('div');
    toast.className = "toast";
    toast.innerHTML = `<i data-lucide="info" class="w-5 h-5 text-blue-400"></i> ${msg}`;
    container.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => toast.remove(), 4000);
}

window.copySnippet = () => {
    const txt = document.getElementById('instrument-snippet').innerText;
    navigator.clipboard.writeText(txt).then(() => showToast("Snippet Copied."));
};
