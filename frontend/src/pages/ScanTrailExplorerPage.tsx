import React, { useState, useEffect } from 'react';
import { GitCommit, Search, AlertTriangle, ArrowRight, CheckCircle2, User, Package, Calendar } from 'lucide-react';
import { api } from '../services/api';
import { ScanTrail } from '../types';

export const ScanTrailExplorerPage: React.FC = () => {
  const [sku, setSku] = useState<string>('MED-1042');
  const [trail, setTrail] = useState<ScanTrail | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchTrail = async (searchSku: string) => {
    setLoading(true);
    try {
      const res = await api.getScanTrail(searchSku);
      setTrail(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrail(sku);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (sku.trim()) {
      fetchTrail(sku.trim());
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <GitCommit className="w-5 h-5 text-cyan-400" />
            Scan Trail Audit Timeline Explorer
          </h2>
          <p className="text-xs text-slate-400">
            Audit historic put-aways, moves, pick failures, and cycle counts to detect unrecorded physical moves
          </p>
        </div>

        {/* SKU Search Input */}
        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <input
              type="text"
              value={sku}
              onChange={(e) => setSku(e.target.value)}
              placeholder="Enter SKU e.g. MED-1042..."
              className="pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono font-bold"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition"
          >
            {loading ? 'Searching...' : 'Explore Trail'}
          </button>
        </form>
      </div>

      {/* Preset Quick SKU Pills */}
      <div className="flex items-center gap-2 text-xs">
        <span className="text-slate-400">Preset Demo SKUs:</span>
        {['MED-1042', 'MED-1088', 'MED-1004', 'MED-1019'].map((item) => (
          <button
            key={item}
            onClick={() => {
              setSku(item);
              fetchTrail(item);
            }}
            className={`px-2.5 py-1 rounded-full font-mono text-[11px] transition ${
              sku === item ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold' : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      {/* Timeline Card Container */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-400">
            <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading scan trail history for {sku}...
          </div>
        ) : !trail || trail.timeline.length === 0 ? (
          <div className="p-8 text-center text-slate-400">
            No scan events found for SKU {sku}.
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <span className="text-sm font-bold text-white font-mono">SKU: {trail.sku}</span>
              <span className="text-xs text-slate-400 font-mono">{trail.total_events} Total Trail Events</span>
            </div>

            {/* Chronological Timeline */}
            <div className="relative pl-6 space-y-8 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
              {trail.timeline.map((event, idx) => (
                <div key={event.id || idx} className="relative flex items-start justify-between gap-4">
                  {/* Timeline Dot */}
                  <div className={`absolute -left-6 top-1 w-5 h-5 rounded-full border-2 flex items-center justify-center bg-slate-950 ${
                    event.suspicious ? 'border-amber-400 text-amber-400' : 'border-cyan-400 text-cyan-400'
                  }`}>
                    <div className={`w-2 h-2 rounded-full ${event.suspicious ? 'bg-amber-400 animate-ping' : 'bg-cyan-400'}`} />
                  </div>

                  {/* Event Detail Card */}
                  <div className={`flex-1 p-4 rounded-xl border text-xs transition ${
                    event.suspicious ? 'bg-amber-500/5 border-amber-500/30' : 'bg-slate-950/60 border-slate-800'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                          event.event_type === 'PUT_AWAY' ? 'bg-blue-500/20 text-blue-400' :
                          event.event_type === 'MOVE_EVENT' ? 'bg-purple-500/20 text-purple-400' :
                          event.event_type === 'PICK_FAILURE' ? 'bg-red-500/20 text-red-400' :
                          'bg-emerald-500/20 text-emerald-400'
                        }`}>
                          {event.event_type}
                        </span>

                        {event.suspicious && (
                          <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold text-[10px] flex items-center gap-1 border border-amber-500/30">
                            <AlertTriangle className="w-3 h-3" />
                            Suspicious Discrepancy Flag
                          </span>
                        )}
                      </div>

                      <span className="text-slate-400 font-mono text-[11px] flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-slate-500" />
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                    </div>

                    <p className="text-sm font-semibold text-slate-200 mt-1">{event.details}</p>

                    <div className="flex items-center gap-6 mt-3 text-[11px] text-slate-400 border-t border-slate-800/60 pt-2">
                      <span className="flex items-center gap-1 font-mono text-cyan-300">
                        <Package className="w-3 h-3 text-slate-500" />
                        Location: {event.location}
                      </span>

                      <span className="flex items-center gap-1 font-mono">
                        <User className="w-3 h-3 text-slate-500" />
                        Worker: {event.worker_id}
                      </span>

                      {event.quantity > 0 && (
                        <span>Quantity: <strong className="text-slate-200">{event.quantity}</strong> units</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
