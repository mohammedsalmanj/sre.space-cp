const API_BASE_URL = window.NEXT_PUBLIC_API_URL;
const logsFeed = document.getElementById('logs-feed');
const incidentList = document.getElementById('incident-list');
const activePRsCount = document.getElementById('active-prs');
const envBadge = document.getElementById('env-badge');

// Block 1: Real-Time Veracity (SSE)
function connectToAgentStream() {
    console.log("🔗 Opening SRE Agent Stream...");
    const eventSource = new EventSource(`${API_BASE_URL}/api/sre-loop?anomaly=false`);

    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);
        const entry = document.createElement('div');
        entry.className = 'log-entry';

        // Add color coding for OODA stages
        if (data.message.includes('[OBSERVE]')) entry.classList.add('observe');
        if (data.message.includes('[ORIENT]')) entry.classList.add('orient');
        if (data.message.includes('[DECIDE]')) entry.classList.add('decide');
        if (data.message.includes('[ACT]')) entry.classList.add('act');

        entry.innerText = data.message;
        logsFeed.appendChild(entry);
        logsFeed.scrollTop = logsFeed.scrollHeight;
    };

    eventSource.onerror = function () {
        console.error("Stream failed. Retrying...");
        eventSource.close();
        setTimeout(connectToAgentStream, 5000);
    };
}

// Block 3: GitHub Integrity Feed
async function fetchGitVeracity() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/git-activity`);
        const data = await res.json();

        if (data && !data.error) {
            activePRsCount.innerText = data.length;
            incidentList.innerHTML = data.map(pr => `
                <div class="incident-card" onclick="window.open('${pr.html_url}', '_blank')">
                    <div class="incident-info">
                        <h4>PR #${pr.number} - ${pr.title}</h4>
                        <p style="font-family: 'JetBrains Mono'; font-size: 10px;">SHA: ${pr.head.sha.substring(0, 7)} | 👤 ${pr.user.login}</p>
                    </div>
                    <div class="status-badge" style="background: ${pr.state === 'open' ? '#dcfce7' : '#f1f5f9'}; color: ${pr.state === 'open' ? '#10b981' : '#64748b'};">
                        ${pr.state.toUpperCase()}
                    </div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Git veracity sync failed:", err);
    }
}

async function updateSystemState() {
    try {
        const res = await fetch(`${API_BASE_URL}/system/health`);
        const data = await res.json();

        if (data.env) {
            envBadge.innerText = data.env.toUpperCase();
            envBadge.style.background = data.env === 'cloud' ? '#3b82f6' : '#f59e0b';
            envBadge.style.color = 'white';
        }
    } catch (err) {
        envBadge.innerText = "OFFLINE";
        envBadge.style.background = "#ef4444";
    }
}

// Initialization
connectToAgentStream();
fetchGitVeracity();
updateSystemState();

// Polling
setInterval(fetchGitVeracity, 10000);
setInterval(updateSystemState, 5000);
