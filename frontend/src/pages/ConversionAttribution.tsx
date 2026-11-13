import React, { useState, useEffect } from 'react';
import { Sparkles, ChevronLeft, ChevronRight, DollarSign, Clock, Layers } from 'lucide-react';
import { api } from '../services/api';
import { Attribution, CampaignPerformanceMetric } from '../types';

export const ConversionAttribution: React.FC = () => {
  const [attributions, setAttributions] = useState<Attribution[]>([]);
  const [campaignStats, setCampaignStats] = useState<CampaignPerformanceMetric[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(25);
  const [loading, setLoading] = useState(true);

  const fetchAttributionData = async () => {
    try {
      setLoading(true);
      const [attrRes, statsRes] = await Promise.all([
        api.getAttributions({ skip, limit }),
        api.getCampaignPerformance(),
      ]);
      setAttributions(attrRes.items);
      setTotal(attrRes.total);
      setCampaignStats(statsRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttributionData();
  }, [skip]);

  return (
    <div className="space-y-8">
      {/* Attribution Logic Banner */}
      <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs flex items-start gap-3">
        <Sparkles className="w-5 h-5 shrink-0 text-indigo-400 mt-0.5" />
        <div>
          <span className="font-bold text-white block mb-0.5">Deterministic Last-Click Attribution Engine</span>
          Attributes orders 1:1 strictly to the latest qualifying campaign CLICK occurring prior to the order timestamp
          within a 7-day lookback window. Prevents revenue double-counting and logs latency hours.
        </div>
      </div>

      {/* Campaign Performance Summary */}
      <div>
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">
          Campaign Conversion Attribution Summary
        </h3>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-6 py-3">Campaign</th>
                <th className="px-6 py-3">Channel</th>
                <th className="px-6 py-3">Sends</th>
                <th className="px-6 py-3">Delivered</th>
                <th className="px-6 py-3">Clicks</th>
                <th className="px-6 py-3">Attributed Orders</th>
                <th className="px-6 py-3">Attributed Revenue ($)</th>
                <th className="px-6 py-3 text-right">Conv. Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-300">
              {campaignStats.map((stat) => (
                <tr key={stat.campaign_id} className="hover:bg-slate-800/40">
                  <td className="px-6 py-3.5 font-medium text-white">{stat.name}</td>
                  <td className="px-6 py-3.5">{stat.channel}</td>
                  <td className="px-6 py-3.5">{stat.sends.toLocaleString()}</td>
                  <td className="px-6 py-3.5">{stat.delivered.toLocaleString()}</td>
                  <td className="px-6 py-3.5">{stat.clicks.toLocaleString()}</td>
                  <td className="px-6 py-3.5 font-semibold text-emerald-400">
                    {stat.conversions.toLocaleString()}
                  </td>
                  <td className="px-6 py-3.5 font-bold text-white">
                    ${stat.revenue.toLocaleString()}
                  </td>
                  <td className="px-6 py-3.5 text-right font-semibold text-indigo-400">
                    {stat.conversion_rate}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Attribution Records Table */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">
          Individual Attribution Ledger (1:1 Non-Double Counted)
        </h3>
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/60 text-slate-400 text-xs uppercase tracking-wider border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">Attribution ID</th>
                  <th className="px-6 py-3">Order ID</th>
                  <th className="px-6 py-3">Winning Campaign</th>
                  <th className="px-6 py-3">Send ID</th>
                  <th className="px-6 py-3">Qualifying Click</th>
                  <th className="px-6 py-3">Conversion Latency</th>
                  <th className="px-6 py-3">Attributed Revenue</th>
                  <th className="px-6 py-3 text-right">Model</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-400">
                      Loading attribution ledger...
                    </td>
                  </tr>
                ) : attributions.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-400">
                      No campaign-attributed orders yet.
                    </td>
                  </tr>
                ) : (
                  attributions.map((attr) => (
                    <tr key={attr.attribution_id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-6 py-3.5 font-mono text-xs font-semibold text-indigo-400">
                        {attr.attribution_id}
                      </td>
                      <td className="px-6 py-3.5 font-mono text-xs text-white">{attr.order_id}</td>
                      <td className="px-6 py-3.5 font-mono text-xs text-slate-300">
                        {attr.campaign_id}
                      </td>
                      <td className="px-6 py-3.5 font-mono text-xs text-slate-400">{attr.send_id}</td>
                      <td className="px-6 py-3.5 text-xs text-slate-300">
                        {new Date(attr.qualifying_click_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-3.5 text-xs font-medium text-amber-400">
                        {attr.latency_hours}h latency
                      </td>
                      <td className="px-6 py-3.5 font-bold text-emerald-400">
                        ${Number(attr.attributed_revenue).toFixed(2)}
                      </td>
                      <td className="px-6 py-3.5 text-right font-mono text-xs text-slate-400">
                        {attr.model}
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
              <strong className="text-white">{total.toLocaleString()}</strong> attributed conversions
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
    </div>
  );
};
