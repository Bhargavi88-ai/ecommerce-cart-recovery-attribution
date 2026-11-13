import React, { useState, useEffect } from 'react';
import { ShoppingCart, Filter, ChevronLeft, ChevronRight, Search, Eye, Package } from 'lucide-react';
import { api } from '../services/api';
import { Cart } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const CartManagement: React.FC = () => {
  const [carts, setCarts] = useState<Cart[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [statusFilter, setStatusFilter] = useState('');
  const [customerSearch, setCustomerSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedCart, setSelectedCart] = useState<Cart | null>(null);

  const fetchCarts = async () => {
    try {
      setLoading(true);
      const res = await api.getCarts({
        skip,
        limit,
        status: statusFilter || undefined,
        customer_id: customerSearch.trim() || undefined,
      });
      setCarts(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInspect = async (cartId: string) => {
    try {
      const detailed = await api.getCartById(cartId);
      setSelectedCart(detailed);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchCarts();
  }, [skip, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSkip(0);
    fetchCarts();
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by Customer ID..."
            value={customerSearch}
            onChange={(e) => setCustomerSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </form>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setSkip(0);
            }}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Cart Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="ABANDONED">ABANDONED</option>
            <option value="ELIGIBLE">ELIGIBLE</option>
            <option value="SUPPRESSED">SUPPRESSED</option>
            <option value="CAMPAIGN_SCHEDULED">CAMPAIGN_SCHEDULED</option>
            <option value="RECOVERED">RECOVERED</option>
            <option value="EXPIRED">EXPIRED</option>
          </select>
        </div>
      </div>

      {/* Carts Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Cart ID</th>
                <th className="px-6 py-3">Customer ID</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Total Amount</th>
                <th className="px-6 py-3">Last Activity</th>
                <th className="px-6 py-3">Abandoned At</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    Loading shopping carts...
                  </td>
                </tr>
              ) : carts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    No carts found matching criteria.
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
                    <td className="px-6 py-3.5">
                      <StatusBadge status={cart.status} />
                    </td>
                    <td className="px-6 py-3.5 font-semibold text-white">
                      ${Number(cart.total_amount).toFixed(2)}
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-400">
                      {new Date(cart.last_activity_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-400">
                      {cart.abandoned_at ? new Date(cart.abandoned_at).toLocaleString() : '—'}
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <button
                        onClick={() => handleInspect(cart.cart_id)}
                        className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1 ml-auto"
                      >
                        <Eye className="w-3.5 h-3.5" /> Lines
                      </button>
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
            <strong className="text-white">{total.toLocaleString()}</strong> carts
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

      {/* Cart Lines Inspection Modal */}
      {selectedCart && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <Package className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">Cart Line Items</h3>
              </div>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {selectedCart.cart_id}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-xs text-slate-400">
                <span>Customer: <strong className="text-white">{selectedCart.customer_id}</strong></span>
                <span>Status: <StatusBadge status={selectedCart.status} /></span>
              </div>

              <div className="border border-slate-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-800/80 text-slate-400 uppercase">
                    <tr>
                      <th className="px-4 py-2">Line ID</th>
                      <th className="px-4 py-2">Product ID</th>
                      <th className="px-4 py-2">Qty</th>
                      <th className="px-4 py-2">Unit Price</th>
                      <th className="px-4 py-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {selectedCart.cart_lines?.map((line) => (
                      <tr key={line.cart_line_id}>
                        <td className="px-4 py-2 font-mono text-indigo-400">{line.cart_line_id}</td>
                        <td className="px-4 py-2 font-mono">{line.product_id}</td>
                        <td className="px-4 py-2">{line.quantity}</td>
                        <td className="px-4 py-2">${Number(line.unit_price).toFixed(2)}</td>
                        <td className="px-4 py-2 text-right font-medium text-white">
                          ${Number(line.total_price).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex justify-between items-center pt-2 border-t border-slate-800 text-sm">
                <span className="font-semibold text-slate-400">Reconciled Cart Total</span>
                <span className="text-lg font-bold text-emerald-400">
                  ${Number(selectedCart.total_amount).toFixed(2)}
                </span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedCart(null)}
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
