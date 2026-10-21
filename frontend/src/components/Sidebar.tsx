import React from 'react';
import {
  LayoutDashboard,
  Globe2,
  TrendingUp,
  PieChart,
  DollarSign,
  GitCompare,
  Cpu,
  BarChart3,
  Database,
  FileText,
  Info
} from 'lucide-react';

export type TabType =
  | 'overview'
  | 'explorer'
  | 'forecasting'
  | 'composition'
  | 'costs'
  | 'comparison'
  | 'training'
  | 'evaluation'
  | 'datasets'
  | 'reports'
  | 'about';

interface SidebarProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

const NAV_ITEMS: { id: TabType; label: string; icon: React.FC<{ className?: string }> }[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'explorer', label: 'Global Beach Explorer', icon: Globe2 },
  { id: 'forecasting', label: 'Waste Forecasting', icon: TrendingUp },
  { id: 'composition', label: 'Waste Composition', icon: PieChart },
  { id: 'costs', label: 'Recycling & Treatment Costs', icon: DollarSign },
  { id: 'comparison', label: 'Beach Comparison', icon: GitCompare },
  { id: 'training', label: 'Model Training', icon: Cpu },
  { id: 'evaluation', label: 'Model Evaluation', icon: BarChart3 },
  { id: 'datasets', label: 'Dataset Management', icon: Database },
  { id: 'reports', label: 'Reports & Export', icon: FileText },
  { id: 'about', label: 'About the Project', icon: Info },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between h-[calc(100vh-4rem)] sticky top-16 select-none shrink-0">
      <div className="py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Navigation
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-teal-50 text-teal-800 border border-teal-200 shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-teal-600' : 'text-slate-400'}`} />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Footer system status note */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center space-x-2 text-[11px] text-slate-500">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="font-medium">System Online</span>
        </div>
        <p className="text-[10px] text-slate-400 mt-1">BeachWaste AI • PyTorch 2.9 Core</p>
      </div>
    </aside>
  );
};
