import React, { useState, useEffect } from 'react';
import { Beach, ForecastResponse, CostResponse } from '../types';
import { estimateCost, fetchCurrencies } from '../services/api';
import {
  DollarSign,
  Truck,
  Layers,
  Recycle,
  Trash2,
  Leaf,
  Sliders,
  AlertCircle,
  HelpCircle,
  RotateCcw
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

interface CostsPageProps {
  beach: Beach | null;
  forecast: ForecastResponse | null;
  currency: string;
  onCurrencyChange: (c: string) => void;
}

export const CostsPage: React.FC<CostsPageProps> = ({
  beach,
  forecast,
  currency,
  onCurrencyChange
}) => {
  const [currencies, setCurrencies] = useState<any[]>([]);
  const [costData, setCostData] = useState<CostResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // Editable unit costs in USD
  const [collectionCost, setCollectionCost] = useState(0.45);
  const [transportCost, setTransportCost] = useState(0.20);
  const [sortingCost, setSortingCost] = useState(0.15);
  const [recyclingCost, setRecyclingCost] = useState(0.35);
  const [disposalCost, setDisposalCost] = useState(0.50);
  const [compostingCost, setCompostingCost] = useState(0.18);
  const [materialRevenue, setMaterialRevenue] = useState(0.12);
  const [fixedMonthly, setFixedMonthly] = useState(0.0);

  const baseWaste = forecast?.cumulative_predicted_waste_kg || beach?.avg_monthly_waste_kg || 2500;

  useEffect(() => {
    fetchCurrencies()
      .then((res) => setCurrencies(res.currencies || []))
      .catch((err) => console.error(err));
  }, []);

  const calculate = async () => {
    setLoading(true);
    try {
      const res = await estimateCost({
        total_waste_kg: baseWaste,
        currency: currency,
        collection_cost_per_kg: collectionCost,
        transport_cost_per_kg: transportCost,
        sorting_cost_per_kg: sortingCost,
        recycling_processing_per_kg: recyclingCost,
        non_recyclable_disposal_per_kg: disposalCost,
        organic_composting_per_kg: compostingCost,
        material_revenue_per_kg: materialRevenue,
        fixed_monthly_cost: fixedMonthly
      });
      setCostData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    calculate();
  }, [baseWaste, currency, collectionCost, transportCost, sortingCost, recyclingCost, disposalCost, compostingCost, materialRevenue, fixedMonthly]);

  const resetDefaults = () => {
    setCollectionCost(0.45);
    setTransportCost(0.20);
    setSortingCost(0.15);
    setRecyclingCost(0.35);
    setDisposalCost(0.50);
    setCompostingCost(0.18);
    setMaterialRevenue(0.12);
    setFixedMonthly(0.0);
  };

  if (!beach) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <DollarSign className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="font-bold text-slate-800 text-base">Select a Beach to Estimate Costs</h3>
      </div>
    );
  }

  // Cost breakdown chart data
  const chartData = costData
    ? [
        { name: 'Collection', cost: costData.collection_cost },
        { name: 'Transport', cost: costData.transport_cost },
        { name: 'Sorting', cost: costData.sorting_cost },
        { name: 'Recycling', cost: costData.recycling_processing_cost },
        { name: 'Disposal', cost: costData.non_recyclable_disposal_cost },
        { name: 'Composting', cost: costData.organic_composting_cost },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Top Header & Currency Selector */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-bold text-slate-900 text-base">Waste Treatment & Recycling Cost Estimator</h2>
              <span className="text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200 px-2 py-0.5 rounded-full">
                Financial Operations Model
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Cost projections for <b>{beach.name}</b> across <b>{baseWaste.toLocaleString()} kg</b> estimated waste.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            {/* Currency selector */}
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-semibold text-slate-500">Currency:</span>
              <select
                value={currency}
                onChange={(e) => onCurrencyChange(e.target.value)}
                className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800 focus:outline-none focus:border-teal-500"
              >
                {currencies.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.symbol} {c.code} - {c.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={resetDefaults}
              className="p-1.5 rounded-lg border border-slate-200 text-slate-400 hover:text-slate-700 hover:bg-slate-50 transition-colors"
              title="Reset to benchmark default unit rates"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Provenance and Illustrative Notice */}
        <div className="p-3 bg-amber-50/70 border border-amber-200/80 rounded-xl text-xs text-amber-900 flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <span>
            <b>Illustrative Financial Notice:</b> Unit rates represent standardized municipal and environmental NGO operational benchmarks. They are not contractual quotes. Users may adjust all parameters below to match local contract tariffs.
          </span>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-1">
          <span className="text-xs font-semibold text-slate-500">GROSS TREATMENT BUDGET</span>
          <div className="text-2xl font-extrabold text-slate-900">
            {currency} {costData?.gross_total_cost.toLocaleString()}
          </div>
          <span className="text-xs text-slate-400">Before material salvage revenue</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-1">
          <span className="text-xs font-semibold text-emerald-600">MATERIAL SALES REVENUE CREDIT</span>
          <div className="text-2xl font-extrabold text-emerald-600">
            - {currency} {costData?.material_credits_or_revenue.toLocaleString()}
          </div>
          <span className="text-xs text-slate-400">Reclaimed high-grade PET & metals</span>
        </div>

        <div className="bg-teal-50 rounded-2xl border border-teal-200 p-5 shadow-sm space-y-1">
          <span className="text-xs font-bold text-teal-800">NET REQUIRED BUDGET</span>
          <div className="text-2xl font-extrabold text-teal-900">
            {currency} {costData?.net_total_cost.toLocaleString()}
          </div>
          <span className="text-xs text-teal-700 font-medium">Final operating expenditure</span>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-1">
          <span className="text-xs font-semibold text-slate-500">EFFECTIVE COST / KG</span>
          <div className="text-2xl font-extrabold text-slate-900">
            {currency} {costData?.effective_cost_per_kg.toFixed(3)}
          </div>
          <span className="text-xs text-slate-400">Per kilogram collected & processed</span>
        </div>
      </div>

      {/* Operational Breakdown Chart & Editable Parameters Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cost by Operational Step Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
          <h3 className="font-bold text-slate-900 text-sm">Cost Allocation by Operational Lifecycle Step</h3>
          <p className="text-xs text-slate-500">Visualizing where treatment expenses are allocated across operations.</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} unit={` ${currency}`} />
                <Tooltip formatter={(val: any) => [`${currency} ${Number(val).toLocaleString()}`, 'Cost']} />
                <Bar dataKey="cost" fill="#0d9488" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Editable Parameter Controls */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm">
            <Sliders className="w-4 h-4 text-teal-600" />
            <span>Editable Unit Tariffs ($ USD)</span>
          </div>
          <p className="text-[11px] text-slate-500">Adjust unit costs to simulate local market conditions.</p>

          <div className="space-y-2.5 text-xs">
            <div>
              <div className="flex justify-between mb-0.5">
                <span className="text-slate-600">Collection / Labor</span>
                <span className="font-bold text-slate-800">${collectionCost.toFixed(2)}/kg</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="1.50"
                step="0.05"
                value={collectionCost}
                onChange={(e) => setCollectionCost(parseFloat(e.target.value))}
                className="w-full accent-teal-600"
              />
            </div>

            <div>
              <div className="flex justify-between mb-0.5">
                <span className="text-slate-600">Transportation / Haulage</span>
                <span className="font-bold text-slate-800">${transportCost.toFixed(2)}/kg</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.80"
                step="0.05"
                value={transportCost}
                onChange={(e) => setTransportCost(parseFloat(e.target.value))}
                className="w-full accent-teal-600"
              />
            </div>

            <div>
              <div className="flex justify-between mb-0.5">
                <span className="text-slate-600">Sorting & MRF Facility</span>
                <span className="font-bold text-slate-800">${sortingCost.toFixed(2)}/kg</span>
              </div>
              <input
                type="range"
                min="0.05"
                max="0.60"
                step="0.05"
                value={sortingCost}
                onChange={(e) => setSortingCost(parseFloat(e.target.value))}
                className="w-full accent-teal-600"
              />
            </div>

            <div>
              <div className="flex justify-between mb-0.5">
                <span className="text-slate-600">Recycling Processing</span>
                <span className="font-bold text-slate-800">${recyclingCost.toFixed(2)}/kg</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="1.00"
                step="0.05"
                value={recyclingCost}
                onChange={(e) => setRecyclingCost(parseFloat(e.target.value))}
                className="w-full accent-teal-600"
              />
            </div>

            <div>
              <div className="flex justify-between mb-0.5">
                <span className="text-slate-600">Residual Landfill / Disposal</span>
                <span className="font-bold text-slate-800">${disposalCost.toFixed(2)}/kg</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="1.20"
                step="0.05"
                value={disposalCost}
                onChange={(e) => setDisposalCost(parseFloat(e.target.value))}
                className="w-full accent-teal-600"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Material Specific Financial Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
        <h3 className="font-bold text-slate-900 text-sm">Material-Specific Cost Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/70 text-slate-600">
                <th className="py-2.5 px-3 font-semibold">Material Stream</th>
                <th className="py-2.5 px-3 font-semibold text-right">Projected Mass (kg)</th>
                <th className="py-2.5 px-3 font-semibold text-right">Unit Treatment Cost ({currency}/kg)</th>
                <th className="py-2.5 px-3 font-semibold text-right">Total Stream Cost ({currency})</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {costData?.materials_cost_breakdown.map((m) => (
                <tr key={m.category} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-slate-800">{m.category}</td>
                  <td className="py-2.5 px-3 text-right font-semibold text-slate-700">{m.mass_kg.toLocaleString()} kg</td>
                  <td className="py-2.5 px-3 text-right text-slate-600">
                    {currency} {m.unit_treatment_cost.toFixed(2)}
                  </td>
                  <td className="py-2.5 px-3 text-right font-extrabold text-teal-700">
                    {currency} {m.total_treatment_cost.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
