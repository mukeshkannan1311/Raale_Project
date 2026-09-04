import React, { useState, useEffect } from 'react';
import { Grid, ShieldAlert, CheckCircle2, Lock, AlertTriangle, Layers, Thermometer, Box } from 'lucide-react';
import { api } from '../services/api';
import { LocationMaster } from '../types';

export const WarehouseMapPage: React.FC = () => {
  const [locations, setLocations] = useState<LocationMaster[]>([]);
  const [selectedZone, setSelectedZone] = useState<string>('');
  const [selectedLoc, setSelectedLoc] = useState<LocationMaster | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchLocations = async () => {
      setLoading(true);
      try {
        const res = await api.getLocations(selectedZone || undefined);
        setLocations(res);
        if (res.length > 0) setSelectedLoc(res[0]);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchLocations();
  }, [selectedZone]);

  const zones = ['ALL ZONES', 'AMBIENT', 'COLD_STORAGE', 'QUARANTINE', 'HIGH_VALUE', 'CONTROLLED_ACCESS'];

  const getStatusColor = (loc: LocationMaster) => {
    if (loc.status === 'BLOCKED') return 'bg-red-500/20 border-red-500/50 text-red-400';
    if (loc.location_id === 'COLD-02-R01-B03') return 'bg-emerald-500/30 border-emerald-400 text-emerald-300 font-bold ring-2 ring-emerald-400/50 animate-pulse';
    if (loc.location_id === 'A-03-R02-B04') return 'bg-amber-500/20 border-amber-500/50 text-amber-400';
    if (loc.restricted) return 'bg-purple-500/20 border-purple-500/40 text-purple-300';
    return 'bg-slate-900 border-slate-800 text-slate-300 hover:border-cyan-500/50';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Grid className="w-5 h-5 text-cyan-400" />
            Interactive Warehouse Storage Map
          </h2>
          <p className="text-xs text-slate-400">
            Visual spatial layout displaying zone status, temperature controls, and discrepancy hotspots
          </p>
        </div>

        {/* Zone Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {zones.map((z) => (
            <button
              key={z}
              onClick={() => setSelectedZone(z === 'ALL ZONES' ? '' : z)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
                (z === 'ALL ZONES' && !selectedZone) || selectedZone === z
                  ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                  : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
              }`}
            >
              {z.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 flex flex-wrap items-center gap-6 text-xs text-slate-400">
        <span className="font-semibold text-slate-300">Layout Legend:</span>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-slate-800 border border-slate-700" />
          <span>Active Normal Bin</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-amber-500/30 border border-amber-500/50" />
          <span>Pick Failure Spot (Expected)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-emerald-500/30 border border-emerald-400" />
          <span>Predicted Target Bin (91.4%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-purple-500/30 border border-purple-500/50" />
          <span>Restricted Zone</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-red-500/30 border border-red-500/50" />
          <span>Blocked Bin</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Grid */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center justify-between">
            <span>Rack & Bin Layout Grid</span>
            <span className="text-xs text-slate-400 font-mono">{locations.length} Bins Filtered</span>
          </h3>

          {loading ? (
            <div className="p-8 text-center text-slate-400">Loading map grid...</div>
          ) : (
            <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2.5 max-h-[500px] overflow-y-auto pr-1">
              {locations.map((loc) => (
                <button
                  key={loc.location_id}
                  onClick={() => setSelectedLoc(loc)}
                  className={`p-2.5 rounded-lg border text-center transition flex flex-col items-center justify-center ${getStatusColor(
                    loc
                  )} ${selectedLoc?.location_id === loc.location_id ? 'ring-2 ring-cyan-400' : ''}`}
                >
                  <span className="font-mono text-[10px] font-bold block truncate w-full">{loc.location_id}</span>
                  <span className="text-[9px] opacity-75 mt-0.5">{loc.zone.slice(0, 4)}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Selected Location Details Panel */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Box className="w-4 h-4 text-cyan-400" />
                Bin Location Inspector
              </h3>
              {selectedLoc && (
                <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-[10px] font-bold text-slate-300">
                  {selectedLoc.status}
                </span>
              )}
            </div>

            {selectedLoc ? (
              <div className="mt-4 space-y-4 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Location Identifier</span>
                  <span className="text-lg font-mono font-bold text-cyan-400">{selectedLoc.location_id}</span>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Zone</span>
                    <span className="font-semibold text-slate-200">{selectedLoc.zone}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Temperature Class</span>
                    <span className="font-semibold text-slate-200 flex items-center gap-1">
                      <Thermometer className="w-3 h-3 text-cyan-400" />
                      {selectedLoc.temperature_class}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800/80">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Allowed Product Type</span>
                    <span className="font-semibold text-slate-200">{selectedLoc.allowed_product_type}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Restricted Security</span>
                    <span className={`font-semibold ${selectedLoc.restricted ? 'text-purple-400' : 'text-slate-300'}`}>
                      {selectedLoc.restricted ? 'Yes (Authorized Only)' : 'No'}
                    </span>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800/80">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-slate-400 text-[11px]">Bin Utilization</span>
                    <span className="font-mono text-cyan-300 font-bold">{selectedLoc.current_utilization} / {selectedLoc.capacity} units</span>
                  </div>
                  <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div
                      className="bg-cyan-400 h-full rounded-full"
                      style={{ width: `${(selectedLoc.current_utilization / selectedLoc.capacity) * 100}%` }}
                    />
                  </div>
                </div>

                {selectedLoc.location_id === 'COLD-02-R01-B03' && (
                  <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs">
                    <p className="font-bold flex items-center gap-1.5 mb-1">
                      <CheckCircle2 className="w-4 h-4" />
                      Discrepancy Target Bin #1
                    </p>
                    <p className="text-[11px] text-emerald-300">
                      MED-1042 batch predicted at 91.4% confidence based on recent move & cycle count evidence.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <p className="mt-8 text-center text-slate-500 text-xs">Select a bin grid node above to view details</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
