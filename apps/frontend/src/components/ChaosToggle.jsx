import React from 'react';
import { Switch } from '@headlessui/react' // Can implement manual toggle if headlessui not avail, using simple div
// Wait, I shouldn't introduce headlessui unless I install it. I'll build a custom one.

const ChaosToggle = ({ enabled, setEnabled }) => {
    return (
        <div className="flex items-center gap-3 bg-red-900/20 px-4 py-2 rounded-full border border-red-500/20">
            <span className={`text-xs font-bold uppercase tracking-wider ${enabled ? 'text-red-400' : 'text-slate-500'}`}>
                Chaos Mode
            </span>
            <button
                className={`w-12 h-6 rounded-full p-1 transition-colors duration-300 focus:outline-none ${enabled ? 'bg-red-500' : 'bg-slate-700'}`}
                onClick={() => setEnabled(!enabled)}
            >
                <div
                    className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${enabled ? 'translate-x-6' : 'translate-x-0'}`}
                />
            </button>
        </div>
    );
};

export default ChaosToggle;
