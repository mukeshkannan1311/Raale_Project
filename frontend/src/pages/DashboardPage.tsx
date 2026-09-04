import React, { useEffect, useState } from 'react';
import {
  Package, AlertTriangle, ShieldCheck, Clock, CheckCircle2, ShieldAlert,
  ArrowUpRight, ArrowDownRight, Layers, BarChart3, TrendingUp
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie
} from 'recharts';
import { api } from '../services/api';
import { DashboardSummary, Discrepancy } from '../types';
import { DemoScenarioBanner } from '../components/DemoScenarioBanner';
import { DiscrepancyDrawer } from '../components/DiscrepancyDrawer';

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [selectedDisc, setSelectedDisc] = useState<Discrepancy | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.getDashboardSummary();
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
      <div className="p-8 text-center text-slate-400 flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-sm">Loading Warehouse Location Intelligence Dashboard...</p>
      </div>
    );
  }

  const accuracyData = [
    { metric: 'Top-1 Accuracy', Baseline: data.accuracy_comparison.baseline_top1, Prototype: data.accuracy_comparison.prototype_top1 },
    { metric: 'Top-3 Accuracy', Baseline: data.accuracy_comparison.baseline_top3, Prototype: data.accuracy_comparison.prototype_top3 },
  ];

  const timeData = [
    { metric: 'Locate Time (min)', Baseline: 48.5, Prototype: data.avg_locate_time_mins },
    { metric: 'Correction Time (min)', Baseline: 72.0, Prototype: data.avg_correction_time_mins },
  ];

  const zoneData = Object.entries(data.zone_discrepancies).map(([zone, count]) => ({
    name: zone.replace('_', ' '),
    count: count
  }));

  const ZONE_COLORS = ['#38bdf8', '#34d399', '#f59e0b', '#a78bfa', '#f43f5e'];

  return (
    <div className="p-6 space-y-6">
      {/* Demo Walkthrough Banner */}
      <DemoScenarioBanner />

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Total SKUs */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium">Total Tracked SKUs</p>
            <h3 className="text-2xl font-bold text-white mt-1">{data.total_skus}</h3>
            <p className="text-[11px] text-cyan-400 mt-1 flex items-center gap-1">
              <Package className="w-3 h-3" />
              1,000+ Scan Events
            </p>
          </div>
          <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Package className="w-6 h-6" />
          </div>
        </div>

        {/* Suspected Discrepancies */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-amber-500/30 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium">Suspected Discrepancies</p>
            <h3 className="text-2xl font-bold text-amber-400 mt-1">{data.suspected_discrepancies}</h3>
            <p className="text-[11px] text-amber-300 mt-1 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              Requires Audit
            </p>
          </div>
          <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        {/* High Confidence */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium">High Confidence (&gt;80%)</p>
            <h3 className="text-2xl font-bold text-emerald-400 mt-1">{data.high_confidence_discrepancies}</h3>
            <p className="text-[11px] text-emerald-300 mt-1 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" />
              Ready for Verification
            </p>
          </div>
          <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>

        {/* Avg Locate Time */}
        <div className="p-4 rounded-xl bg-slate-900/80 border border-blue-500/30 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium">Avg Locate Time</p>
            <h3 className="text-2xl font-bold text-blue-400 mt-1">{data.avg_locate_time_mins} min</h3>
            <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1 font-semibold">
              <ArrowDownRight className="w-3.5 h-3.5" />
              70.7% Faster than Baseline
            </p>
          </div>
          <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Clock className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Baseline vs Prototype Accuracy Chart */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-200 text-sm flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                Baseline vs. PharmaTrace Prototype Accuracy (%)
              </h3>
              <p className="text-xs text-slate-400">Scikit-learn Random Forest ML vs. Latest Scan Baseline</p>
            </div>
          </div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={accuracyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="metric" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="Baseline" fill="#64748b" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Prototype" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Locate Time Reduction Chart */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-200 text-sm flex items-center gap-2">
                <Clock className="w-4 h-4 text-emerald-400" />
                Average Search & Correction Time (Minutes)
              </h3>
              <p className="text-xs text-slate-400 font-mono text-emerald-400 font-semibold">48.5 min Baseline → 14.2 min Prototype</p>
            </div>
          </div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timeData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="metric" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="Baseline" fill="#ef4444" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Prototype" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Discrepancies Table */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-slate-200 text-sm flex items-center gap-2">
              <Layers className="w-4 h-4 text-amber-400" />
              Active Warehouse Discrepancy Queue
            </h3>
            <p className="text-xs text-slate-400">Click any row to inspect calculated candidate probabilities and evidence</p>
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border border-slate-800">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3">SKU / Batch</th>
                <th className="p-3">Expected Loc</th>
                <th className="p-3">Predicted Loc</th>
                <th className="p-3">Confidence</th>
                <th className="p-3">Priority</th>
                <th className="p-3">Status</th>
                <th className="p-3">Action Required</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {data.recent_discrepancies.map((disc) => (
                <tr
                  key={disc.id}
                  onClick={() => setSelectedDisc(disc)}
                  className="hover:bg-slate-800/50 cursor-pointer transition"
                >
                  <td className="p-3">
                    <span className="font-mono font-bold text-white block">{disc.sku}</span>
                    <span className="text-[10px] text-slate-400">{disc.batch_id}</span>
                  </td>
                  <td className="p-3 font-mono text-slate-300">{disc.expected_location}</td>
                  <td className="p-3 font-mono font-bold text-emerald-400">{disc.predicted_location}</td>
                  <td className="p-3">
                    <span className="px-2 py-1 rounded bg-cyan-500/10 text-cyan-300 font-mono font-bold">
                      {disc.confidence}%
                    </span>
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                      disc.priority === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                      disc.priority === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                      'bg-blue-500/20 text-blue-400'
                    }`}>
                      {disc.priority}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium text-[10px]">
                      {disc.status}
                    </span>
                  </td>
                  <td className="p-3 text-cyan-400 text-xs font-semibold hover:underline">
                    Inspect Evidence →
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Discrepancy Detail Drawer */}
      <DiscrepancyDrawer
        discrepancy={selectedDisc}
        onClose={() => setSelectedDisc(null)}
        onRefresh={loadData}
      />
    </div>
  );
};
