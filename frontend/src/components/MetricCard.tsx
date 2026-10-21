import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  icon: React.FC<{ className?: string }>;
  badge?: string;
  badgeVariant?: 'teal' | 'amber' | 'blue' | 'slate' | 'emerald' | 'purple';
  change?: string;
  changePositive?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  subtitle,
  icon: Icon,
  badge,
  badgeVariant = 'teal',
  change,
  changePositive = true
}) => {
  const badgeStyles = {
    teal: 'bg-teal-50 text-teal-700 border-teal-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    blue: 'bg-sky-50 text-sky-700 border-sky-200',
    slate: 'bg-slate-100 text-slate-700 border-slate-200',
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
  }[badgeVariant];

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
            {badge && (
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeStyles}`}>
                {badge}
              </span>
            )}
          </div>
          <div className="flex items-baseline space-x-1 pt-1">
            <span className="text-2xl font-extrabold text-slate-900 tracking-tight">{value}</span>
            {unit && <span className="text-xs font-semibold text-slate-500">{unit}</span>}
          </div>
        </div>
        <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-600 group-hover:bg-teal-50 group-hover:text-teal-600 group-hover:border-teal-200 transition-colors">
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {(subtitle || change) && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          {subtitle && <span>{subtitle}</span>}
          {change && (
            <span className={`font-semibold ${changePositive ? 'text-emerald-600' : 'text-amber-600'}`}>
              {change}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
