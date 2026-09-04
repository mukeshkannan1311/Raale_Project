import React, { useState, useEffect } from 'react';
import { FlaskConical, Play, RefreshCw, CheckCircle2, XCircle, TrendingUp, ShieldCheck, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { ExperimentComparison } from '../types';

export const ExperimentsPage: React.FC = () => {
  const [data, setData] = useState<ExperimentComparison | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.getExperimentResults();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunExperiment = async () => {
    setLoading(true);
    try {
      const res = await api.runExperiment();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading || !data) {
    return (
      <div className="p-8 text-center text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-cyan-400" />
        Running ML Experiment Evaluation across seed dataset...
      </div>
    );
  }

  const { baseline, target, prototype, improvement_pct, error_analysis } = data;

  const metricsTable = [
    { metric: 'Top-1 Location Accuracy', baseline: `${baseline.top1_accuracy}%`, target: `${target.top1_accuracy}%`, prototype: `${prototype.top1_accuracy}%`, status: prototype.top1_accuracy >= target.top1_accuracy ? 'TARGET MET' : 'TARGET NOT ACHIEVED' },
    { metric: 'Top-3 Location Accuracy', baseline: `${baseline.top3_accuracy}%`, target: `${target.top3_accuracy}%`, prototype: `${prototype.top3_accuracy}%`, status: prototype.top3_accuracy >= target.top3_accuracy ? 'TARGET MET' : 'TARGET NOT ACHIEVED' },
    { metric: 'False Positive Rate', baseline: `${baseline.false_positive_rate}%`, target: `<${target.false_positive_rate}%`, prototype: `${prototype.false_positive_rate}%`, status: prototype.false_positive_rate <= target.false_positive_rate ? 'TARGET MET' : 'TARGET NOT ACHIEVED' },
    { metric: 'Average Time to Locate (mins)', baseline: `${baseline.avg_locate_time_mins} min`, target: `<${target.avg_locate_time_mins} min`, prototype: `${prototype.avg_locate_time_mins} min`, status: prototype.avg_locate_time_mins <= target.avg_locate_time_mins ? 'TARGET MET' : 'TARGET NOT ACHIEVED' },
    { metric: 'Average Time to Correct (mins)', baseline: `${baseline.avg_correction_time_mins} min`, target: `<${target.avg_correction_time_mins} min`, prototype: `${prototype.avg_correction_time_mins} min`, status: prototype.avg_correction_time_mins <= target.avg_correction_time_mins ? 'TARGET MET' : 'TARGET NOT ACHIEVED' },
    { metric: 'Missing Stock Located %', baseline: `${baseline.missing_stock_located_pct}%`, target: `${target.missing_stock_located_pct}%`, prototype: `${prototype.missing_stock_located_pct}%`, status: prototype.missing_stock_located_pct >= target.missing_stock_located_pct ? 'TARGET MET' : 'TARGET NOT ACHIEVED' },
    { metric: 'Unsafe Assignment Count', baseline: `${baseline.unsafe_assignment_count}`, target: '0', prototype: `${prototype.unsafe_assignment_count}`, status: prototype.unsafe_assignment_count === 0 ? 'TARGET MET' : 'SAFETY VIOLATION' },
    { metric: 'Worker Workload Violations', baseline: `${baseline.worker_workload_violations}`, target: '0', prototype: `${prototype.worker_workload_violations}`, status: prototype.worker_workload_violations === 0 ? 'TARGET MET' : 'SAFETY VIOLATION' },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-cyan-400" />
            Baseline vs. PharmaTrace Experiment Benchmarks
          </h2>
          <p className="text-xs text-slate-400">
            Empirical evaluation against ground-truth database records (Scikit-learn RF vs. Latest Scan Baseline)
          </p>
        </div>

        <button
          onClick={handleRunExperiment}
          className="px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold text-xs flex items-center gap-2 transition shadow-lg shadow-cyan-500/20"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>Execute Experiment Suite</span>
        </button>
      </div>

      {/* Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30">
          <p className="text-xs text-slate-400 font-medium">Top-1 Location Accuracy Gain</p>
          <h3 className="text-2xl font-bold text-emerald-400 mt-1">+{improvement_pct.top1_accuracy}%</h3>
          <p className="text-[11px] text-emerald-300 mt-1">42.5% Baseline → {prototype.top1_accuracy}% Prototype</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-cyan-500/30">
          <p className="text-xs text-slate-400 font-medium">Locate Time Reduction</p>
          <h3 className="text-2xl font-bold text-cyan-400 mt-1">{improvement_pct.locate_time_reduction}% Faster</h3>
          <p className="text-[11px] text-cyan-300 mt-1">48.5 min → {prototype.avg_locate_time_mins} min</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-blue-500/30">
          <p className="text-xs text-slate-400 font-medium">Missing Stock Recovery</p>
          <h3 className="text-2xl font-bold text-blue-400 mt-1">+{improvement_pct.stock_located_gain}% Located</h3>
          <p className="text-[11px] text-blue-300 mt-1">42.0% Baseline → {prototype.missing_stock_located_pct}% Prototype</p>
        </div>
      </div>

      {/* Main Comparison Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Baseline vs Target vs Prototype Metric Matrix</h3>
          <span className="text-xs text-slate-400 font-mono">Calculated on 100+ SKUs / 1,000+ Events</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3.5">Metric</th>
                <th className="p-3.5">Baseline</th>
                <th className="p-3.5">Target</th>
                <th className="p-3.5">PharmaTrace Prototype</th>
                <th className="p-3.5 text-right">Result Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {metricsTable.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="p-3.5 font-sans font-semibold text-slate-200">{row.metric}</td>
                  <td className="p-3.5 text-slate-400">{row.baseline}</td>
                  <td className="p-3.5 text-slate-400">{row.target}</td>
                  <td className="p-3.5 font-bold text-cyan-300">{row.prototype}</td>
                  <td className="p-3.5 text-right font-sans">
                    {row.status === 'TARGET MET' ? (
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">
                        {row.status}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 text-[10px] font-bold border border-amber-500/20">
                        {row.status}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Error Analysis Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Model Error Analysis & Discrepancy Failure Categorization
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Diagnosing root cause when predictions diverge from ground truth</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3.5">SKU</th>
                <th className="p-3.5">Actual Location</th>
                <th className="p-3.5">Baseline Prediction</th>
                <th className="p-3.5">Prototype Prediction</th>
                <th className="p-3.5">Correct?</th>
                <th className="p-3.5">Failure Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {error_analysis.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="p-3.5 font-bold text-white">{item.sku}</td>
                  <td className="p-3.5 text-emerald-400">{item.actual_location}</td>
                  <td className="p-3.5 text-slate-400">{item.baseline_prediction}</td>
                  <td className="p-3.5 text-cyan-300">{item.prototype_prediction}</td>
                  <td className="p-3.5 font-sans">
                    {item.is_correct ? (
                      <span className="text-emerald-400 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Yes
                      </span>
                    ) : (
                      <span className="text-red-400 font-bold flex items-center gap-1">
                        <XCircle className="w-3.5 h-3.5" /> No
                      </span>
                    )}
                  </td>
                  <td className="p-3.5 font-sans text-amber-300 text-[11px]">{item.failure_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
