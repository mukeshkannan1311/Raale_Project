import React, { useEffect, useState } from 'react';
import { SearchCode, Filter, RefreshCw, ShieldCheck, AlertTriangle, ChevronRight } from 'lucide-react';
import { api } from '../services/api';
import { Discrepancy } from '../types';
import { DiscrepancyDrawer } from '../components/DiscrepancyDrawer';

export const DiscrepancyFinderPage: React.FC = () => {
  const [discrepancies, setDiscrepancies] = useState<Discrepancy[]>([]);
  const [selectedDisc, setSelectedDisc] = useState<Discrepancy | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters state
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await api.getDiscrepancies({
        priority: priorityFilter || undefined,
        status: statusFilter || undefined,
      });
      setDiscrepancies(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [priorityFilter, statusFilter]);

  const filteredDiscrepancies = discrepancies.filter((d) => {
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        d.sku.toLowerCase().includes(q) ||
        d.batch_id.toLowerCase().includes(q) ||
        d.expected_location.toLowerCase().includes(q) ||
        d.predicted_location.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <SearchCode className="w-5 h-5 text-cyan-400" />
            Inventory Discrepancy Finder Engine
          </h2>
          <p className="text-xs text-slate-400">
            Real-time candidate probability predictions based on warehouse scan trails & historical evidence
          </p>
        </div>

        <button
          onClick={loadData}
          className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Data</span>
        </button>
      </div>

      {/* Filters Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by SKU, Batch, or Bin..."
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
            <SearchCode className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          </div>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">Critical Priority</option>
            <option value="HIGH">High Priority</option>
            <option value="MEDIUM">Medium Priority</option>
            <option value="LOW">Low Priority</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="SUSPECTED">Suspected</option>
            <option value="LOCATED">Located</option>
            <option value="CORRECTED">Corrected</option>
            <option value="MISSING">Missing</option>
          </select>
        </div>

        <div className="text-xs text-slate-400 font-mono">
          Showing <span className="text-cyan-400 font-bold">{filteredDiscrepancies.length}</span> Records
        </div>
      </div>

      {/* Discrepancies Data Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3.5">SKU / Batch</th>
                <th className="p-3.5">System Location</th>
                <th className="p-3.5">Predicted Location</th>
                <th className="p-3.5">ML Confidence</th>
                <th className="p-3.5">Priority</th>
                <th className="p-3.5">Evidence Summary</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-cyan-400" />
                    Fetching discrepancy predictions...
                  </td>
                </tr>
              ) : filteredDiscrepancies.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-400">
                    No discrepancies matched the applied filters.
                  </td>
                </tr>
              ) : (
                filteredDiscrepancies.map((disc) => (
                  <tr
                    key={disc.id}
                    onClick={() => setSelectedDisc(disc)}
                    className="hover:bg-slate-800/60 cursor-pointer transition"
                  >
                    <td className="p-3.5">
                      <span className="font-mono font-bold text-white block">{disc.sku}</span>
                      <span className="text-[10px] text-slate-400">{disc.batch_id} • {disc.quantity} units</span>
                    </td>
                    <td className="p-3.5 font-mono text-slate-400">{disc.expected_location}</td>
                    <td className="p-3.5 font-mono font-bold text-emerald-400">{disc.predicted_location}</td>
                    <td className="p-3.5">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              disc.confidence >= 80 ? 'bg-emerald-400' : disc.confidence >= 50 ? 'bg-cyan-400' : 'bg-amber-400'
                            }`}
                            style={{ width: `${disc.confidence}%` }}
                          />
                        </div>
                        <span className="font-mono font-bold text-cyan-300">{disc.confidence}%</span>
                      </div>
                    </td>
                    <td className="p-3.5">
                      <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                        disc.priority === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                        disc.priority === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {disc.priority}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-300 max-w-xs truncate text-[11px]">
                      {disc.evidence_json?.[0]?.description || 'Recent scan trail activity'}
                    </td>
                    <td className="p-3.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        disc.status === 'CORRECTED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        disc.status === 'LOCATED' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' :
                        disc.status === 'MISSING' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                        'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {disc.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedDisc(disc);
                        }}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold inline-flex items-center gap-1 transition"
                      >
                        <span>Details</span>
                        <ChevronRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Discrepancy Details Drawer */}
      <DiscrepancyDrawer
        discrepancy={selectedDisc}
        onClose={() => setSelectedDisc(null)}
        onRefresh={loadData}
      />
    </div>
  );
};
