import React, { useState, useEffect } from 'react';
import { ShieldCheck, Filter, ChevronLeft, ChevronRight, Search } from 'lucide-react';
import { api } from '../services/api';
import { Consent } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const ConsentManagement: React.FC = () => {
  const [consents, setConsents] = useState<Consent[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [channelFilter, setChannelFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [customerSearch, setCustomerSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchConsents = async () => {
    try {
      setLoading(true);
      const res = await api.getConsents({
        skip,
        limit,
        channel: channelFilter || undefined,
        status: statusFilter || undefined,
        customer_id: customerSearch.trim() || undefined,
      });
      setConsents(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConsents();
  }, [skip, channelFilter, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSkip(0);
    fetchConsents();
  };

  return (
    <div className="space-y-6">
      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by customer ID (e.g. CUS-000001)..."
            value={customerSearch}
            onChange={(e) => setCustomerSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </form>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
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
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setSkip(0);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="OPT_IN">Opt-In</option>
            <option value="OPT_OUT">Opt-Out / Withdrawn</option>
          </select>
        </div>
      </div>

      {/* Consents Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Consent ID</th>
                <th className="px-6 py-3">Customer ID</th>
                <th className="px-6 py-3">Channel</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Effective At</th>
                <th className="px-6 py-3">Consent Source</th>
                <th className="px-6 py-3">Recorded At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    Loading consent audit records...
                  </td>
                </tr>
              ) : consents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    No consent records found.
                  </td>
                </tr>
              ) : (
                consents.map((c) => (
                  <tr key={c.consent_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-xs text-indigo-400">{c.consent_id}</td>
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-200">{c.customer_id}</td>
                    <td className="px-6 py-3.5 font-medium text-white">{c.channel}</td>
                    <td className="px-6 py-3.5">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-300">
                      {new Date(c.effective_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
                        {c.source}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-500">
                      {new Date(c.created_at).toLocaleString()}
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
            <strong className="text-white">{total.toLocaleString()}</strong> consent logs
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
    </div>
  );
};
