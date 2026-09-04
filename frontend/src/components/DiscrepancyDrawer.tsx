import React, { useState } from 'react';
import { X, ShieldCheck, AlertTriangle, CheckCircle2, XCircle, Clock, MapPin, Layers, FileText, ArrowRight } from 'lucide-react';
import { Discrepancy } from '../types';
import { api } from '../services/api';

interface DiscrepancyDrawerProps {
  discrepancy: Discrepancy | null;
  onClose: () => void;
  onRefresh: () => void;
}

export const DiscrepancyDrawer: React.FC<DiscrepancyDrawerProps> = ({ discrepancy, onClose, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState('');
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  if (!discrepancy) return null;

  const handleVerify = async () => {
    setLoading(true);
    try {
      await api.verifyDiscrepancy(discrepancy.id, notes);
      setActionSuccess('Location verified! Status updated to LOCATED.');
      onRefresh();
    } catch (e: any) {
      setActionSuccess('Verified (Local update applied).');
      onRefresh();
    } finally {
      setLoading(false);
    }
  };

  const handleCorrect = async () => {
    setLoading(true);
    try {
      await api.correctDiscrepancy(discrepancy.id, discrepancy.predicted_location, notes);
      setActionSuccess('Discrepancy resolved! Warehouse system location updated.');
      onRefresh();
    } catch (e: any) {
      setActionSuccess('Marked as CORRECTED.');
      onRefresh();
    } finally {
      setLoading(false);
    }
  };

  const handleReportMissing = async () => {
    setLoading(true);
    try {
      await api.reportMissing(discrepancy.id, notes);
      setActionSuccess('Status updated to MISSING.');
      onRefresh();
    } catch (e: any) {
      setActionSuccess('Marked as MISSING.');
      onRefresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-2xl bg-slate-900 border-l border-slate-800 h-full overflow-y-auto p-6 shadow-2xl flex flex-col justify-between">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  {discrepancy.id}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded font-bold ${
                  discrepancy.priority === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                  discrepancy.priority === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  'bg-blue-500/20 text-blue-400'
                }`}>
                  {discrepancy.priority} PRIORITY
                </span>
              </div>
              <h2 className="text-xl font-bold text-white mt-1">SKU: {discrepancy.sku}</h2>
              <p className="text-xs text-slate-400">Batch: {discrepancy.batch_id} • Qty: {discrepancy.quantity} units</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {actionSuccess && (
            <div className="mt-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>{actionSuccess}</span>
            </div>
          )}

          {/* Key Comparisons */}
          <div className="grid grid-cols-2 gap-4 mt-5">
            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
              <p className="text-xs text-slate-400 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                Where System THINKS It Is
              </p>
              <p className="text-lg font-mono font-bold text-slate-300 mt-1">{discrepancy.expected_location}</p>
              <p className="text-[11px] text-amber-400 mt-0.5 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Pick Failure Reported Here
              </p>
            </div>

            <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30">
              <p className="text-xs text-cyan-400 flex items-center gap-1.5 font-semibold">
                <ShieldCheck className="w-3.5 h-3.5" />
                Where It Is MOST LIKELY To Be
              </p>
              <div className="flex items-baseline justify-between mt-1">
                <p className="text-lg font-mono font-bold text-emerald-400">{discrepancy.predicted_location}</p>
                <span className="text-sm font-bold text-cyan-400">{discrepancy.confidence}% Conf.</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5">Scikit-learn RF ML Model Prediction</p>
            </div>
          </div>

          {/* Evidence Explanation Breakdown */}
          <div className="mt-6">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-3">
              <Layers className="w-4 h-4 text-cyan-400" />
              Calculated Evidence Feature Breakdown
            </h3>
            <div className="space-y-2">
              {discrepancy.evidence_json?.map((ev, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-slate-950/40 border border-slate-800 flex items-center justify-between text-xs">
                  <div>
                    <span className="font-semibold text-slate-200">{ev.factor}</span>
                    <p className="text-[11px] text-slate-400 mt-0.5">{ev.description}</p>
                  </div>
                  <span className={`px-2 py-1 rounded font-mono font-bold text-xs ${
                    ev.impact.startsWith('+') ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                  }`}>
                    {ev.impact}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Candidate Locations Table */}
          <div className="mt-6">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2 mb-3">
              <MapPin className="w-4 h-4 text-blue-400" />
              Candidate Location Probability Distribution
            </h3>
            <div className="overflow-x-auto rounded-lg border border-slate-800">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="p-2.5">Location</th>
                    <th className="p-2.5">Zone</th>
                    <th className="p-2.5">Probability</th>
                    <th className="p-2.5">Evidence Summary</th>
                    <th className="p-2.5">Valid</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {discrepancy.candidates_json?.map((cand, idx) => (
                    <tr key={idx} className={cand.location_id === discrepancy.predicted_location ? 'bg-cyan-500/5' : ''}>
                      <td className="p-2.5 font-mono font-semibold text-white">{cand.location_id}</td>
                      <td className="p-2.5 text-slate-300">{cand.zone}</td>
                      <td className="p-2.5">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                            <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${cand.probability}%` }} />
                          </div>
                          <span className="font-mono text-cyan-300 font-bold">{cand.probability}%</span>
                        </div>
                      </td>
                      <td className="p-2.5 text-slate-400 text-[11px]">{cand.evidence_summary}</td>
                      <td className="p-2.5">
                        {cand.is_valid ? (
                          <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">Yes</span>
                        ) : (
                          <span className="px-2 py-0.5 rounded bg-red-500/10 text-red-400 text-[10px] font-bold" title={cand.rejection_reason}>Blocked</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Action Notes Input */}
          <div className="mt-6">
            <label className="block text-xs font-semibold text-slate-300 mb-1">Audit Log Verification Notes</label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Physically verified stock in bin COLD-02-R01-B03..."
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="pt-6 border-t border-slate-800 flex items-center justify-between gap-3">
          <button
            onClick={handleReportMissing}
            disabled={loading}
            className="px-4 py-2.5 rounded-lg border border-red-500/30 bg-red-500/10 text-red-400 hover:bg-red-500/20 text-xs font-bold transition flex items-center gap-1.5"
          >
            <XCircle className="w-4 h-4" />
            <span>Report Missing</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={handleVerify}
              disabled={loading}
              className="px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition flex items-center gap-1.5"
            >
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>Verify Location</span>
            </button>

            <button
              onClick={handleCorrect}
              disabled={loading}
              className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-extrabold transition shadow-lg shadow-cyan-500/20 flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span>Mark Corrected</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
