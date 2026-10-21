import React, { useState, useEffect } from 'react';
import { Beach, ForecastResponse } from '../types';
import { generateForecast } from '../services/api';
import {
  TrendingUp,
  Cpu,
  Calendar,
  Sliders,
  Download,
  RefreshCw,
  AlertCircle,
  HelpCircle,
  ShieldCheck,
  Check
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

interface ForecastingPageProps {
  beach: Beach | null;
  forecast: ForecastResponse | null;
  onUpdateForecast: (f: ForecastResponse) => void;
  currency: string;
}

export const ForecastingPage: React.FC<ForecastingPageProps> = ({
  beach,
  forecast,
  onUpdateForecast,
  currency
}) => {
  const [modelType, setModelType] = useState('lstm');
  const [horizonMonths, setHorizonMonths] = useState(6);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Scenario parameters
  const [visitorMultiplier, setVisitorMultiplier] = useState(1.0);
  const [stormIncrease, setStormIncrease] = useState(0);

  const fetchPredictions = async () => {
    if (!beach) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await generateForecast({
        beach_id: beach.id,
        model_type: modelType,
        horizon_months: horizonMonths,
        custom_scenario: {
          visitor_multiplier: visitorMultiplier,
          storm_increase: stormIncrease
        },
        currency: currency
      });
      onUpdateForecast(resp);
    } catch (err: any) {
      setError(err.message || 'Failed to generate model forecast.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (beach) {
      fetchPredictions();
    }
  }, [beach?.id, modelType, horizonMonths, currency]);

  if (!beach) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <TrendingUp className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="font-bold text-slate-800 text-base">Select a Beach to Forecast</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
          Choose a monitored coastal beach from the global explorer to generate deep learning predictions.
        </p>
      </div>
    );
  }

  // Build combined chart data
  const recentHistory = beach.observations?.slice(-18) || [];
  const chartData = [
    ...recentHistory.map((o) => ({
      date: o.observation_date.slice(0, 7),
      actualWaste: o.waste_mass_kg,
      predictedWaste: null,
      lowerBound: null,
      upperBound: null
    })),
    ...(forecast?.monthly_forecasts || []).map((f) => ({
      date: f.forecast_date.slice(0, 7),
      actualWaste: null,
      predictedWaste: f.predicted_waste_kg,
      lowerBound: f.lower_bound_kg,
      upperBound: f.upper_bound_kg
    }))
  ];

  // Cumulative data for cumulative chart
  let cumSum = 0;
  const cumulativeData = (forecast?.monthly_forecasts || []).map((f) => {
    cumSum += f.predicted_waste_kg;
    return {
      date: f.forecast_date.slice(0, 7),
      monthly: f.predicted_waste_kg,
      cumulative: Math.round(cumSum)
    };
  });

  const exportCSV = () => {
    if (!forecast) return;
    const rows = [
      ['Month_Index', 'Forecast_Date', 'Predicted_Waste_kg', 'Lower_Bound_kg', 'Upper_Bound_kg', 'Estimated_Cost']
    ];
    forecast.monthly_forecasts.forEach((m) => {
      rows.push([
        String(m.month_index),
        m.forecast_date,
        String(m.predicted_waste_kg),
        String(m.lower_bound_kg),
        String(m.upper_bound_kg),
        String(m.estimated_cost_total || 0)
      ]);
    });
    const csvContent = 'data:text/csv;charset=utf-8,' + rows.map((e) => e.join(',')).join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${beach.id}_forecast_${horizonMonths}M.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Control Bar: Model Selector, Horizon, Scenario */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-bold text-slate-900 text-base">Waste Forecasting Engine</h2>
              <span className="text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full">
                Multi-Step Neural Network
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Forecasting future waste generation for <b>{beach.name}</b> ({beach.country}).
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={exportCSV}
              disabled={!forecast}
              className="bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
            <button
              onClick={fetchPredictions}
              disabled={loading}
              className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-1.5 rounded-xl text-xs font-bold flex items-center space-x-1.5 shadow-sm transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? 'Computing...' : 'Regenerate'}</span>
            </button>
          </div>
        </div>

        {/* Configuration Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-3 border-t border-slate-100 text-xs">
          {/* Model Selection */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Architecture / Model</label>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium text-slate-800 focus:outline-none focus:border-teal-500"
            >
              <option value="lstm">PyTorch Standard LSTM (Deep Recurrent)</option>
              <option value="encoder_decoder">PyTorch LSTM Encoder-Decoder (Seq2Seq)</option>
              <option value="seasonal_naive">Seasonal Naive Baseline (12-Mo Lag)</option>
              <option value="persistence">Persistence Baseline (Latest Value)</option>
            </select>
          </div>

          {/* Horizon Selection */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Forecast Horizon</label>
            <div className="grid grid-cols-4 gap-1">
              {[1, 3, 6, 12].map((h) => (
                <button
                  key={h}
                  onClick={() => setHorizonMonths(h)}
                  className={`py-1.5 text-center rounded-lg font-bold transition-all ${
                    horizonMonths === h
                      ? 'bg-teal-600 text-white shadow-sm'
                      : 'bg-slate-50 border border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {h}M
                </button>
              ))}
            </div>
          </div>

          {/* Scenario Slider: Visitors */}
          <div>
            <div className="flex justify-between text-[11px] font-semibold text-slate-500 mb-1">
              <span>Tourism Scenario</span>
              <span className="text-teal-700 font-bold">{visitorMultiplier}x</span>
            </div>
            <input
              type="range"
              min="0.7"
              max="1.5"
              step="0.05"
              value={visitorMultiplier}
              onChange={(e) => setVisitorMultiplier(parseFloat(e.target.value))}
              className="w-full accent-teal-600"
            />
          </div>

          {/* Scenario Switch: Storm */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Storm / Monsoon Event</label>
            <button
              onClick={() => setStormIncrease(stormIncrease === 0 ? 1 : 0)}
              className={`w-full py-2 rounded-xl font-semibold border flex items-center justify-center space-x-1.5 transition-all ${
                stormIncrease === 1
                  ? 'bg-amber-500 text-white border-amber-600 shadow-sm'
                  : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
              }`}
            >
              <span>{stormIncrease === 1 ? '⚡ Storm Surge Active (+25%)' : 'Normal Conditions'}</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Main Forecast Line Chart with Confidence Interval */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-bold text-slate-900 text-sm">
              Multi-Step Time-Series Forecast (18-Month Lookback + {horizonMonths}-Month Projection)
            </h3>
            <p className="text-xs text-slate-500">
              Shaded teal region illustrates 90% confidence prediction intervals generated via Monte Carlo Dropout.
            </p>
          </div>
          {forecast?.test_wape && (
            <div className="flex items-center space-x-2 text-xs bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
              <span className="text-slate-500 font-medium">Model Test WAPE:</span>
              <span className="font-bold text-teal-700">{forecast.test_wape}%</span>
              <span className="text-slate-400">|</span>
              <span className="text-slate-500 font-medium">R²:</span>
              <span className="font-bold text-teal-700">{forecast.test_r2}</span>
            </div>
          )}
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} unit=" kg" />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: '0.75rem', border: '1px solid #e2e8f0', fontSize: '12px' }}
                formatter={(val: any, name: string) => [
                  val !== null ? `${Number(val).toLocaleString()} kg` : '—',
                  name === 'actualWaste' ? 'Historical Observation' : name === 'predictedWaste' ? 'Model Forecast' : name
                ]}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Area
                type="monotone"
                dataKey="upperBound"
                stroke="transparent"
                fill="#99f6e4"
                fillOpacity={0.35}
                name="90% Prediction Interval"
              />
              <Area
                type="monotone"
                dataKey="lowerBound"
                stroke="transparent"
                fill="#ffffff"
                fillOpacity={1.0}
                legendType="none"
              />
              <Line
                type="monotone"
                dataKey="actualWaste"
                stroke="#0f766e"
                strokeWidth={2.5}
                dot={{ r: 3, fill: '#0f766e' }}
                name="Historical Waste (kg)"
              />
              <Line
                type="monotone"
                dataKey="predictedWaste"
                stroke="#0284c7"
                strokeWidth={2.5}
                strokeDasharray="5 5"
                dot={{ r: 4, fill: '#0284c7' }}
                name="Predicted Waste (kg)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Cumulative Chart & Monthly Breakdown Table Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cumulative Projected Mass */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
          <h3 className="font-bold text-slate-900 text-sm">Cumulative Waste Accumulation</h3>
          <p className="text-xs text-slate-500">
            Total projected beach waste over the {horizonMonths}-month forward horizon.
          </p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cumulativeData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} unit=" kg" />
                <Tooltip
                  formatter={(val: any) => [`${Number(val).toLocaleString()} kg`, 'Cumulative Projected']}
                />
                <Bar dataKey="cumulative" fill="#0d9488" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500">Cumulative Total:</span>
            <span className="font-bold text-teal-800 text-sm">
              {forecast?.cumulative_predicted_waste_kg?.toLocaleString() || 0} kg
            </span>
          </div>
        </div>

        {/* Monthly Projection Table */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-bold text-slate-900 text-sm">Monthly Prediction Schedule</h3>
              <span className="text-xs text-slate-500">
                Avg: <b>{forecast?.avg_monthly_predicted_kg?.toLocaleString() || 0} kg/mo</b>
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/70 text-slate-600">
                    <th className="py-2.5 px-3 font-semibold">Step</th>
                    <th className="py-2.5 px-3 font-semibold">Forecast Date</th>
                    <th className="py-2.5 px-3 font-semibold text-right">Predicted Mass</th>
                    <th className="py-2.5 px-3 font-semibold text-right">90% Range</th>
                    <th className="py-2.5 px-3 font-semibold text-right">Recyclable (est)</th>
                    <th className="py-2.5 px-3 font-semibold text-right">Treatment Cost</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {forecast?.monthly_forecasts.map((pt) => (
                    <tr key={pt.month_index} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-2 px-3 font-medium text-slate-500">+{pt.month_index} mo</td>
                      <td className="py-2 px-3 font-semibold text-slate-800">{pt.forecast_date}</td>
                      <td className="py-2 px-3 text-right font-extrabold text-teal-700">
                        {pt.predicted_waste_kg.toLocaleString()} kg
                      </td>
                      <td className="py-2 px-3 text-right text-slate-500 font-mono text-[11px]">
                        [{pt.lower_bound_kg} - {pt.upper_bound_kg}]
                      </td>
                      <td className="py-2 px-3 text-right text-slate-600">
                        {pt.predicted_recyclable_kg?.toLocaleString() || '—'} kg
                      </td>
                      <td className="py-2 px-3 text-right font-semibold text-slate-800">
                        {currency} {pt.estimated_cost_total ? Math.round(pt.estimated_cost_total).toLocaleString() : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
            <span>Model: {modelType.toUpperCase()} • Direct Multi-Step • PyTorch 2.9</span>
            <span>Uncertainty: ±{forecast?.forecast_uncertainty_pct || 15}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};
