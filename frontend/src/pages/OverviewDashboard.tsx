import React, { useEffect, useState } from 'react';
import {
  Users,
  ShoppingCart,
  ClockAlert,
  ShieldCheck,
  SendHorizontal,
  MailCheck,
  CheckCircle,
  Eye,
  MousePointerClick,
  ShoppingBag,
  DollarSign,
  TrendingUp,
  Percent,
  AlertTriangle,
  RotateCcw,
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { api } from '../services/api';
import { OverviewAnalytics } from '../types';
import { KpiCard } from '../components/KpiCard';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

export const OverviewDashboard: React.FC = () => {
  const [data, setData] = useState<OverviewAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getOverviewAnalytics();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm text-slate-400">Loading live analytics from database...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
        <p className="font-semibold">Unable to fetch dashboard metrics</p>
        <p className="text-sm mt-1">{error || 'Unknown error'}</p>
        <button
          onClick={loadData}
          className="mt-3 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold"
        >
          Retry
        </button>
      </div>
    );
  }

  const { kpis } = data;

  return (
    <div className="space-y-8">
      {/* 14 KPI Cards Grid */}
      <div>
        <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">
          Core Conversion & Revenue KPIs
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            title="Total Customers"
            value={kpis.total_customers.toLocaleString()}
            subtitle="Registered master profiles"
            icon={Users}
            color="indigo"
          />
          <KpiCard
            title="Total Carts"
            value={kpis.total_carts.toLocaleString()}
            subtitle={`Abandonment Rate: ${kpis.abandonment_rate}%`}
            icon={ShoppingCart}
            color="blue"
          />
          <KpiCard
            title="Abandoned Carts"
            value={kpis.abandoned_carts.toLocaleString()}
            subtitle={`${kpis.eligible_carts} eligible for recovery`}
            icon={ClockAlert}
            color="amber"
          />
          <KpiCard
            title="Suppressed Carts"
            value={kpis.suppressed_carts.toLocaleString()}
            subtitle={`Suppression Rate: ${kpis.suppression_rate}%`}
            icon={ShieldCheck}
            color="rose"
          />

          <KpiCard
            title="Active Campaigns"
            value={kpis.campaigns}
            subtitle="Email & SMS multi-channel"
            icon={SendHorizontal}
            color="indigo"
          />
          <KpiCard
            title="Send Attempts"
            value={kpis.send_attempts.toLocaleString()}
            subtitle="Dispatched recovery events"
            icon={MailCheck}
            color="blue"
          />
          <KpiCard
            title="Delivery Rate"
            value={`${kpis.delivery_rate}%`}
            subtitle="Successfully reached customer"
            icon={CheckCircle}
            color="emerald"
          />
          <KpiCard
            title="Open Rate"
            value={`${kpis.open_rate}%`}
            subtitle="Opened recovery communications"
            icon={Eye}
            color="indigo"
          />

          <KpiCard
            title="Click Rate"
            value={`${kpis.click_rate}%`}
            subtitle="Clicked recovery link"
            icon={MousePointerClick}
            color="blue"
          />
          <KpiCard
            title="Recovered Orders"
            value={kpis.recovered_orders.toLocaleString()}
            subtitle="Direct campaign conversions"
            icon={ShoppingBag}
            color="emerald"
          />
          <KpiCard
            title="Recovered Revenue"
            value={`$${kpis.recovered_revenue.toLocaleString()}`}
            subtitle={`Avg $${kpis.revenue_per_recovered_cart} per recovered cart`}
            icon={DollarSign}
            color="emerald"
          />
          <KpiCard
            title="Recovery Rate"
            value={`${kpis.recovery_rate}%`}
            subtitle="Attributed / Abandoned"
            icon={RotateCcw}
            color="emerald"
          />

          <KpiCard
            title="Conversion Rate"
            value={`${kpis.conversion_rate}%`}
            subtitle="Orders per sent recovery message"
            icon={Percent}
            color="emerald"
          />
          <KpiCard
            title="Eligible Carts"
            value={kpis.eligible_carts.toLocaleString()}
            subtitle="Ready for recovery scheduling"
            icon={TrendingUp}
            color="indigo"
          />
        </div>
      </div>

      {/* Visualizations Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cart Lifecycle Distribution */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-semibold text-white mb-1">Cart Lifecycle Distribution</h3>
          <p className="text-xs text-slate-400 mb-4">Breakdown of carts across all lifecycle states</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.cart_lifecycle_distribution}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  label={({ name, percent }: any) => `${name} (${((percent || 0) * 100).toFixed(0)}%)`}
                >
                  {data.cart_lifecycle_distribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Email vs SMS Channel Performance */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-semibold text-white mb-1">Channel Comparison: Sends & Revenue</h3>
          <p className="text-xs text-slate-400 mb-4">Volume dispatched vs revenue attributed ($)</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.channel_performance}>
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Legend />
                <Bar dataKey="value" name="Sent Attempts" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="secondary_value" name="Revenue Recovered ($)" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Suppression Reason Breakdown */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-semibold text-white mb-1">Suppression Reasons Breakdown</h3>
          <p className="text-xs text-slate-400 mb-4">Audit of suppression engine decision codes</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={data.suppression_reasons} margin={{ left: 40 }}>
                <XAxis type="number" stroke="#64748b" />
                <YAxis dataKey="name" type="category" stroke="#64748b" width={140} tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Bar dataKey="value" name="Suppressed Messages" fill="#ef4444" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Anomaly Distribution */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-sm">
          <h3 className="text-sm font-semibold text-white mb-1">Detected Anomaly Distribution</h3>
          <p className="text-xs text-slate-400 mb-4">The 4 mandatory labeled edge-case anomaly records</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.anomaly_distribution}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {data.anomaly_distribution.map((_, index) => (
                    <Cell key={`ano-${index}`} fill={COLORS[(index + 3) % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
