import React, { useEffect, useRef } from 'react';

const AgentTerminal = ({ logs, title }) => {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div className="glass-panel rounded-2xl p-0 overflow-hidden flex flex-col h-[500px]">
            <div className="bg-white/5 p-4 border-b border-white/10 flex justify-between items-center">
                <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/50" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                    <div className="w-3 h-3 rounded-full bg-green-500/50" />
                </div>
                <span className="text-xs font-mono text-slate-400 capitalize">{title || 'AGENT FEED // LIVE'}</span>
            </div>

            <div className="flex-1 p-4 overflow-y-auto font-mono text-sm space-y-2 relative">
                {logs.map((log, i) => (
                    <div
                        key={log.id}
                        className={`flex gap-3 pb-2 border-l-2 pl-3 ${log.msg.includes('[CRITICAL]') || log.msg.includes('Error') ? 'border-red-500 text-red-200 bg-red-500/5' :
                            log.msg.includes('[FIXER]') ? 'border-blue-500 text-blue-200' :
                                log.msg.includes('[SUCCESS]') ? 'border-green-500 text-green-200' :
                                    log.msg.includes('[SCOUT]') ? 'border-yellow-500 text-yellow-100' :
                                        log.msg.includes('[BRAIN]') ? 'border-purple-500 text-purple-200' :
                                            'border-slate-700 text-slate-400'
                            }`}
                    >
                        <span className="opacity-50 text-xs mt-[2px]">{log.timestamp}</span>
                        <span>{log.msg}</span>
                        {log.traceId && (
                            <a href="#" className="hidden group-hover:block ml-auto text-xs text-primary underline">
                                {log.traceId}
                            </a>
                        )}
                    </div>
                ))}
                <div ref={bottomRef} />

                {/* Scanline Effect */}
                <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-white/5 to-transparent h-[5px] w-full animate-scan" />
            </div>
        </div>
    );
};

export default AgentTerminal;
