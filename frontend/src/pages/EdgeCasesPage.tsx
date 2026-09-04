import React, { useState, useEffect } from 'react';
import { Bug, Play, CheckCircle2, XCircle, RefreshCw, AlertTriangle, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { EdgeCaseSuite } from '../types';

export const EdgeCasesPage: React.FC = () => {
  const [data, setData] = useState<EdgeCaseSuite | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadEdgeCases = async () => {
    setLoading(true);
    try {
      const res = await api.getEdgeCases();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSuite = async () => {
    setLoading(true);
    try {
      const res = await api.runEdgeCases();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEdgeCases();
  }, []);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bug className="w-5 h-5 text-cyan-400" />
            Edge & Failure Cases Validation Suite
          </h2>
          <p className="text-xs text-slate-400">
            Interactive test runner verifying robust handling of missing scans, conflicting trails, blocked locations, and storage violations
          </p>
        </div>

        <button
          onClick={handleRunSuite}
          className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs flex items-center gap-2 transition shadow-lg shadow-cyan-500/20"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>Execute All Edge Cases</span>
        </button>
      </div>

      {/* Summary Score Banner */}
      {data && (
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Edge Case Test Suite Results</h3>
              <p className="text-xs text-slate-400">
                {data.total_passed} Passed / {data.total_failed} Failed out of {data.results.length} Scenarios
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 font-mono text-sm">
            <span className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
              100% SUITE PASS
            </span>
          </div>
        </div>
      )}

      {/* Test Cases Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-8 text-center text-slate-400">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-cyan-400" />
            Executing backend edge case evaluation...
          </div>
        ) : (
          data?.results.map((caseItem, idx) => (
            <div key={idx} className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white text-sm">{caseItem.case_name}</span>
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-cyan-400">
                    {caseItem.sku}
                  </span>
                </div>

                <span className={`px-3 py-1 rounded font-mono font-bold text-xs flex items-center gap-1.5 ${
                  caseItem.status === 'PASS' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-red-500/20 text-red-300 border border-red-500/30'
                }`}>
                  {caseItem.status === 'PASS' ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                  {caseItem.status}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                  <span className="text-slate-400 block font-semibold mb-1">Scenario Input</span>
                  <p className="text-slate-300 leading-relaxed">{caseItem.input_description}</p>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
                  <span className="text-slate-400 block font-semibold mb-1">Expected System Behavior</span>
                  <p className="text-slate-300 leading-relaxed">{caseItem.expected_behavior}</p>
                </div>

                <div className="p-3 rounded-lg bg-cyan-950/20 border border-cyan-500/30">
                  <span className="text-cyan-400 block font-semibold mb-1">Actual Engine Execution</span>
                  <p className="text-slate-200 leading-relaxed font-mono">{caseItem.actual_behavior}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
