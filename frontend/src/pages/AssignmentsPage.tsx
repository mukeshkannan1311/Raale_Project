import React, { useState, useEffect } from 'react';
import { Users, ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle2, UserCheck, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { FairnessWorkerRow, Discrepancy } from '../types';

export const AssignmentsPage: React.FC = () => {
  const [fairnessRows, setFairnessRows] = useState<FairnessWorkerRow[]>([]);
  const [discrepancies, setDiscrepancies] = useState<Discrepancy[]>([]);
  const [selectedDiscId, setSelectedDiscId] = useState<string>('DISC-MED-1042');
  const [loading, setLoading] = useState<boolean>(true);
  const [assigning, setAssigning] = useState<boolean>(false);
  const [assignResult, setAssignResult] = useState<{ success: boolean; msg: string } | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const discs = await api.getDiscrepancies();
      setDiscrepancies(discs);
      const targetId = selectedDiscId || (discs.length > 0 ? discs[0].id : 'DISC-MED-1042');
      const panel = await api.getFairnessPanel(targetId);
      setFairnessRows(panel);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedDiscId]);

  const handleAssign = async (workerId: string) => {
    setAssigning(true);
    setAssignResult(null);
    try {
      await api.createAssignment(selectedDiscId, workerId, 'Dispatched via Fairness Engine');
      setAssignResult({ success: true, msg: `Task dispatched successfully to worker ${workerId}.` });
      loadData();
    } catch (e: any) {
      const errorDetail = e?.response?.data?.detail || 'Assignment blocked due to workload/safety constraint.';
      setAssignResult({ success: false, msg: errorDetail });
    } finally {
      setAssigning(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-cyan-400" />
            Fairness-Aware Task Assignment & Safety Guard System
          </h2>
          <p className="text-xs text-slate-400">
            Balancing operational speed, worker workload limits, shift statuses, and security clearance
          </p>
        </div>

        <button
          onClick={loadData}
          className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-eval Fairness</span>
        </button>
      </div>

      {/* Target Discrepancy Selector */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <label className="text-xs font-semibold text-slate-300 whitespace-nowrap">Target Discrepancy Task:</label>
          <select
            value={selectedDiscId}
            onChange={(e) => setSelectedDiscId(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono font-bold text-cyan-400 focus:outline-none focus:border-cyan-500"
          >
            {discrepancies.map((d) => (
              <option key={d.id} value={d.id}>
                {d.id} — SKU {d.sku} ({d.priority} Priority, Pred: {d.predicted_location})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Assignment Feedback Message */}
      {assignResult && (
        <div className={`p-4 rounded-xl border text-xs flex items-center gap-3 ${
          assignResult.success ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-red-500/10 border-red-500/40 text-red-300'
        }`}>
          {assignResult.success ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <ShieldAlert className="w-5 h-5 shrink-0" />}
          <div>
            <p className="font-bold text-sm">{assignResult.success ? 'Assignment Confirmed' : 'Safety Constraint Enforced'}</p>
            <p className="text-xs mt-0.5">{assignResult.msg}</p>
          </div>
        </div>
      )}

      {/* Fairness & Workload Evaluation Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-emerald-400" />
            Worker Workload & Fairness Score Matrix
          </h3>
          <span className="text-xs text-slate-400">Ranked by Fairness Score</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3.5">Worker</th>
                <th className="p-3.5">Role</th>
                <th className="p-3.5">Tasks / Max</th>
                <th className="p-3.5">Shift Distance</th>
                <th className="p-3.5">Workload %</th>
                <th className="p-3.5">Zone Authorization</th>
                <th className="p-3.5">Fairness Score</th>
                <th className="p-3.5">Safety Status</th>
                <th className="p-3.5 text-right">Dispatch</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {fairnessRows.map((row) => (
                <tr key={row.worker_id} className={row.eligible ? 'hover:bg-slate-800/40' : 'bg-red-500/5 opacity-75'}>
                  <td className="p-3.5">
                    <span className="font-bold text-white block">{row.name}</span>
                    <span className="font-mono text-[10px] text-slate-400">{row.worker_id}</span>
                  </td>
                  <td className="p-3.5 text-slate-300">{row.role}</td>
                  <td className="p-3.5 font-mono">
                    <span className={row.current_tasks >= row.max_tasks ? 'text-red-400 font-bold' : 'text-slate-200'}>
                      {row.current_tasks} / {row.max_tasks}
                    </span>
                  </td>
                  <td className="p-3.5 font-mono text-slate-300">{row.current_distance_km} / {row.max_distance_km} km</td>
                  <td className="p-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${row.workload_pct >= 80 ? 'bg-red-400' : 'bg-cyan-400'}`}
                          style={{ width: `${row.workload_pct}%` }}
                        />
                      </div>
                      <span className="font-mono font-bold text-slate-300">{row.workload_pct}%</span>
                    </div>
                  </td>
                  <td className="p-3.5 text-slate-300 text-[11px] max-w-xs truncate">{row.zone_authorization}</td>
                  <td className="p-3.5 font-mono font-bold text-cyan-400">{row.fairness_score}</td>
                  <td className="p-3.5">
                    {row.eligible ? (
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">
                        Eligible
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-red-500/10 text-red-400 text-[10px] font-bold border border-red-500/20" title={row.reason}>
                        Blocked
                      </span>
                    )}
                  </td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={() => handleAssign(row.worker_id)}
                      disabled={assigning}
                      className={`px-3 py-1 rounded text-xs font-bold transition ${
                        row.eligible
                          ? 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-sm'
                          : 'bg-slate-800 text-slate-500 border border-slate-700 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30'
                      }`}
                    >
                      Assign Task
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
