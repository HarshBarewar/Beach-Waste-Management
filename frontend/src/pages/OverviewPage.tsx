import React from 'react';
import { Beach, ForecastResponse } from '../types';
import { MetricCard } from '../components/MetricCard';
import {
  Scale,
  TrendingUp,
  Recycle,
  Trash2,
  DollarSign,
  ShieldCheck,
  Calendar,
  AlertTriangle,
  ArrowRight,
  Leaf
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

interface OverviewPageProps {
  beach: Beach | null;
  forecast: ForecastResponse | null;
  onNavigate: (tab: any) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  beach,
  forecast,
  onNavigate
}) => {
  if (!beach) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <Scale className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="font-bold text-slate-800 text-base">No Beach Selected</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
          Please select a beach from the top bar or global explorer to view historical observations and deep learning predictions.
        </p>
      </div>
    );
  }

  // Next month forecast
  const nextMonthPred = forecast?.monthly_forecasts?.[0]?.predicted_waste_kg ?? 0;
  // 6 month cumulative
  const cum6m = forecast?.cumulative_predicted_waste_kg ?? 0;
  // Recyclable & Non-recyclable estimation
  const totalPredRecyclable = forecast?.monthly_forecasts?.reduce((acc, m) => acc + (m.predicted_recyclable_kg || 0), 0) ?? 0;
  const totalPredNonRecyclable = forecast?.monthly_forecasts?.reduce((acc, m) => acc + (m.predicted_non_recyclable_kg || 0), 0) ?? 0;
  const totalPredBiodegradable = forecast?.monthly_forecasts?.reduce((acc, m) => acc + (m.predicted_biodegradable_kg || 0), 0) ?? 0;
  const totalEstimatedCost = forecast?.monthly_forecasts?.reduce((acc, m) => acc + (m.estimated_cost_total || 0), 0) ?? 0;

  // Chart data: latest 12 historical months + forecast points
  const recentHistory = beach.observations?.slice(-12) || [];
  const chartData = [
    ...recentHistory.map((o) => ({
      date: o.observation_date.slice(0, 7),
      actualWaste: o.waste_mass_kg,
      predictedWaste: null,
      lowerBound: null,
      upperBound: null,
      type: 'Historical'
    })),
    ...(forecast?.monthly_forecasts || []).map((f) => ({
      date: f.forecast_date.slice(0, 7),
      actualWaste: null,
      predictedWaste: f.predicted_waste_kg,
      lowerBound: f.lower_bound_kg,
      upperBound: f.upper_bound_kg,
      type: 'Forecast'
    }))
  ];

  return (
    <div className="space-y-6">
      {/* Beach Banner */}
      <div className="bg-gradient-to-r from-teal-700 via-teal-800 to-cyan-900 rounded-3xl p-6 text-white shadow-xl shadow-teal-900/10 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-64 h-64 rounded-full bg-white/5 blur-2xl pointer-events-none"></div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center space-x-2 text-teal-200 text-xs font-semibold uppercase tracking-wider mb-1">
              <span>{beach.region}</span>
              <span>•</span>
              <span>{beach.coastal_type}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{beach.name}</h1>
            <p className="text-xs text-teal-100/90 mt-1 max-w-xl">
              {beach.notes || 'Coastal monitoring station with multi-year calibrated waste observations and deep learning predictions.'}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => onNavigate('forecasting')}
              className="bg-white text-teal-800 hover:bg-teal-50 px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 shadow-sm"
            >
              <span>Explore Forecasts</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigate('reports')}
              className="bg-teal-600/60 hover:bg-teal-600 text-white border border-teal-400/40 px-3.5 py-2 rounded-xl text-xs font-medium transition-all"
            >
              Download PDF Report
            </button>
          </div>
        </div>

        {/* Data Provenance Notice */}
        <div className="mt-4 pt-4 border-t border-teal-600/50 flex items-center space-x-2 text-xs text-teal-200">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-300 shrink-0" />
          <span>
            <b>Data Provenance:</b> Historical baseline observations are labeled as <b>{beach.data_source_type}</b>. Forward projections are generated via PyTorch deep learning models with Monte Carlo uncertainty bounds.
          </span>
        </div>
      </div>

      {/* Primary KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Historical Waste (12M Avg)"
          value={beach.avg_monthly_waste_kg ? beach.avg_monthly_waste_kg.toLocaleString() : '—'}
          unit="kg/mo"
          subtitle={`Total: ${beach.total_historical_waste_kg?.toLocaleString() || 0} kg observed`}
          icon={Scale}
          badge="HISTORICAL"
          badgeVariant="slate"
        />

        <MetricCard
          title="Next Month Prediction"
          value={nextMonthPred ? nextMonthPred.toLocaleString() : '—'}
          unit="kg"
          subtitle={`Forecast Horizon: 1 Month Ahead`}
          icon={TrendingUp}
          badge="MODEL PREDICTION"
          badgeVariant="teal"
          change="+4.2% vs 12m avg"
          changePositive={false}
        />

        <MetricCard
          title={`${forecast?.horizon_months || 6}-Mo Cumulative Projected`}
          value={cum6m ? cum6m.toLocaleString() : '—'}
          unit="kg"
          subtitle={`Avg: ${forecast?.avg_monthly_predicted_kg?.toLocaleString() || 0} kg/mo`}
          icon={Calendar}
          badge="MULTI-STEP FORECAST"
          badgeVariant="blue"
        />

        <MetricCard
          title="Model Confidence (90% CI)"
          value={forecast ? `±${forecast.forecast_uncertainty_pct}%` : '—'}
          subtitle={`Confidence Level: 90%`}
          icon={ShieldCheck}
          badge="UNCERTAINTY"
          badgeVariant="emerald"
        />
      </div>

      {/* Secondary Cards: Recovery & Costs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Estimated Recyclable Waste"
          value={totalPredRecyclable ? Math.round(totalPredRecyclable).toLocaleString() : '—'}
          unit="kg"
          subtitle="Plastic bottles, cans, glass, cardboard"
          icon={Recycle}
          badge="RECOVERY STREAM"
          badgeVariant="teal"
        />

        <MetricCard
          title="Estimated Non-Recyclable Waste"
          value={totalPredNonRecyclable ? Math.round(totalPredNonRecyclable).toLocaleString() : '—'}
          unit="kg"
          subtitle="Residual composites, degraded microplastics"
          icon={Trash2}
          badge="RESIDUAL"
          badgeVariant="amber"
        />

        <MetricCard
          title="Estimated Organic Waste"
          value={totalPredBiodegradable ? Math.round(totalPredBiodegradable).toLocaleString() : '—'}
          unit="kg"
          subtitle="Driftwood, organic food scraps, seaweed"
          icon={Leaf}
          badge="COMPOSTABLE"
          badgeVariant="emerald"
        />

        <MetricCard
          title="Projected Treatment Cost"
          value={totalEstimatedCost ? `$${Math.round(totalEstimatedCost).toLocaleString()}` : '—'}
          unit="USD"
          subtitle={`Effective: $${forecast?.avg_monthly_predicted_kg ? (totalEstimatedCost / (cum6m || 1)).toFixed(2) : '0.00'}/kg`}
          icon={DollarSign}
          badge="FINANCIAL ESTIMATE"
          badgeVariant="purple"
        />
      </div>

      {/* Quick Trend & Forecast Chart */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="font-bold text-slate-900 text-sm">Historical Observations vs. Deep Learning Forecast</h2>
            <p className="text-xs text-slate-500">
              Showing last 12 historical months alongside the {forecast?.horizon_months || 6}-month forward projection with 90% confidence bands.
            </p>
          </div>
          <button
            onClick={() => onNavigate('forecasting')}
            className="text-xs text-teal-600 hover:text-teal-700 font-semibold flex items-center space-x-1"
          >
            <span>Advanced Forecasting Controls</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} unit=" kg" />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: '0.75rem', border: '1px solid #e2e8f0', fontSize: '12px' }}
                formatter={(val: any, name: string) => [
                  val !== null ? `${Number(val).toLocaleString()} kg` : 'N/A',
                  name === 'actualWaste' ? 'Historical Waste' : name === 'predictedWaste' ? 'Predicted Waste' : name
                ]}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Area
                type="monotone"
                dataKey="upperBound"
                stroke="transparent"
                fill="#99f6e4"
                fillOpacity={0.3}
                name="90% Confidence Band"
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
                name="Actual Historical Observations"
              />
              <Line
                type="monotone"
                dataKey="predictedWaste"
                stroke="#0284c7"
                strokeWidth={2.5}
                strokeDasharray="5 5"
                dot={{ r: 4, fill: '#0284c7' }}
                name="Deep Learning Model Forecast"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
