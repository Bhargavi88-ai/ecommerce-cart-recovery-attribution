import React, { useState, useEffect } from 'react';
import { MailCheck, Filter, ChevronLeft, ChevronRight, Search, Activity, History } from 'lucide-react';
import { api } from '../services/api';
import { SendAttempt } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const MessageEventTracking: React.FC = () => {
  const [sends, setSends] = useState<SendAttempt[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [statusFilter, setStatusFilter] = useState('');
  const [channelFilter, setChannelFilter] = useState('');
  const [suppressionFilter, setSuppressionFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedSend, setSelectedSend] = useState<SendAttempt | null>(null);

  const fetchSends = async () => {
    try {
      setLoading(true);
      const res = await api.getSendAttempts({
        skip,
        limit,
        status: statusFilter || undefined,
        channel: channelFilter || undefined,
        suppression_reason: suppressionFilter || undefined,
      });
      setSends(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const inspectTimeline = async (sendId: string) => {
    try {
      const detailed = await api.getSendAttemptById(sendId);
      setSelectedSend(detailed);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchSends();
  }, [skip, statusFilter, channelFilter, suppressionFilter]);

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setSkip(0);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Send Statuses</option>
            <option value="SENT">SENT</option>
            <option value="SUPPRESSED">SUPPRESSED</option>
            <option value="QUEUED">QUEUED</option>
            <option value="FAILED">FAILED</option>
          </select>

          <select
            value={channelFilter}
            onChange={(e) => {
              setChannelFilter(e.target.value);
              setSkip(0);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Channels</option>
            <option value="EMAIL">Email</option>
            <option value="SMS">SMS</option>
          </select>

          <select
            value={suppressionFilter}
            onChange={(e) => {
              setSuppressionFilter(e.target.value);
              setSkip(0);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Suppression Reasons</option>
            <option value="NO_EMAIL_CONSENT">NO_EMAIL_CONSENT</option>
            <option value="NO_SMS_CONSENT">NO_SMS_CONSENT</option>
            <option value="CONSENT_WITHDRAWN">CONSENT_WITHDRAWN</option>
            <option value="CART_PURCHASED">CART_PURCHASED</option>
            <option value="FREQUENCY_CAP_REACHED">FREQUENCY_CAP_REACHED</option>
            <option value="DUPLICATE_CAMPAIGN">DUPLICATE_CAMPAIGN</option>
          </select>
        </div>
      </div>

      {/* Sends Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Send ID</th>
                <th className="px-6 py-3">Message ID</th>
                <th className="px-6 py-3">Cart ID</th>
                <th className="px-6 py-3">Customer</th>
                <th className="px-6 py-3">Channel</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Suppression Reason</th>
                <th className="px-6 py-3">Scheduled At</th>
                <th className="px-6 py-3 text-right">Timeline</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={9} className="px-6 py-12 text-center text-slate-400">
                    Loading message send events...
                  </td>
                </tr>
              ) : sends.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-12 text-center text-slate-400">
                    No send attempts found.
                  </td>
                </tr>
              ) : (
                sends.map((s) => (
                  <tr key={s.send_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-xs font-semibold text-indigo-400">
                      {s.send_id}
                    </td>
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-400">{s.message_id}</td>
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-300">{s.cart_id}</td>
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-300">{s.customer_id}</td>
                    <td className="px-6 py-3.5 font-medium">{s.channel}</td>
                    <td className="px-6 py-3.5">
                      <StatusBadge status={s.status} />
                    </td>
                    <td className="px-6 py-3.5 text-xs text-rose-400 font-mono">
                      {s.suppression_reason ? (
                        <span className="px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/20">
                          {s.suppression_reason}
                        </span>
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-400">
                      {new Date(s.scheduled_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      {s.status === 'SENT' ? (
                        <button
                          onClick={() => inspectTimeline(s.send_id)}
                          className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1 ml-auto"
                        >
                          <Activity className="w-3.5 h-3.5" /> Events
                        </button>
                      ) : (
                        <span className="text-xs text-slate-600 italic">None</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>
            Showing <strong className="text-white">{total === 0 ? 0 : skip + 1}</strong> to{' '}
            <strong className="text-white">{Math.min(skip + limit, total)}</strong> of{' '}
            <strong className="text-white">{total.toLocaleString()}</strong> send attempts
          </span>
          <div className="flex items-center gap-2">
            <button
              disabled={skip === 0}
              onClick={() => setSkip(Math.max(0, skip - limit))}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 disabled:opacity-40 disabled:hover:bg-transparent"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              disabled={skip + limit >= total}
              onClick={() => setSkip(skip + limit)}
              className="p-1.5 rounded-lg border border-slate-800 hover:bg-slate-800 disabled:opacity-40 disabled:hover:bg-transparent"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Timeline Modal */}
      {selectedSend && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <History className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">Communication Event Lifecycle</h3>
              </div>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {selectedSend.send_id}
              </span>
            </div>

            <div className="space-y-3">
              <p className="text-xs text-slate-400">
                Simulated provider telemetry in chronological sequence:
              </p>

              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
                {selectedSend.communication_events && selectedSend.communication_events.length > 0 ? (
                  selectedSend.communication_events.map((evt, idx) => (
                    <div key={evt.event_id} className="relative">
                      <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-indigo-500 ring-4 ring-slate-900" />
                      <div className="bg-slate-800/60 border border-slate-700/60 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <StatusBadge status={evt.event_type} />
                          <span className="font-mono text-[10px] text-slate-500">{evt.event_id}</span>
                        </div>
                        <div className="text-xs text-slate-300 mt-1">
                          {new Date(evt.timestamp).toLocaleString()}
                        </div>
                        {evt.metadata_json && (
                          <div className="text-[11px] font-mono text-slate-400 mt-1 bg-slate-900/60 p-1 rounded">
                            {evt.metadata_json}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500">No events logged.</p>
                )}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedSend(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

