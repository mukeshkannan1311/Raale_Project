import React from 'react';
import { ShieldAlert, ShieldCheck, HeartHandshake, Eye, Lock, FileText, CheckCircle2 } from 'lucide-react';

export const EthicsPage: React.FC = () => {
  const principles = [
    {
      title: '1. Human-in-the-Loop Verification',
      icon: HeartHandshake,
      description: 'Machine learning probability predictions assist warehouse personnel; they never automatically alter physical inventory stock without human physical verification.'
    },
    {
      title: '2. Transparent Uncertainty & Confidence',
      icon: Eye,
      description: 'Low-confidence predictions (<50%) and conflicting scan trails are explicitly flagged with uncertainty warnings, prompting manual physical audit rather than blind assignment.'
    },
    {
      title: '3. Safety System Absolute Override',
      icon: ShieldAlert,
      description: 'Operational efficiency targets NEVER override worker or driver safety constraints. Task dispatch is automatically blocked if worker workload, distance, or shift limits are exceeded.'
    },
    {
      title: '4. Restricted Zone Clearance & Security',
      icon: Lock,
      description: 'Access to Controlled Access and High Value zones requires verified security credentials. The system blocks unauthorized personnel from receiving tasks in restricted areas.'
    },
    {
      title: '5. Workload Fairness & Overload Prevention',
      icon: CheckCircle2,
      description: 'The fairness assignment engine dynamically distributes tasks based on current task count and accumulated shift distance, preventing worker burnout and task stacking.'
    },
    {
      title: '6. Full Traceability & Auditability',
      icon: FileText,
      description: 'Every model prediction, evidence feature breakdown, user verification, and location correction is permanently stored in PostgreSQL audit logs for compliance oversight.'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-cyan-400" />
          Ethics & Responsible Warehouse Operations Policy
        </h2>
        <p className="text-xs text-slate-400">
          Core ethical principles governing AI deployment, worker safety, fairness, and pharmaceutical traceability
        </p>
      </div>

      {/* Principles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {principles.map((p, idx) => {
          const Icon = p.icon;
          return (
            <div key={idx} className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-2">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="text-sm font-bold text-white">{p.title}</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed pl-12">{p.description}</p>
            </div>
          );
        })}
      </div>

      {/* Compliance Note Banner */}
      <div className="p-5 rounded-xl bg-gradient-to-r from-slate-900 to-blue-950/40 border border-blue-500/30 text-xs text-slate-300 flex items-start gap-4">
        <ShieldCheck className="w-6 h-6 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <h4 className="font-bold text-white text-sm">Pharmaceutical Controlled-Storage Compliance Notice</h4>
          <p className="mt-1 leading-relaxed text-slate-400">
            PharmaTrace operates under strict pharmaceutical GxP (Good Warehouse Practice) standards. Discrepancy resolutions must adhere to temperature-controlled chain of custody protocols. Cold storage vaccines (e.g. MED-1042) require continuous 2°C - 8°C temperature monitoring during physical relocation.
          </p>
        </div>
      </div>
    </div>
  );
};
