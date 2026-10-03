import React, { useState, useEffect } from 'react';
import { ShieldCheck, Clock, FileText, UserCheck, AlertTriangle } from 'lucide-react';
import axios from 'axios';

interface AuditLog {
  id: string;
  timestamp: string;
  user_id?: string;
  action: string;
  entity?: string;
  sku?: string;
  location_id?: string;
  worker_id?: string;
  details_json?: any;
}

export const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await axios.get('/api/audit/logs');
      setLogs(res.data);
    } catch {
      // Mock fallback
      setLogs([
        {
          id: 'AUD-1001',
          timestamp: new Date().toISOString(),
          user_id: 'USR-001',
          action: 'DISCREPANCY_DETECTION_RUN',
          entity: 'DISCREPANCIES',
          details_json: { detected_count: 12, mode: 'AUTOMATED_CRON' }
        },
        {
          id: 'AUD-1002',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          user_id: 'USR-002',
          action: 'PREDICTION_GENERATED',
          entity: 'PREDICTION',
          sku: 'MED-1002-001',
          location_id: 'COLD-02-R01-B03',
          details_json: { confidence: 0.91, top_candidates_count: 3 }
        },
        {
          id: 'AUD-1003',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          user_id: 'USR-003',
          action: 'DISCREPANCY_RESOLVED',
          entity: 'DISCREPANCY',
          sku: 'MED-1005-004',
          location_id: 'HIGH-A02-R01-B04',
          details_json: { notes: 'Physical count verified bin contents.', verified_location: 'HIGH-A02-R01-B04' }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-emerald-400" />
            System Audit Logs & Governance Trail
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Immutable, compliant record of system events, predictions, safety overrides, and inventory corrections.
          </p>
        </div>
        <button
          onClick={fetchLogs}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-lg border border-slate-700 transition"
        >
          Refresh Logs
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
          <span className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-400" />
            Recent Audit Event Stream ({logs.length} items)
          </span>
          <span className="text-xs text-slate-400 bg-slate-800 px-2.5 py-1 rounded-full border border-slate-700">
            Role Access: WAREHOUSE_MANAGER & ADMIN
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading audit records...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/60 text-slate-400 uppercase text-xs border-b border-slate-800">
                <tr>
                  <th className="p-3.5">Log ID</th>
                  <th className="p-3.5">Timestamp</th>
                  <th className="p-3.5">User</th>
                  <th className="p-3.5">Action Event</th>
                  <th className="p-3.5">Target Entity</th>
                  <th className="p-3.5">SKU / Location</th>
                  <th className="p-3.5">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30 transition">
                    <td className="p-3.5 font-mono text-xs text-slate-400">{log.id}</td>
                    <td className="p-3.5 text-xs text-slate-400 whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="p-3.5 font-medium text-slate-200">
                      {log.user_id || 'SYSTEM_CRON'}
                    </td>
                    <td className="p-3.5">
                      <span className={`inline-block px-2.5 py-0.5 rounded text-xs font-semibold ${
                        log.action.includes('RESOLVED') ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        log.action.includes('PREDICTION') ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' :
                        'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-300 font-mono text-xs">{log.entity || 'SYSTEM'}</td>
                    <td className="p-3.5 text-slate-300 font-mono text-xs">
                      {log.sku ? `${log.sku} ${log.location_id ? `(${log.location_id})` : ''}` : '-'}
                    </td>
                    <td className="p-3.5 text-xs text-slate-400 max-w-xs truncate">
                      {log.details_json ? JSON.stringify(log.details_json) : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogPage;
