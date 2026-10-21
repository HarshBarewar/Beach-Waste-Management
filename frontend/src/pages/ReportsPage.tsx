import React, { useState } from 'react';
import { Beach, ForecastResponse } from '../types';
import { generatePdfReport } from '../services/api';
import {
  FileText,
  Download,
  Printer,
  RotateCw,
  CheckCircle2,
  AlertTriangle,
  Leaf,
  Layers,
  DollarSign
} from 'lucide-react';

interface ReportsPageProps {
  beach: Beach | null;
  forecast: ForecastResponse | null;
  currency: string;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({
  beach,
  forecast,
  currency
}) => {
  const [modelType, setModelType] = useState('lstm');
  const [horizonMonths, setHorizonMonths] = useState(6);
  const [generating, setGenerating] = useState(false);
  const [reportResult, setReportResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  if (!beach) {
    return (
      <div className="p-12 text-center bg-white rounded-2xl border border-slate-200">
        <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="font-bold text-slate-800 text-base">Select a Beach to Generate Reports</h3>
      </div>
    );
  }

  const handleGeneratePdf = async () => {
    setGenerating(true);
    setError(null);
    setReportResult(null);
    try {
      const res = await generatePdfReport({
        beach_id: beach.id,
        model_type: modelType,
        horizon_months: horizonMonths,
        currency: currency
      });
      setReportResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate PDF assessment report.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-2">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-teal-600" />
          <h2 className="font-bold text-slate-900 text-base">Assessment Reports & Data Export Center</h2>
          <span className="text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full">
            ReportLab PDF Generator
          </span>
        </div>
        <p className="text-xs text-slate-500">
          Generate formal coastal waste assessments, including executive summaries, multi-horizon forecasts, recovery streams, recycling costs, and environmental action plans.
        </p>
      </div>

      {/* Report Generation Actions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* PDF Generator Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm border-b border-slate-100 pb-3">
            <Printer className="w-4 h-4 text-teal-600" />
            <span>Generate Official PDF Assessment</span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-600 font-semibold mb-1">Target Beach</label>
              <div className="p-2.5 bg-slate-50 rounded-xl font-bold text-slate-800 border border-slate-200">
                {beach.name} ({beach.country})
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-600 font-semibold mb-1">Forecasting Model</label>
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-800"
                >
                  <option value="lstm">PyTorch LSTM</option>
                  <option value="encoder_decoder">Encoder-Decoder</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-semibold mb-1">Forecast Horizon</label>
                <select
                  value={horizonMonths}
                  onChange={(e) => setHorizonMonths(parseInt(e.target.value))}
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-800"
                >
                  <option value={1}>1 Month</option>
                  <option value={3}>3 Months</option>
                  <option value={6}>6 Months</option>
                  <option value={12}>12 Months</option>
                </select>
              </div>
            </div>
          </div>

          <button
            onClick={handleGeneratePdf}
            disabled={generating}
            className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2.5 rounded-xl text-xs flex items-center justify-center space-x-2 shadow-sm transition-all disabled:opacity-50"
          >
            {generating ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin" />
                <span>Compiling Document...</span>
              </>
            ) : (
              <>
                <FileText className="w-4 h-4" />
                <span>Generate Assessment PDF</span>
              </>
            )}
          </button>

          {reportResult && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs space-y-2">
              <div className="flex items-center space-x-1.5 font-bold">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Report Successfully Created!</span>
              </div>
              <a
                href={reportResult.download_url}
                download
                className="w-full inline-flex items-center justify-center space-x-1.5 bg-emerald-600 hover:bg-emerald-700 text-white py-2 rounded-lg font-bold text-xs transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download PDF File</span>
              </a>
            </div>
          )}

          {error && (
            <div className="p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* CSV Data Export Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm border-b border-slate-100 pb-3">
              <Download className="w-4 h-4 text-teal-600" />
              <span>Raw Observation & Forecast CSV Export</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Export complete time-series dataset containing all {beach.total_observations} historical observations and model predictions formatted for Python, R, or Excel scientific analysis.
            </p>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 space-y-1 text-xs">
              <div className="font-semibold text-slate-700">Included Attributes:</div>
              <p className="text-[11px] text-slate-500">
                Observation dates, total waste mass, plastic, glass, metal, paper, organics, visitor counts, rainfall, temperature, and quality flags.
              </p>
            </div>
          </div>

          <a
            href={`/api/reports/export-csv/${beach.id}`}
            download
            className="w-full bg-slate-800 hover:bg-slate-900 text-white font-bold py-2.5 rounded-xl text-xs flex items-center justify-center space-x-2 transition-all shadow-sm"
          >
            <Download className="w-4 h-4" />
            <span>Download Complete CSV Dataset</span>
          </a>
        </div>

        {/* Environmental Action Recommendations Summary */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 text-teal-800 font-bold text-sm border-b border-slate-100 pb-3">
              <Leaf className="w-4 h-4 text-teal-600" />
              <span>Environmental Recommendations</span>
            </div>
            <div className="space-y-2 pt-2 text-xs text-slate-600">
              <p>• <b>Source Reduction:</b> Implement single-use plastic deposit-refund kiosks around primary promenade boardwalks.</p>
              <p>• <b>Storm Pre-Emption:</b> Deploy seasonal storm-drain debris interceptor booms before high-rainfall months.</p>
              <p>• <b>Volunteer Mobilization:</b> Align community weekend beach sweeps with projected peak visitor waves.</p>
              <p>• <b>Material Value Recovery:</b> Contract local PET bottle and aluminium reclaimers to offset hauling expenses.</p>
            </div>
          </div>

          <div className="text-[11px] text-slate-400 border-t border-slate-100 pt-3">
            Reports generated under BeachWaste AI academic guidelines.
          </div>
        </div>
      </div>
    </div>
  );
};
