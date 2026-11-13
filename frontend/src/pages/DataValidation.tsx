import React, { useState, useEffect } from 'react';
import { FileCheck2, Play, CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { ValidationSummary } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const DataValidation: React.FC = () => {
  const [summary, setSummary] = useState<ValidationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetchLatestReport = async () => {
    try {
      setLoading(true);
      const res = await api.getValidationReport();
      setSummary(res);
    } catch {
      // If report not found yet, run validation automatically
      handleRunValidation();
    } finally {
      setLoading(false);
    }
  };

  const handleRunValidation = async () => {
    try {
      setRunning(true);
      const res = await api.runValidation();
      setSummary(res);
    } catch (err: any) {
      alert(`Validation error: ${err.message}`);
    } finally {
      setRunning(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestReport();
  }, []);

  return (
    <div className="space-y-6">
      {/* Run Validation Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-white">Automated 16-Point Data Quality Audit</h3>
          <p className="text-xs text-slate-400">
            Validates referential integrity, chronology, arithmetic reconciliations, and suppression rules
          </p>
        </div>
        <button
          onClick={handleRunValidation}
          disabled={running}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-sm shadow-indigo-600/30 transition-all disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${running ? 'animate-spin' : ''}`} />
          {running ? 'Running Validation Suite...' : 'Execute Full Validation Suite'}
        </button>
      </div>

      {/* Summary Scorecard */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400 uppercase font-medium">Overall Status</span>
            <div className="mt-1 flex items-center gap-2">
              <StatusBadge status={summary.overall_status} />
            </div>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400 uppercase font-medium">Rules Evaluated</span>
            <div className="mt-1 text-2xl font-bold text-white">{summary.total_rules} Rules</div>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400 uppercase font-medium">Rules Compliant</span>
            <div className="mt-1 text-2xl font-bold text-emerald-400">{summary.passed_rules} Passed</div>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs text-slate-400 uppercase font-medium">Total Violations</span>
            <div className={`mt-1 text-2xl font-bold ${summary.total_violations === 0 ? 'text-slate-300' : 'text-rose-400'}`}>
              {summary.total_violations}
            </div>
          </div>
        </div>
      )}

      {/* Rules Breakdown Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Rule Name & Scope</th>
                <th className="px-6 py-3">Validation Status</th>
                <th className="px-6 py-3">Violation Count</th>
                <th className="px-6 py-3 text-right">Error Sample Inspection</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-slate-400">
                    Evaluating relational constraints and business rules...
                  </td>
                </tr>
              ) : !summary ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-slate-400">
                    No validation data available. Click "Execute Full Validation Suite" above.
                  </td>
                </tr>
              ) : (
                summary.rule_results.map((rule) => (
                  <tr key={rule.rule_name} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-xs font-semibold text-slate-200">
                      {rule.rule_name}
                    </td>
                    <td className="px-6 py-3.5">
                      <StatusBadge status={rule.status} />
                    </td>
                    <td className="px-6 py-3.5 font-medium">
                      {rule.error_count === 0 ? (
                        <span className="text-emerald-400 font-semibold">0 violations</span>
                      ) : (
                        <span className="text-rose-400 font-semibold">{rule.error_count} violations</span>
                      )}
                    </td>
                    <td className="px-6 py-3.5 text-right text-xs">
                      {rule.sample_errors && rule.sample_errors.length > 0 ? (
                        <span className="text-rose-300 font-mono">
                          {rule.sample_errors[0]}
                        </span>
                      ) : (
                        <span className="text-slate-500 italic">None (Clean check)</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

