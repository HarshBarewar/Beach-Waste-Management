import React, { useState, useEffect } from 'react';
import { Beach, ForecastResponse, CompositionResponse } from '../types';
import { estimateComposition } from '../services/api';
import {
  PieChart as PieIcon,
  Recycle,
  Trash2,
  Leaf,
  Layers,
  Sliders,
  AlertTriangle,
  Info,
  CheckCircle2
} from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';

interface CompositionPageProps {
  beach: Beach | null;
  forecast: ForecastResponse | null;
}

const MATERIAL_COLORS: Record<string, string> = {
  Plastic: '#0d9488',   // Teal
  Metal: '#f59e0b',     // Amber
  Glass: '#0284c7',     // Sky Blue
  Paper: '#8b5cf6',     // Purple
  Organic: '#10b981',   // Emerald
  Textiles: '#ec4899',  // Pink
  Other: '#64748b',     // Slate
};

const RECOVERY_COLORS: Record<string, string> = {
  'Recyclable Stream': '#0d9488',
  'Composting/Biodegradable': '#10b981',
  'Landfill/Incineration Residual': '#f43f5e'
};

export const CompositionPage: React.FC<CompositionPageProps> = ({ beach, forecast }) => {
  const [method, setMethod] = useState<'historical_beach_profile' | 'regional_profile' | 'user_scenario'>('historical_beach_profile');
  const [composition, setComposition] = useState<CompositionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // User custom shares state
  const [customShares, setCustomShares] = useState<Record<string, number>>({
    plastic: 55,
    metal: 12,
    glass: 12,
    paper: 9,
    organic: 7,
    other: 5
  });

  const baseMass = forecast?.cumulative_predicted_waste_kg || beach?.avg_monthly_waste_kg || 2500;

  const loadComposition = async () => {
    setLoading(true);
    try {
      const res = await estimateComposition({
        beach_id: beach?.id,
        total_waste_kg: baseMass,
        method: method,
        user_shares: method === 'user_scenario' ? customShares : undefined
      });
      setComposition(res);
    } catch (err) {
      console.error('Failed to load composition', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComposition();
  }, [beach?.id, baseMass, method]);

  if (!beach) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <PieIcon className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="font-bold text-slate-800 text-base">Select a Beach to Inspect Composition</h3>
      </div>
    );
  }

  // Recovery breakdown pie data
  const recoveryPieData = composition
    ? [
        { name: 'Recyclable Stream', value: composition.recyclable_kg, pct: composition.recyclable_pct, color: '#0d9488' },
        { name: 'Non-Recyclable Residual', value: composition.non_recyclable_kg, pct: composition.non_recyclable_pct, color: '#f43f5e' },
        { name: 'Biodegradable / Organic', value: composition.biodegradable_kg, pct: composition.biodegradable_pct, color: '#10b981' }
      ]
    : [];

  // Material pie data
  const materialPieData = composition?.materials.map((m) => ({
    name: m.category,
    value: m.mass_kg,
    pct: m.percentage,
    color: MATERIAL_COLORS[m.category] || '#64748b'
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header & Method Switcher */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-bold text-slate-900 text-base">Waste Composition & Recovery Classification</h2>
              <span className="text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full">
                Calibrated Coastal Streams
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Material composition vs. recovery stream allocation for <b>{beach.name}</b> based on projected{' '}
              <b>{baseMass.toLocaleString()} kg</b> total waste.
            </p>
          </div>

          {/* Method Selector */}
          <div className="flex items-center space-x-1.5 bg-slate-100 p-1 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setMethod('historical_beach_profile')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                method === 'historical_beach_profile' ? 'bg-white text-teal-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Beach Historical Profile
            </button>
            <button
              onClick={() => setMethod('regional_profile')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                method === 'regional_profile' ? 'bg-white text-teal-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Regional Benchmark ({beach.region})
            </button>
            <button
              onClick={() => setMethod('user_scenario')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                method === 'user_scenario' ? 'bg-white text-teal-800 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Custom Scenario
            </button>
          </div>
        </div>

        {/* Methodology & Classification Warning */}
        <div className="p-3 bg-teal-50/60 border border-teal-200/60 rounded-xl text-xs text-teal-900 space-y-1">
          <div className="flex items-center space-x-1.5 font-bold">
            <Info className="w-3.5 h-3.5 text-teal-700" />
            <span>Dual Classification Policy</span>
          </div>
          <p className="text-[11px] text-teal-800/90 leading-relaxed">
            <b>Material Composition</b> (e.g. plastic polymers, metals, glass containers) and <b>Treatment Classes</b> (recyclable, non-recyclable, compostable) are distinct concepts. Highly degraded coastal marine plastics and thin multilayer packaging cannot be processed in standard municipal recycling facilities and are classified into non-recyclable residual streams.
          </p>
        </div>
      </div>

      {/* Dual Charts Grid: Material vs Recovery */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Material Composition Donut */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Material Breakdown</h3>
              <p className="text-xs text-slate-500">Physical categories based on beach cleanup records.</p>
            </div>
            <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full border border-slate-200">
              Sum: 100% Normalized
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={materialPieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={3}
                >
                  {materialPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any, name: string) => [
                    `${Number(val).toLocaleString()} kg`,
                    name
                  ]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recovery Stream Donut */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Recovery & Treatment Streams</h3>
              <p className="text-xs text-slate-500">Realistic operational disposition classification.</p>
            </div>
            <div className="flex items-center space-x-1 text-emerald-700 text-xs font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Verified</span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={recoveryPieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={3}
                >
                  {recoveryPieData.map((entry, index) => (
                    <Cell key={`cell-rec-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any, name: string) => [
                    `${Number(val).toLocaleString()} kg`,
                    name
                  ]}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Material Detailed Breakdown Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h3 className="font-bold text-slate-900 text-sm">Material Stream Quantification</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/70 text-slate-600">
                <th className="py-2.5 px-3 font-semibold">Material Stream</th>
                <th className="py-2.5 px-3 font-semibold text-right">Fraction (%)</th>
                <th className="py-2.5 px-3 font-semibold text-right">Projected Mass (kg)</th>
                <th className="py-2.5 px-3 font-semibold">Operational Disposition Class</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {composition?.materials.map((m) => (
                <tr key={m.category} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-slate-800 flex items-center space-x-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: MATERIAL_COLORS[m.category] || '#64748b' }}
                    ></span>
                    <span>{m.category}</span>
                  </td>
                  <td className="py-2.5 px-3 text-right font-semibold text-slate-700">{m.percentage}%</td>
                  <td className="py-2.5 px-3 text-right font-extrabold text-teal-700">
                    {m.mass_kg.toLocaleString()} kg
                  </td>
                  <td className="py-2.5 px-3 text-slate-600">
                    <span className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-slate-700">
                      {m.treatment_class}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>Source: {composition?.data_source_description}</span>
          <span className="text-[11px] text-amber-700">{composition?.uncertainty_warning}</span>
        </div>
      </div>
    </div>
  );
};
