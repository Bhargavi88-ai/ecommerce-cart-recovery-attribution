import React, { useState, useEffect } from 'react';
import { Search, Filter, ChevronLeft, ChevronRight, User, Mail, Phone, Calendar } from 'lucide-react';
import { api } from '../services/api';
import { Customer } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const CustomerManagement: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [search, setSearch] = useState('');
  const [channelFilter, setChannelFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const res = await api.getCustomers({
        skip,
        limit,
        search: search.trim() || undefined,
        preferred_channel: channelFilter || undefined,
      });
      setCustomers(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [skip, channelFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSkip(0);
    fetchCustomers();
  };

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by ID, name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
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
            <option value="">All Preferred Channels</option>
            <option value="EMAIL">Email</option>
            <option value="SMS">SMS</option>
          </select>
        </div>
      </div>

      {/* Customers Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Customer ID</th>
                <th className="px-6 py-3">Full Name</th>
                <th className="px-6 py-3">Email Address</th>
                <th className="px-6 py-3">Phone Number</th>
                <th className="px-6 py-3">Preferred Channel</th>
                <th className="px-6 py-3">Registered At</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    Loading customer directory...
                  </td>
                </tr>
              ) : customers.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    No customers found matching filter criteria.
                  </td>
                </tr>
              ) : (
                customers.map((c) => (
                  <tr key={c.customer_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-xs font-semibold text-indigo-400">
                      {c.customer_id}
                    </td>
                    <td className="px-6 py-3.5 font-medium text-white">
                      {c.first_name} {c.last_name}
                    </td>
                    <td className="px-6 py-3.5 text-slate-400">{c.email}</td>
                    <td className="px-6 py-3.5 text-slate-400">{c.phone}</td>
                    <td className="px-6 py-3.5">
                      <StatusBadge status={c.preferred_channel} />
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-400">
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <button
                        onClick={() => setSelectedCustomer(c)}
                        className="text-xs font-medium text-indigo-400 hover:text-indigo-300"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>
            Showing <strong className="text-white">{total === 0 ? 0 : skip + 1}</strong> to{' '}
            <strong className="text-white">{Math.min(skip + limit, total)}</strong> of{' '}
            <strong className="text-white">{total.toLocaleString()}</strong> customers
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

      {/* Customer Detail Modal */}
      {selectedCustomer && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <User className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">Customer Details</h3>
              </div>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {selectedCustomer.customer_id}
              </span>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Full Name</span>
                <span className="font-medium text-white">
                  {selectedCustomer.first_name} {selectedCustomer.last_name}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Email</span>
                <span className="text-white font-mono text-xs">{selectedCustomer.email}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Phone</span>
                <span className="text-white">{selectedCustomer.phone}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Preferred Channel</span>
                <StatusBadge status={selectedCustomer.preferred_channel} />
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Created Timestamp</span>
                <span className="text-slate-300 text-xs">
                  {new Date(selectedCustomer.created_at).toLocaleString()}
                </span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedCustomer(null)}
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
