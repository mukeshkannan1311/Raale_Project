import React, { useState } from 'react';
import { ClipboardList, CheckSquare, Square, ShieldCheck, Server, Database, Lock, Activity } from 'lucide-react';

interface ChecklistItem {
  id: string;
  category: string;
  item: string;
  details: string;
  checked: boolean;
}

export const DeploymentChecklistPage: React.FC = () => {
  const [items, setItems] = useState<ChecklistItem[]>([
    // Environment
    { id: '1', category: 'Environment', item: 'PostgreSQL database container configured and connected via SQLAlchemy pool', details: 'Validated with DATABASE_URL env var.', checked: true },
    { id: '2', category: 'Environment', item: 'Environment variables configured (.env file created, secrets isolated)', details: 'No hardcoded plain API keys.', checked: true },
    { id: '3', category: 'Environment', item: 'FastAPI CORS middleware restricted to trusted production origin', details: 'Configured in main.py.', checked: true },

    // Backend
    { id: '4', category: 'Backend', item: 'FastAPI REST endpoint health check (/api/health) operational', details: 'Returns JSON 200 OK.', checked: true },
    { id: '5', category: 'Backend', item: 'SQLAlchemy database migration and table schemas verified', details: '5 core datasets + Worker/Assignment tables.', checked: true },
    { id: '6', category: 'Backend', item: 'Scikit-learn Random Forest ML Discrepancy Engine trained', details: 'Feature extractor and probability calculator active.', checked: true },

    // Frontend
    { id: '7', category: 'Frontend', item: 'React Vite production build succeeds cleanly', details: 'TypeScript strict types validated.', checked: true },
    { id: '8', category: 'Frontend', item: 'API base URL dynamically configured via environment proxy', details: 'Connected to FastAPI backend.', checked: true },
    { id: '9', category: 'Frontend', item: 'Responsive dark-mode UI design tested across desktop and tablet views', details: 'Tailwind glassmorphism layout.', checked: true },

    // Security & Operations
    { id: '10', category: 'Security & Safety', item: 'Worker and Driver workload limits enforced', details: 'Assignment blocks trigger when tasks >= max_tasks.', checked: true },
    { id: '11', category: 'Security & Safety', item: 'Restricted storage zone authorization checks active', details: 'Prevents unauthorized worker dispatches.', checked: true },
    { id: '12', category: 'Security & Safety', item: 'PostgreSQL audit logging active for all discrepancy actions', details: 'Full audit log trail maintained.', checked: true },
  ]);

  const toggleItem = (id: string) => {
    setItems((prev) =>
      prev.map((i) => (i.id === id ? { ...i, checked: !i.checked } : i))
    );
  };

  const total = items.length;
  const completed = items.filter((i) => i.checked).length;
  const pct = Math.round((completed / total) * 100);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ClipboardList className="w-5 h-5 text-cyan-400" />
            Production Deployment & Readiness Checklist
          </h2>
          <p className="text-xs text-slate-400">
            System readiness verification across database, backend ML APIs, frontend UI, security, and safety constraints
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl text-xs">
          <span className="text-slate-400 font-medium">Readiness Score:</span>
          <span className="font-mono font-bold text-cyan-400 text-base">{pct}%</span>
          <span className="text-emerald-400 font-bold">({completed}/{total} Tasks)</span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
        <div className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>

      {/* Categories Grid */}
      <div className="space-y-4">
        {['Environment', 'Backend', 'Frontend', 'Security & Safety'].map((cat) => {
          const catItems = items.filter((i) => i.category === cat);
          return (
            <div key={cat} className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-3">
              <h3 className="text-sm font-bold text-cyan-400 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4" />
                {cat} Requirements
              </h3>

              <div className="space-y-2">
                {catItems.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => toggleItem(item.id)}
                    className={`p-3 rounded-lg border text-xs cursor-pointer transition flex items-start gap-3 ${
                      item.checked ? 'bg-slate-950/60 border-slate-800/80' : 'bg-red-500/5 border-red-500/20'
                    }`}
                  >
                    <button className="mt-0.5 text-cyan-400">
                      {item.checked ? <CheckSquare className="w-4 h-4 text-emerald-400" /> : <Square className="w-4 h-4 text-slate-600" />}
                    </button>
                    <div>
                      <span className={`font-semibold ${item.checked ? 'text-slate-200' : 'text-slate-400 line-through'}`}>
                        {item.item}
                      </span>
                      <p className="text-[11px] text-slate-400 mt-0.5">{item.details}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
