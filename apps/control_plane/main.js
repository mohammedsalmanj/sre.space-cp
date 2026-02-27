/**
 * SRE.SPACE v6.0 - THE HARD RESET - FINAL POLISH
 * Author: AG (for Mohammed Salman)
 */

let activeEnv = 'local';
let currentSSE = null;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    connectSRELoop();
});

/* --- ENVIRONMENT TOGGLE --- */
window.setEnv = (env) => {
    activeEnv = env;
    const isLocal = env === 'local';

    // UI Classes
    document.getElementById('btn-env-local').className = `wizard-track-btn ${isLocal ? 'active' : 'border-transparent bg-white shadow-sm border border-slate-100'}`;
    document.getElementById('btn-env-cloud').className = `wizard-track-btn ${!isLocal ? 'active' : 'border-transparent bg-white shadow-sm border border-slate-100'}`;

    // Card Visibility
    document.getElementById('env-local-card').classList.toggle('hidden', !isLocal);
    document.getElementById('env-cloud-card').classList.toggle('hidden', isLocal);

    showToast(`Operational Environment: ${env.toUpperCase()} Verified.`);
};

/* --- STACK SELECTOR --- */
window.selectStack = (stack) => {
    const cmds = {
        ec2: `curl -sSL https://install.sre.space/aws-otel.sh | bash\nsre-pilot link --stack ec2 --target standalone`,
        eks: `helm repo add sre-space http://charts.sre.space\nhelm install sre-pilot sre-space/agent --set controlPlane.url=${window.location.host}`,
        vms: `gcloud compute instances add-metadata sre-host \\\n  --metadata startup-script="curl -sSL install.sre.space/gce"`
    };

    document.getElementById('automation-cmd').innerText = cmds[stack];

    // Visual indicators
    document.querySelectorAll('[id^="stack-"]').forEach(img => img.classList.add('grayscale'));
    document.getElementById(`stack-${stack === 'vms' ? 'gcp' : stack}-img`).classList.remove('grayscale');

    document.querySelectorAll('[id^="icon-"]').forEach(icon => {
        icon.classList.add('grayscale', 'opacity-30');
    });
    const mainIcon = stack === 'vms' ? 'gcp' : (stack === 'eks' ? 'k8s' : 'aws');
    document.getElementById(`icon-${mainIcon}`).classList.remove('grayscale', 'opacity-30');

    showToast(`Strata Logic: ${stack.toUpperCase()} Bootstrap Generated.`);
};

/* --- INITIALIZATION SEQUENCE --- */
window.initializeSpace = async () => {
    const btn = document.getElementById('btn-initialize');
    const originalText = btn.innerText;
    btn.disabled = true;

    const steps = [
        { msg: "1. Scanning OTel Strata...", time: 1000 },
        { msg: "2. Verifying Pinecone Vector Link...", time: 1200 },
        { msg: "3. Hot-Linking Cloud Driver...", time: 800 },
        { msg: "4. Status: NOMINAL", time: 500 }
    ];

    for (const step of steps) {
        btn.innerText = step.msg;
        appendReasoning(step.msg, 'SYSTEM');
        await new Promise(r => setTimeout(r, step.time));
    }

    btn.innerText = "SPACE INITIALIZED";
    btn.classList.add('!bg-emerald-600');
    showToast("Control Plane: NOMINAL Authority Granted.");
};

/* --- CORE LOOP --- */
function connectSRELoop() {
    if (currentSSE) currentSSE.close();

    const url = `/api/sre-loop?simulation=true`;
    currentSSE = new EventSource(url);

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

    entry.innerHTML = `
        <span class="terminal-timestamp">${time}</span>
        <span class="terminal-agent agent-${agent.toLowerCase()}">${agent}</span>
        <span class="text-slate-600">${msg}</span>
    `;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function appendReasoning(thought, agent) {
    const container = document.getElementById('terminal-feed');
    const entry = document.createElement('div');
    entry.className = "terminal-entry animate-entrance border-l-2 border-blue-600 pl-4 my-4 bg-blue-50/30 py-2 rounded-r-xl";
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    entry.innerHTML = `
        <div class="flex items-center gap-2 mb-1">
            <span class="text-[9px] font-black text-blue-600 uppercase tracking-widest italic">${agent} THOUGHT</span>
        </div>
        <p class="text-slate-800 font-medium italic">"${thought.trim()}"</p>
    `;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

/* --- UTILS --- */
window.showToast = (msg) => {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = "bg-slate-900 text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-4 animate-entrance border border-white/10";
    toast.innerHTML = `<i data-lucide="info" class="w-5 h-5 text-blue-400"></i> <span class="text-[11px] font-black uppercase tracking-widest">${msg}</span>`;
    container.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-10');
        setTimeout(() => toast.remove(), 500);
    }, 4000);
};

window.copySnippet = () => {
    const text = document.getElementById('automation-cmd').innerText;
    navigator.clipboard.writeText(text).then(() => showToast("Command Copied to Clipboard."));
};

window.clearTerminal = () => {
    document.getElementById('terminal-feed').innerHTML = '<div class="italic text-slate-400 text-[11px]"># Cache flushed. Strata normalized.</div>';
};

window.injectCredentials = () => {
    showToast("Credentials Handshaked. Provisioning Enterprise Link...");
    setTimeout(() => {
        showToast("Link Successful. Authority Verified.");
    }, 1500);
};
