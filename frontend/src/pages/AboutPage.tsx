import React from 'react';
import {
  BookOpen,
  Cpu,
  Layers,
  ShieldCheck,
  TrendingUp,
  PieChart,
  DollarSign,
  AlertTriangle,
  FileCode,
  GraduationCap
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-800 to-cyan-900 rounded-3xl p-8 text-white shadow-xl shadow-teal-900/10 space-y-3">
        <div className="flex items-center space-x-2 text-teal-200 text-xs font-bold uppercase tracking-wider">
          <GraduationCap className="w-4 h-4" />
          <span>Deep Learning Lab Research Project</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
          BeachWaste AI: Architecture & Scientific Methodology
        </h1>
        <p className="text-xs sm:text-sm text-teal-100/90 leading-relaxed max-w-3xl">
          An end-to-end deep learning system for global coastal debris monitoring, multi-step time-series forecasting,
          waste composition stream classification, and transparent municipal recycling cost estimation.
        </p>
      </div>

      {/* 4 Distinct Core Tasks & Why They Differ */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
          <Layers className="w-5 h-5 text-teal-600" />
          <span>1. The Four Distinct Analytic Tasks</span>
        </h2>
        <p className="text-xs text-slate-600 leading-relaxed">
          A fundamental scientific principle of BeachWaste AI is strictly separating four analytical responsibilities.
          Confusing or conflating these leads to severe methodological flaws:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="flex items-center space-x-2 text-teal-800 font-bold">
              <TrendingUp className="w-4 h-4 text-teal-600" />
              <span>Task A: Multi-Step Waste Quantity Forecasting</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              <b>Method:</b> PyTorch LSTM and Seq2Seq Encoder-Decoder models.
              <br />
              <b>Role:</b> Predicts aggregate waste mass (kg) across 1, 3, 6, and 12-month horizons using historical temporal sequences, cyclical seasonality, and weather covariates.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="flex items-center space-x-2 text-sky-800 font-bold">
              <PieChart className="w-4 h-4 text-sky-600" />
              <span>Task B: Waste Composition & Recovery Classification</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              <b>Method:</b> Dual physical material & recovery stream mapping.
              <br />
              <b>Role:</b> Total mass alone cannot tell what materials are present. Composition requires empirical beach survey baselines, regional coastal benchmarks, or explicitly parameterized user scenarios.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="flex items-center space-x-2 text-amber-800 font-bold">
              <ShieldCheck className="w-4 h-4 text-amber-600" />
              <span>Task C: Waste Pattern Anomaly Detection</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              <b>Method:</b> Sequence Autoencoder with latent bottleneck.
              <br />
              <b>Role:</b> Computes reconstruction error (MSE) to flag atypical events (e.g., severe storm washup or tourist surges). Anomalies are not treated as erroneous or corrupt data.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="flex items-center space-x-2 text-purple-800 font-bold">
              <DollarSign className="w-4 h-4 text-purple-600" />
              <span>Task D: Recycling & Treatment Cost Estimation</span>
            </div>
            <p className="text-slate-600 leading-relaxed">
              <b>Method:</b> Multi-stage lifecycle operational accounting with currency exchange.
              <br />
              <b>Role:</b> Translates physical quantities into operational expenditures (collection, haulage, sorting, recovery, disposal minus revenue).
            </p>
          </div>
        </div>
      </div>

      {/* Deep Learning Mathematical Formulations */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
          <FileCode className="w-5 h-5 text-teal-600" />
          <span>2. Deep Learning Mathematical Formulations</span>
        </h2>

        {/* LSTM Section */}
        <div className="space-y-2 text-xs">
          <h3 className="font-bold text-slate-800">PyTorch LSTM Recurrent Gates</h3>
          <p className="text-slate-600">
            Given input vector x(t) and prior hidden state h(t-1), the LSTM cell computes gating activations:
          </p>
          <div className="p-3 bg-slate-900 text-teal-300 font-mono text-[11px] rounded-xl space-y-1">
            <p>f_t = σ(W_f · [h_(t-1), x_t] + b_f)       // Forget Gate</p>
            <p>i_t = σ(W_i · [h_(t-1), x_t] + b_i)       // Input Gate</p>
            <p>c̃_t = tanh(W_c · [h_(t-1), x_t] + b_c)    // Candidate Memory</p>
            <p>c_t = f_t * c_(t-1) + i_t * c̃_t           // Updated Cell State</p>
            <p>o_t = σ(W_o · [h_(t-1), x_t] + b_o)       // Output Gate</p>
            <p>h_t = o_t * tanh(c_t)                     // Hidden Output State</p>
          </div>
        </div>

        {/* Evaluation Metrics */}
        <div className="space-y-2 text-xs pt-3 border-t border-slate-100">
          <h3 className="font-bold text-slate-800">Evaluation Metrics Formulation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 font-mono text-[11px] space-y-1">
              <span className="font-bold text-slate-800 font-sans block">WAPE (Weighted Absolute Percentage Error):</span>
              <p className="text-teal-700">WAPE = ( ∑ |y_t - ŷ_t| / ∑ |y_t| ) × 100%</p>
              <p className="text-[10px] text-slate-500 font-sans">
                Superior to standard MAPE when observations approach zero.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 font-mono text-[11px] space-y-1">
              <span className="font-bold text-slate-800 font-sans block">RMSE (Root Mean Squared Error):</span>
              <p className="text-teal-700">RMSE = √( (1/N) ∑ (y_t - ŷ_t)² )</p>
              <p className="text-[10px] text-slate-500 font-sans">
                Penalizes large outlier forecast errors heavily.
              </p>
            </div>
          </div>
        </div>

        {/* Cost Formula */}
        <div className="space-y-2 text-xs pt-3 border-t border-slate-100">
          <h3 className="font-bold text-slate-800">Municipal Treatment Cost Formulation</h3>
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl font-mono text-[11px] text-slate-800 space-y-1">
            <p>Gross Cost = (M × C_coll) + (M × C_trans) + (M × C_sort) + (M_rec × C_rec) + (M_disp × C_disp) + (M_comp × C_comp) + C_fixed</p>
            <p className="text-teal-700 font-bold">Net Budget = max(0, Gross Cost - (M_rec × R_credit))</p>
          </div>
        </div>
      </div>

      {/* Limitations & Ethical Research Conduct */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3 text-xs text-slate-600">
        <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-600" />
          <span>3. Limitations & Academic Integrity Standards</span>
        </h2>
        <ul className="space-y-2 list-disc pl-5">
          <li>
            <b>Data Provenance:</b> All synthetic demonstration data records are explicitly tagged as <code>SYNTHETIC_DEMO</code>. They should not be cited as empirical field measurements without real sensor deployments.
          </li>
          <li>
            <b>Geographic Generalization:</b> Neural time-series models learn localized seasonal rhythms. Predictions for unobserved beaches without historical series are speculative and must be interpreted with caution.
          </li>
          <li>
            <b>Recyclability Realism:</b> High salinity, sun degradation, and marine bio-fouling severely impair the commercial recyclability of ocean plastics. The model accounts for this by directing degraded plastics to residual streams.
          </li>
          <li>
            <b>Price Volatility:</b> Material salvage revenues fluctuate with international virgin resin markets and commodity scrap indices.
          </li>
        </ul>
      </div>
    </div>
  );
};
