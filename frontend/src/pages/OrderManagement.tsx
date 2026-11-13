import React, { useState, useEffect } from 'react';
import { ShoppingBag, ChevronLeft, ChevronRight, Search, Eye, Package } from 'lucide-react';
import { api } from '../services/api';
import { Order } from '../types';
import { StatusBadge } from '../components/StatusBadge';

export const OrderManagement: React.FC = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [searchCustomer, setSearchCustomer] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const res = await api.getOrders({
        skip,
        limit,
        customer_id: searchCustomer.trim() || undefined,
      });
      setOrders(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const inspectOrder = async (orderId: string) => {
    try {
      const detailed = await api.getOrderById(orderId);
      setSelectedOrder(detailed);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [skip]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSkip(0);
    fetchOrders();
  };

  return (
    <div className="space-y-6">
      {/* Header & Filter */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by customer ID..."
            value={searchCustomer}
            onChange={(e) => setSearchCustomer(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </form>
      </div>

      {/* Orders Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Order ID</th>
                <th className="px-6 py-3">Customer ID</th>
                <th className="px-6 py-3">Cart ID</th>
                <th className="px-6 py-3">Order Amount ($)</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Placed Timestamp</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    Loading orders ledger...
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    No orders found.
                  </td>
                </tr>
              ) : (
                orders.map((o) => (
                  <tr key={o.order_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-xs font-semibold text-indigo-400">
                      {o.order_id}
                    </td>
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-300">{o.customer_id}</td>
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-400">
                      {o.cart_id || 'Direct / Organic'}
                    </td>
                    <td className="px-6 py-3.5 font-semibold text-emerald-400">
                      ${Number(o.total_amount).toFixed(2)}
                    </td>
                    <td className="px-6 py-3.5">
                      <StatusBadge status={o.status} />
                    </td>
                    <td className="px-6 py-3.5 text-xs text-slate-400">
                      {new Date(o.order_timestamp).toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <button
                        onClick={() => inspectOrder(o.order_id)}
                        className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center gap-1 ml-auto"
                      >
                        <Eye className="w-3.5 h-3.5" /> Items
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
            <strong className="text-white">{total.toLocaleString()}</strong> orders
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

      {/* Order Lines Modal */}
      {selectedOrder && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <Package className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-white text-base">Order Line Items</h3>
              </div>
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {selectedOrder.order_id}
              </span>
            </div>

            <div className="space-y-3">
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
                    {selectedOrder.order_lines?.map((line) => (
                      <tr key={line.order_line_id}>
                        <td className="px-4 py-2 font-mono text-indigo-400">{line.order_line_id}</td>
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
                <span className="font-semibold text-slate-400">Total Order Amount</span>
                <span className="text-lg font-bold text-emerald-400">
                  ${Number(selectedOrder.total_amount).toFixed(2)}
                </span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedOrder(null)}
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

