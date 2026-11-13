import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert, FileText, Check, RotateCcw } from 'lucide-react';
import { api } from '../services/api';
import { AnomalyRecord } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const AnomalyManagement: React.FC = () => {
  const [anomalies, setAnomalies] = useState<AnomalyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchAnomalies = async () => {
    try {
      setLoading(true);
      const res = await api.getAnomalies();
      setAnomalies(res.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      setUpdatingId(id);
      await api.updateAnomalyStatus(id, newStatus);
      fetchAnomalies();
    } catch (err: any) {
      alert(`Error updating anomaly: ${err.message}`);
    } finally {
      setUpdatingId(null);
    }
  };

  useEffect(() => {
    fetchAnomalies();
  }, []);

  return (
    <div className="space-y-6">
      {/* Notice Banner */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 shrink-0 text-amber-400 mt-0.5" />
        <div>
          <span className="font-bold text-white block mb-0.5">Labelled Anomaly Detection Suite</span>
          Displays the 4 mandatory production exception test fixtures generated to audit exception handling:
          <span className="font-mono text-amber-200"> MESSAGE_AFTER_OPTOUT</span>,
          <span className="font-mono text-amber-200"> CART_ABANDONED_AFTER_PURCHASE</span>,
          <span className="font-mono text-amber-200"> DUPLICATE_ATTRIBUTION</span>, and
          <span className="font-mono text-amber-200"> STALE_CART_TOTAL</span>.
        </div>
      </div>

      {/* Anomalies List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading anomaly records...</div>
        ) : anomalies.length === 0 ? (
          <div className="p-12 text-center text-slate-400">No anomaly records registered.</div>
        ) : (
          anomalies.map((ano) => (
            <div
              key={ano.anomaly_id}
              className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-all space-y-4 shadow-sm"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs font-bold text-indigo-400 bg-indigo-500/10 px-2.5 py-1 rounded border border-indigo-500/20">
                    {ano.anomaly_id}
                  </span>
                  <span className="font-bold text-white text-base font-mono">{ano.issue_type}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400">Affected:</span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 font-mono">
                    {ano.affected_entity} [{ano.affected_record_id}]
                  </span>
                  <StatusBadge status={ano.resolution_status} />
                </div>
              </div>

              {/* Observed vs Expected Comparison Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/20 space-y-1">
                  <span className="font-bold text-rose-400 uppercase tracking-wider block">
                    Observed Anomaly Behavior
                  </span>
                  <p className="text-rose-200 font-mono leading-relaxed">{ano.observed_value}</p>
                  <p className="text-slate-400 pt-1">
                    Actual Decision: <span className="font-semibold text-white">{ano.actual_decision}</span>
                  </p>
                </div>

                <div className="p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 space-y-1">
                  <span className="font-bold text-emerald-400 uppercase tracking-wider block">
                    Expected Policy Decision
                  </span>
                  <p className="text-emerald-200 font-mono leading-relaxed">{ano.expected_value}</p>
                  <p className="text-slate-400 pt-1">
                    Expected Decision: <span className="font-semibold text-white">{ano.expected_decision}</span>
                  </p>
                </div>
              </div>

              {/* Ground Truth & Actions Footer */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-slate-800/80 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-slate-500">Ground Truth Label:</span>
                  <span className="font-mono text-amber-400 font-semibold">{ano.ground_truth_label}</span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-slate-500">Set Resolution:</span>
                  {ano.resolution_status !== 'RESOLVED' && (
                    <button
                      disabled={updatingId === ano.anomaly_id}
                      onClick={() => handleStatusChange(ano.anomaly_id, 'RESOLVED')}
                      className="flex items-center gap-1 px-3 py-1 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 rounded text-xs font-semibold transition-all disabled:opacity-50"
                    >
                      <Check className="w-3.5 h-3.5" /> Mark Resolved
                    </button>
                  )}
                  {ano.resolution_status !== 'DETECTED' && (
                    <button
                      disabled={updatingId === ano.anomaly_id}
                      onClick={() => handleStatusChange(ano.anomaly_id, 'DETECTED')}
                      className="flex items-center gap-1 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded text-xs font-semibold transition-all disabled:opacity-50"
                    >
                      <RotateCcw className="w-3.5 h-3.5" /> Reopen
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

