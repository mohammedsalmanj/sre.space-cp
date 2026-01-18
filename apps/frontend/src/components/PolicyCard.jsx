import React, { useState } from 'react';
import { Shield, Sparkles, AlertTriangle, CheckCircle2, Activity } from 'lucide-react';

const PolicyCard = ({ title, icon: Icon, onQuote, chaosMode, triggerAction }) => {
    const [status, setStatus] = useState('idle'); // idle, checking, scanning, analyzing, success, error, remediating

    const handleQuote = async () => {
        if (status !== 'idle') return;

        // Trigger real backend action
        if (triggerAction) triggerAction();

        // Sequence
        setStatus('checking');
        onQuote(`Checking Eligibility for ${title}...`);

        setTimeout(() => {
            setStatus('scanning');
            onQuote(`[SCOUT] Scanning Risk Profile...`);
        }, 800);

        setTimeout(() => {
            if (chaosMode) {
                setStatus('error');
                onQuote(`[CRITICAL] 500 Internal Server Error on ${title} API`);

                // Fixer Trigger
                setTimeout(() => {
                    setStatus('remediating');
                    onQuote(`[FIXER] Detected saturation. Restarting Policy-API...`);

                    setTimeout(() => {
                        setStatus('idle');
                        onQuote(`[FIXER] System recovered. Ready for traffic.`);
                    }, 2000);
                }, 1500);

            } else {
                setStatus('analyzing');
                onQuote(`[BRAIN] Analyze User Risk: Low. Confidence: 98%.`);

                setTimeout(() => {
                    setStatus('success');
                    onQuote(`[SUCCESS] Quote Generated: Q-${Math.floor(Math.random() * 10000)}`);
                    setTimeout(() => setStatus('idle'), 3000);
                }, 1000);
            }
        }, 2000);
    };

    const variants = {
        idle: { scale: 1, borderColor: "rgba(255,255,255,0.1)" },
        checking: { scale: 1.02, borderColor: "#6366f1" },
        scanning: { scale: 1.02, borderColor: "#eab308" }, // yellow
        analyzing: { scale: 1.02, borderColor: "#a855f7" }, // purple
        success: { scale: 1.05, borderColor: "#10b981", boxShadow: "0 0 20px rgba(16, 185, 129, 0.4)" },
        error: { scale: 0.98, borderColor: "#ef4444", x: [0, -5, 5, -5, 0] },
        remediating: { scale: 1, borderColor: "#3b82f6", opacity: 0.8 },
    };

    return (
        <div
            className="glass-panel p-6 rounded-2xl border-t relative overflow-hidden cursor-pointer group"
            onClick={handleQuote}
        >
            <div className="flex justify-between items-start mb-4">
                <div className="p-3 bg-white/5 rounded-xl group-hover:bg-primary/20 transition-colors">
                    <Icon className="w-8 h-8 text-slate-200 group-hover:text-primary transition-colors" />
                </div>
                {status === 'success' && <CheckCircle2 className="text-secondary w-6 h-6" />}
                {status === 'error' && <AlertTriangle className="text-danger w-6 h-6" />}
                {status === 'remediating' && <Activity className="text-blue-400 w-6 h-6 animate-spin" />}
            </div>

            <h3 className="text-xl font-bold mb-1">{title}</h3>
            <p className="text-sm text-slate-400 mb-6">Comprehensive coverage for your peace of mind.</p>

            <button className="w-full py-3 bg-white/10 hover:bg-primary hover:text-white rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2">
                {status === 'idle' && <>Get Instant Quote <Sparkles className="w-4 h-4" /></>}
                {status === 'checking' && "Verifying..."}
                {status === 'scanning' && "Scout Scanning..."}
                {status === 'analyzing' && "Brain Analyzing..."}
                {status === 'success' && "Quote Ready!"}
                {status === 'error' && "Service Error"}
                {status === 'remediating' && "Auto-Fixing..."}
            </button>

            {/* Progress Bar for Loading States */}
            {(status === 'checking' || status === 'scanning' || status === 'analyzing') && (
                <div
                    className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-primary to-secondary transition-all duration-[2000ms]"
                    style={{ width: "100%" }}
                />
            )}
        </div>
    );
};

export default PolicyCard;
