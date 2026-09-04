import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  SearchCode,
  GitCommit,
  Grid,
  Users,
  FlaskConical,
  Bug,
  CheckCircle2,
  ShieldAlert,
  ClipboardList,
  ChevronRight
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/discrepancies', label: 'Discrepancy Finder', icon: SearchCode },
  { path: '/scan-trails', label: 'Scan Trails', icon: GitCommit },
  { path: '/warehouse-map', label: 'Warehouse Map', icon: Grid },
  { path: '/assignments', label: 'Assignments & Safety', icon: Users },
  { path: '/experiments', label: 'Experiments', icon: FlaskConical },
  { path: '/edge-cases', label: 'Edge Cases Test Harness', icon: Bug },
  { path: '/validation', label: 'Stakeholder Validation', icon: CheckCircle2 },
  { path: '/ethics', label: 'Ethics & Responsible Ops', icon: ShieldAlert },
  { path: '/checklist', label: 'Deployment Checklist', icon: ClipboardList },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-slate-900/60 border-r border-slate-800 flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16 shrink-0">
      <div className="p-3 space-y-1 overflow-y-auto">
        <p className="px-3 py-2 text-[11px] font-bold tracking-wider text-slate-400 uppercase">
          Warehouse Operations
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </div>
              <ChevronRight className="w-3.5 h-3.5 opacity-40" />
            </NavLink>
          );
        })}
      </div>

      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs">
          <p className="font-semibold text-slate-300">PharmaTrace Engine</p>
          <p className="text-slate-400 mt-0.5 text-[11px]">PostgreSQL + RandomForest ML</p>
          <div className="mt-2 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-[10px] text-emerald-400 font-mono">ALL SYSTEMS NOMINAL</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
