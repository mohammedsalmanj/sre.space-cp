import React, { useState, useEffect, useRef } from 'react';
import { Heart, Car, Dog, Stethoscope, Terminal, Activity, Shield, Sparkles } from 'lucide-react';
import PolicyCard from './components/PolicyCard';
import AgentTerminal from './components/AgentTerminal';
import ChaosToggle from './components/ChaosToggle';

function App() {
    const [chaosMode, setChaosMode] = useState(false);
    const [logs, setLogs] = useState([
        { id: 1, timestamp: new Date().toLocaleTimeString(), msg: "System connected to SRE Control Plane." }
    ]);
    const [stats, setStats] = useState({
        uptime: "99.98%",
        latency: "24ms"
    });

    const addLog = (msg, topic = "system") => {
        const newLog = {
            id: Date.now() + Math.random(),
            timestamp: new Date().toLocaleTimeString(),
            msg: `[${topic.toUpperCase()}] ${msg}`
        };
        setLogs(prev => [...prev.slice(-49), newLog]);
    };

    // WebSocket Connection
    useEffect(() => {
        const ws = new WebSocket(`ws://${window.location.hostname}:8005/ws/stream`);

        ws.onopen = () => {
            addLog("WebSocket Stream Connected", "network");
        };

        ws.onmessage = (event) => {
            const message = json.parse(event.data);
            const { topic, data } = message;

            if (topic === "agent_thoughts") {
                addLog(data.thought || data.message, "brain");
            } else if (topic === "incident_updates") {
                addLog(`Incident ${data.id}: ${data.status}`, "scout");
            } else if (topic === "remediation_log") {
                addLog(`Remediation: ${data.action}`, "fixer");
            } else {
                addLog(JSON.stringify(data), topic);
            }
        };

        ws.onclose = () => {
            addLog("WebSocket Stream Disconnected. Retrying...", "network");
        };

        return () => ws.close();
    }, []);

    const triggerQuote = async (policyType) => {
        addLog(`Initiating ${policyType} quote...`, "user");
        try {
            const response = await fetch('/api/v1/quote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: json.stringify({
                    policy_type: policyType,
                    user_id: "user-" + Math.floor(Math.random() * 1000),
                    timestamp: Date.now()
                })
            });
            const data = await response.json();
            addLog(`Quote request broadcasted: ${data.quote_id}`, "system");
        } catch (error) {
            addLog(`Failed to initiate quote: ${error.message}`, "error");
        }
    };

    const policies = [
        { title: "Life Insurance", icon: Heart },
        { title: "Vehicle Policy", icon: Car },
        { title: "Pet Coverage", icon: Dog },
        { title: "Dental Plan", icon: Stethoscope },
    ];

    return (
        <div className="min-h-screen p-8 flex flex-col items-center">
            {/* Header */}
            <header className="w-full max-w-7xl flex justify-between items-center mb-12">
                <div>
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 mb-2">
                        Anti-Gravity Control Plane
                    </h1>
                    <p className="text-slate-400 font-mono text-sm">Reactive Insurance Platform // Autonomy Level 5</p>
                </div>
                <div className="flex items-center gap-6">
                    <div className="flex gap-4">
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Uptime</span>
                            <span className="text-sm font-mono text-accent">{stats.uptime}</span>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Latency</span>
                            <span className="text-sm font-mono text-primary">{stats.latency}</span>
                        </div>
                    </div>
                    <ChaosToggle enabled={chaosMode} setEnabled={setChaosMode} />
                </div>
            </header>

            {/* Main Grid */}
            <div className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-12 gap-8">

                {/* Policy Cards Area */}
                <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    {policies.map((p, i) => (
                        <PolicyCard
                            key={i}
                            title={p.title}
                            icon={p.icon}
                            chaosMode={chaosMode}
                            onQuote={(msg) => addLog(msg, "ui")}
                            triggerAction={() => triggerQuote(p.title)}
                        />
                    ))}
                </div>

                {/* SRE Terminal Side Panel */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="glass-panel p-6 rounded-2xl flex flex-col gap-4">
                        <h2 className="text-lg font-bold flex items-center gap-2">
                            <Activity className="w-5 h-5 text-primary" />
                            Agent Pulse
                        </h2>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between text-xs font-mono">
                                <span className="text-slate-500">Scout (Monitoring)</span>
                                <span className="text-accent">CONNECTED</span>
                            </div>
                            <div className="flex items-center justify-between text-xs font-mono">
                                <span className="text-slate-500">Brain (Reasoning)</span>
                                <span className="text-purple-400">ACTIVE</span>
                            </div>
                            <div className="flex items-center justify-between text-xs font-mono">
                                <span className="text-slate-500">Fixer (Remediation)</span>
                                <span className="text-blue-400">WAITING</span>
                            </div>
                        </div>
                    </div>

                    <AgentTerminal logs={logs} />
                </div>
            </div>
        </div>
    );
}

export default App;
