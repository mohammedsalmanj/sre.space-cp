import React, { useState, useEffect } from 'react';
import { Heart, Car, Dog, Stethoscope, Terminal } from 'lucide-react';
import PolicyCard from './components/PolicyCard';
import AgentTerminal from './components/AgentTerminal';
import ChaosToggle from './components/ChaosToggle';

function App() {
    const [chaosMode, setChaosMode] = useState(false);
    const [logs, setLogs] = useState([
        { id: 1, timestamp: new Date().toLocaleTimeString(), msg: "System connected to SRE Control Plane." }
    ]);

    const addLog = (msg) => {
        const newLog = {
            id: Date.now(),
            timestamp: new Date().toLocaleTimeString(),
            msg: msg
        };
        setLogs(prev => [...prev, newLog]);
    };

    // Simulate background chatter
    useEffect(() => {
        const interval = setInterval(() => {
            if (Math.random() > 0.8) {
                addLog(`[SYSTEM] Heartbeat check: Healthy. Latency: ${Math.floor(Math.random() * 20 + 10)}ms`);
            }
        }, 8000);
        return () => clearInterval(interval);
    }, []);

    const policies = [
        { title: "Life Insurance", icon: Heart },
        { title: "Vehicle Policy", icon: Car },
        { title: "Pet Coverage", icon: Dog },
        { title: "Dental Plan", icon: Stethoscope },
    ];

    return (
        <div className="min-h-screen p-8 flex flex-col items-center">
            {/* Header */}
            <header className="w-full max-w-7xl flex justify-between items-center mb-12 animate-fade-in-down">
                <div>
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 mb-2">
                        SRE.Space Policy Hub
                    </h1>
                    <p className="text-slate-400 font-mono text-sm">Reactive Insurance Platform // Autonomy Level 5</p>
                </div>
                <ChaosToggle enabled={chaosMode} setEnabled={setChaosMode} />
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
                            onQuote={addLog}
                        />
                    ))}
                </div>

                {/* SRE Terminal Side Panel */}
                <div className="lg:col-span-4 flex flex-col gap-6">
                    <div className="glass-panel p-6 rounded-2xl">
                        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                            <Terminal className="w-5 h-5 text-primary" />
                            System Status
                        </h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-white/5 p-4 rounded-xl text-center">
                                <span className="block text-2xl font-bold text-accent">99.98%</span>
                                <span className="text-xs text-slate-500 uppercase tracking-widest">Uptime</span>
                            </div>
                            <div className="bg-white/5 p-4 rounded-xl text-center">
                                <span className="block text-2xl font-bold text-primary">24ms</span>
                                <span className="text-xs text-slate-500 uppercase tracking-widest">Avg Latency</span>
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
