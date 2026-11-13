import React, { useState, useEffect } from 'react';
import { ClockAlert, ShieldAlert, CheckCircle2, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { Cart } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const AbandonedCartMonitoring: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'all' | 'eligible' | 'suppressed'>('all');
  const [carts, setCarts] = useState<Cart[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [loading, setLoading] = useState(true);

  const fetchAbandonedCarts = async () => {
    try {
      setLoading(true);
      let res;
      if (activeTab === 'eligible') {
        res = await api.getEligibleCarts({ skip, limit });
      } else if (activeTab === 'suppressed') {
        res = await api.getSuppressedCarts({ skip, limit });
      } else {
        res = await api.getAbandonedCarts({ skip, limit });
      }
      setCarts(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAbandonedCarts();
  }, [skip, activeTab]);

  return (
    <div className="space-y-6">
      {/* Policy Callout Banner */}
      <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs flex items-start gap-3">
        <ClockAlert className="w-5 h-5 shrink-0 text-indigo-400 mt-0.5" />
        <div>
          <span className="font-bold text-white block mb-0.5">Automated Abandonment Policy Engine</span>
          Carts are flagged as <span className="font-mono text-indigo-200">ABANDONED</span> when idle for &gt;60 minutes with valid products and no purchase.
          Carts are evaluated against customer consent, suppression rules, and 7-day frequency caps before dispatch.
        </div>
      </div>

      {/* Segment Tabs */}
      <div className="flex border-b border-slate-800 gap-2">
        <button
          onClick={() => {
            setActiveTab('all');
            setSkip(0);
          }}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'all'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ClockAlert className="w-4 h-4" /> All Abandoned
        </button>
        <button
          onClick={() => {
            setActiveTab('eligible');
            setSkip(0);
          }}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'eligible'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <CheckCircle2 className="w-4 h-4" /> Eligible for Recovery
        </button>
        <button
          onClick={() => {
            setActiveTab('suppressed');
            setSkip(0);
          }}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'suppressed'
              ? 'border-rose-500 text-rose-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <ShieldAlert className="w-4 h-4" /> Suppressed by Rules
        </button>
      </div>

      {/* Monitoring Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Cart ID</th>
                <th className="px-6 py-3">Customer ID</th>
                <th className="px-6 py-3">Value ($)</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Last Active</th>
                <th className="px-6 py-3">Abandonment Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                    Scanning abandoned cart pipeline...
                  </td>
                </tr>
              ) : carts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                    No carts found in this category.
                  </td>
                </tr>
              ) : (
                carts.map((cart) => (
                  <tr key={cart.cart_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-xs font-semibold text-indigo-400">
                      {cart.cart_id}
                    </td>
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-300">
                      {cart.customer_id}
                    </td>
                    <td className="px-6 py-3.5 font-semibold text-white">
                      ${Number(cart.total_amount).toFixed(2)}
                    </td>
                    <td className="px-6 py-3.5">
                      <StatusBadge status={cart.status} />
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-400">
                      {new Date(cart.last_activity_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 text-xs text-amber-400 font-medium">
                      {cart.abandoned_at ? new Date(cart.abandoned_at).toLocaleString() : 'Pending'}
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
            <strong className="text-white">{total.toLocaleString()}</strong> carts in segment
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

