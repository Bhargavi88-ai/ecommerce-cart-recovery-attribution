import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const s = status ? status.toUpperCase() : 'UNKNOWN';

  let colorClasses = 'bg-slate-700 text-slate-300 border-slate-600';

  if (['ACTIVE', 'OPT_IN', 'SENT', 'DELIVERED', 'COMPLETED', 'PASS', 'RESOLVED'].includes(s)) {
    colorClasses = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  } else if (['ABANDONED', 'SUPPRESSED', 'OPT_OUT', 'BOUNCED', 'FAILED', 'FAIL', 'DETECTED'].includes(s)) {
    colorClasses = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
  } else if (['ELIGIBLE', 'OPENED', 'CLICKED', 'RECOVERED', 'CAMPAIGN_SCHEDULED'].includes(s)) {
    colorClasses = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
  } else if (['QUEUED', 'WARNING', 'PENDING'].includes(s)) {
    colorClasses = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${colorClasses}`}>
      {s.replace(/_/g, ' ')}
    </span>
  );
};

