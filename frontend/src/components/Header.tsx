import React from 'react';
import { Pill, Activity, ShieldCheck, Bell, Search, User } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="h-16 bg-slate-900/90 border-b border-slate-800 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 p-0.5 shadow-lg shadow-cyan-500/20">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <Pill className="w-5 h-5 text-cyan-400 transform -rotate-45" />
          </div>
        </div>
        <div>
          <h1 className="font-bold text-lg text-white flex items-center gap-2">
            PharmaTrace
            <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-medium">
              v1.0 Operational
            </span>
          </h1>
          <p className="text-xs text-slate-400">Inventory Location Discrepancy Finder Engine</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* ML Engine Status Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <Activity className="w-3.5 h-3.5 animate-pulse" />
          <span>ML Probability Engine Active</span>
        </div>

        {/* Safety System Guard Badge */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Safety System Enforced</span>
        </div>

        {/* User Profile */}
        <div className="flex items-center gap-3 pl-4 border-l border-slate-800">
          <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400 font-semibold text-sm">
            OP
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-medium text-slate-200">Ops Supervisor</p>
            <p className="text-[10px] text-slate-400">Zone Lead</p>
          </div>
        </div>
      </div>
    </header>
  );
};
