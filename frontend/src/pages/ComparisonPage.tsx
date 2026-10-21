import React, { useState, useEffect } from 'react';
import { Beach, ComparedBeach } from '../types';
import { compareBeaches } from '../services/api';
import {
  GitCompare,
  AlertTriangle,
  Scale,
  DollarSign,
  Recycle,
  Check,
  X,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

interface ComparisonPageProps {
  beaches: Beach[];
  comparisonList: string[];
  onToggleComparison: (beachId: string) => void;
  currency: string;
}

export const ComparisonPage: React.FC<ComparisonPageProps> = ({
  beaches,
  comparisonList,
  onToggleComparison,
  currency
}) => {
  const [data, setData] = useState<{ compared_beaches: ComparedBeach[]; comparability_warning: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [metricMode, setMetricMode] = useState<'mass' | 'intensity'>('mass');

  useEffect(() => {
    // If list is empty, default to first 3 beaches for demo comparison
    const targetIds = comparisonList.length > 0
      ? comparisonList
      : beaches.slice(0, 3).map((b) => b.id);

    if (targetIds.length > 0) {
      setLoading(true);
      compareBeaches(targetIds)
        .then((res) => setData(res))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [comparisonList, beaches]);

  const compared = data?.compared_beaches || [];

  // Comparative chart data
  const chartData = compared.map((b) => ({
    name: b.beach_name.split(',')[0],
    avgMonthlyMassKg: b.avg_monthly_waste_kg,
    peakRecordedMassKg: b.peak_recorded_waste_kg,
    intensityKgM2: b.avg_waste_intensity_kg_m2 * 1000, // scaled to g/m2 for clear visualization
    plasticPct: b.avg_plastic_pct,
    recyclablePct: b.avg_recyclable_pct
  }));

  return (
    <div className="space-y-6">
      {/* Top Banner & Selector */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-bold text-slate-900 text-base">Multi-Beach Comparative Analysis</h2>
              <span className="text-[10px] font-bold bg-sky-50 text-sky-700 border border-sky-200 px-2 py-0.5 rounded-full">
                {compared.length} of 5 Beaches Selected
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Evaluating coastal waste profiles across differing geographical and climatic shorelines.
            </p>
          </div>

          <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setMetricMode('mass')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                metricMode === 'mass' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600'
              }`}
            >
              Absolute Mass (kg)
            </button>
            <button
              onClick={() => setMetricMode('intensity')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                metricMode === 'intensity' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600'
              }`}
            >
              Normalized Density (g/m²)
            </button>
          </div>
        </div>

        {/* Comparability Warning Alert */}
        <div className="p-3 bg-amber-50/70 border border-amber-200/80 rounded-xl text-xs text-amber-900 flex items-start space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <span>
            <b>Scientific Comparability Notice:</b> {data?.comparability_warning || (
              'Do not rank beaches as objectively cleaner or dirtier when surveyed areas or cleanup frequencies differ. Inspect normalized intensity (kg/m²) for fair comparisons.'
            )}
          </span>
        </div>

        {/* Selected Beach Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
          <span className="text-xs font-semibold text-slate-400">Comparing:</span>
          {compared.map((b) => (
            <span
              key={b.beach_id}
              className="inline-flex items-center space-x-1.5 bg-teal-50 text-teal-800 border border-teal-200 px-2.5 py-1 rounded-lg text-xs font-semibold"
            >
              <span>{b.beach_name}</span>
              <button
                onClick={() => onToggleComparison(b.beach_id)}
                className="text-teal-600 hover:text-teal-900"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
          {compared.length < 5 && (
            <span className="text-xs text-slate-400 italic">
              (Select up to {5 - compared.length} more beaches from Explorer)
            </span>
          )}
        </div>
      </div>

      {/* Comparative Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h3 className="font-bold text-slate-900 text-sm">
          {metricMode === 'mass' ? 'Monthly Waste Mass Comparison (kg)' : 'Normalized Waste Density Comparison (grams / m²)'}
        </h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis
                tick={{ fontSize: 11, fill: '#64748b' }}
                unit={metricMode === 'mass' ? ' kg' : ' g/m²'}
              />
              <Tooltip
                formatter={(val: any, name: string) => [
                  `${Number(val).toLocaleString()} ${metricMode === 'mass' ? 'kg' : 'g/m²'}`,
                  name === 'avgMonthlyMassKg'
                    ? '12-Month Average Mass'
                    : name === 'peakRecordedMassKg'
                    ? 'Peak Recorded Mass'
                    : 'Normalized Intensity'
                ]}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              {metricMode === 'mass' ? (
                <>
                  <Bar dataKey="avgMonthlyMassKg" fill="#0d9488" name="12-Month Avg Mass (kg)" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="peakRecordedMassKg" fill="#0284c7" name="Peak Recorded Mass (kg)" radius={[6, 6, 0, 0]} />
                </>
              ) : (
                <Bar dataKey="intensityKgM2" fill="#0f766e" name="Surface Density (grams / m²)" radius={[6, 6, 0, 0]} />
              )}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Side-by-Side Comparison Matrix */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h3 className="font-bold text-slate-900 text-sm">Detailed Side-by-Side Metric Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/70 text-slate-600">
                <th className="py-2.5 px-3 font-semibold">Attribute / Metric</th>
                {compared.map((b) => (
                  <th key={b.beach_id} className="py-2.5 px-3 font-bold text-slate-900">
                    {b.beach_name.split(',')[0]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr>
                <td className="py-2.5 px-3 font-semibold text-slate-500">Country & Region</td>
                {compared.map((b) => (
                  <td key={b.beach_id} className="py-2.5 px-3 text-slate-700">
                    {b.country} ({b.region})
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-slate-500">Coastal Shore Type</td>
                {compared.map((b) => (
                  <td key={b.beach_id} className="py-2.5 px-3 text-slate-700">
                    {b.coastal_type}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-slate-500">Surveyed Beach Area</td>
                {compared.map((b) => (
                  <td key={b.beach_id} className="py-2.5 px-3 font-medium text-slate-700">
                    {b.surveyed_area_m2.toLocaleString()} m²
                  </td>
                ))}
              </tr>
              <tr className="bg-teal-50/30">
                <td className="py-2.5 px-3 font-bold text-teal-900">Normalized Density (kg/m²)</td>
                {compared.map((b) => (
                  <td key={b.beach_id} className="py-2.5 px-3 font-extrabold text-teal-800">
                    {b.avg_waste_intensity_kg_m2.toFixed(4)} kg/m²
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-slate-500">Average Monthly Waste</td>
                {compared.map((b) => (
                  <td key={b.beach_id} className="py-2.5 px-3 font-bold text-slate-800">
                    {b.avg_monthly_waste_kg.toLocaleString()} kg
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-slate-500">Estimated Plastic Share</td>
                {compared.map((b) => (
                  <td key={b.beach_id} className="py-2.5 px-3 text-slate-700">
                    {b.avg_plastic_pct}%
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-slate-500">Recyclable Share</td>
                {compared.map((b) => (
                  <td key={b.beach_id} className="py-2.5 px-3 text-emerald-700 font-semibold">
                    {b.avg_recyclable_pct}%
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold text-slate-500">Data Coverage Period</td>
                {compared.map((b) => (
                  <td key={b.beach_id} className="py-2.5 px-3 text-slate-500 text-[11px]">
                    {b.data_start_date} to {b.data_end_date} ({b.total_observations} mos)
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
