/**
 * SRE.SPACE v6.0 - THE HARD RESET
 * Sidebar Navigation & Agentic Loop Sync
 * Inspired by commit 314c6d8
 */

let currentSSE = null;

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    connectSRELoop();
});

/* --- NAVIGATION BUS --- */
window.switchTab = (tab) => {
    // Update Sidebar state
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    event?.currentTarget?.classList.add('active');

    showToast(`Navigated to: ${tab.toUpperCase()}`);

    // In a real app we would switch panes here. 
    // For this dashboard, we focused on the integrated Dashboard view.
};

/* --- SYSTEM INITIALIZATION --- */
window.initializeSpace = async () => {
    const btn = event?.currentTarget || document.querySelector('button[onclick="initializeSpace()"]');
    btn.disabled = true;

    const steps = [
        "Scanning OTel Strata...",
        "Verifying Pinecone Memory...",
        "Synchronizing Cloud Drivers...",
        "Authority: GRANTED"
    ];

    for (const msg of steps) {
        btn.innerText = msg;
        appendReasoning(msg, 'SYSTEM');
        await new Promise(r => setTimeout(r, 600));
    }

    btn.innerText = "INITIALIZED";
    btn.classList.add('!bg-emerald-600');
    showToast("Control Plane Online.");
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
    entry.className = "terminal-entry animate-entrance mb-1 flex items-start gap-3";
    const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' });

    const agentColor = agent?.toLowerCase() === 'scout' ? 'text-blue-500' : 'text-purple-500';

    entry.innerHTML = `
        <span class="text-[10px] text-slate-300 font-bold font-mono">${time}</span>
        <span class="text-[10px] font-black uppercase tracking-wider ${agentColor} min-w-[60px]">[${agent}]</span>
        <span class="text-slate-600 text-[11px] font-medium font-sans">${msg}</span>
    `;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function appendReasoning(thought, agent) {
    const container = document.getElementById('terminal-feed');
    const entry = document.createElement('div');
    entry.className = "animate-entrance my-4 p-4 bg-slate-50 border border-slate-100 rounded-2xl border-l-4 border-l-blue-600";

    entry.innerHTML = `
        <div class="flex items-center gap-2 mb-2">
            <span class="text-[9px] font-black text-blue-600 uppercase tracking-[0.2em] italic">Internal Reasoning Pipeline</span>
        </div>
        <p class="text-[12px] text-slate-800 font-bold italic leading-relaxed">"${thought.trim()}"</p>
    `;

    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

/* --- CHAOS CONTROLS --- */
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

    // Auto-restore nominal status in UI after 30s
    setTimeout(() => {
        status.className = "px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-[9px] font-black uppercase tracking-widest border border-emerald-100 flex items-center gap-2";
        status.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span> NOMINAL`;
    }, 30000);
};

window.clearTerminal = () => {
    document.getElementById('terminal-feed').innerHTML = '<div class="italic text-slate-400 text-[11px]"># Strata buffer flushed. Monitoring normalized.</div>';
};

window.showToast = (msg) => {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = "bg-slate-900 text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-4 animate-entrance border border-white/10";
    toast.innerHTML = `<i data-lucide="info" class="w-4 h-4 text-blue-400"></i> <span class="text-[10px] font-black uppercase tracking-widest">${msg}</span>`;
    container.appendChild(toast);
    lucide.createIcons();
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-10');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
};
