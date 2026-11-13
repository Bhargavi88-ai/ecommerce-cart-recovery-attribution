import React from 'react';
import {
  LayoutDashboard,
  Users,
  ShieldCheck,
  ShoppingCart,
  ClockAlert,
  SendHorizontal,
  MailCheck,
  ShoppingBag,
  Sparkles,
  AlertTriangle,
  FileCheck2,
  DatabaseZap,
} from 'lucide-react';

export type PageId =
  | 'overview'
  | 'customers'
  | 'consents'
  | 'carts'
  | 'abandoned'
  | 'campaigns'
  | 'messages'
  | 'orders'
  | 'attributions'
  | 'anomalies'
  | 'validation'
  | 'exports';

interface SidebarProps {
  currentPage: PageId;
  onNavigate: (page: PageId) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const navItems = [
    { id: 'overview', label: 'Overview Dashboard', icon: LayoutDashboard },
    { id: 'customers', label: 'Customers', icon: Users },
    { id: 'consents', label: 'Consent Management', icon: ShieldCheck },
    { id: 'carts', label: 'Shopping Carts', icon: ShoppingCart },
    { id: 'abandoned', label: 'Abandoned Carts', icon: ClockAlert },
    { id: 'campaigns', label: 'Campaign Engine', icon: SendHorizontal },
    { id: 'messages', label: 'Message Tracking', icon: MailCheck },
    { id: 'orders', label: 'Orders Placed', icon: ShoppingBag },
    { id: 'attributions', label: 'Campaign Attribution', icon: Sparkles },
    { id: 'anomalies', label: 'Anomaly Manager', icon: AlertTriangle },
    { id: 'validation', label: 'Data Quality Suite', icon: FileCheck2 },
    { id: 'exports', label: 'Generator & Exports', icon: DatabaseZap },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 min-h-screen">
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-black text-lg">
          CR
        </div>
        <div>
          <h1 className="text-sm font-bold text-white tracking-wide">CartRecovery</h1>
          <p className="text-[11px] text-slate-400 font-medium tracking-tight">& Attribution Studio</p>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Core Workflows
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id as PageId)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 text-xs text-slate-500">
        <div className="flex items-center justify-between mb-1">
          <span>Engine Status</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Online
          </span>
        </div>
        <div className="text-[11px] text-slate-600">v2.0.0 • Seed 20261022</div>
      </div>
    </aside>
  );
};
