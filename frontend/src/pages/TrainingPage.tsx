import React, { useState, useEffect } from 'react';
import { ModelInfo, TrainingJobStatus, DatasetItem } from '../types';
import { fetchModels, fetchDatasets, startTraining, fetchTrainingStatus } from '../services/api';
import {
  Cpu,
  Play,
  RotateCw,
  CheckCircle2,
  AlertCircle,
  Sliders,
  Database,
  ShieldCheck,
  TrendingDown,
  Layers,
  History
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

export const TrainingPage: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [datasets, setDatasets] = useState<DatasetItem[]>([]);
  const [selectedModel, setSelectedModel] = useState('lstm');
  const [selectedDataset, setSelectedDataset] = useState('demo_dataset');

  // Hyperparameters
  const [epochs, setEpochs] = useState(30);
  const [batchSize, setBatchSize] = useState(16);
  const [learningRate, setLearningRate] = useState(0.003);
  const [sequenceLength, setSequenceLength] = useState(12);
  const [hiddenDim, setHiddenDim] = useState(64);
  const [dropout, setDropout] = useState(0.15);

  // Active training job state
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<TrainingJobStatus | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    fetchModels().then((res) => setModels(res.models || [])).catch((e) => console.error(e));
    fetchDatasets().then((res) => setDatasets(res.datasets || [])).catch((e) => console.error(e));
  };

  useEffect(() => {
    loadData();
  }, []);

  // Poll active training job
  useEffect(() => {
    if (!activeJobId) return;

    const interval = setInterval(async () => {
      try {
        const status = await fetchTrainingStatus(activeJobId);
        setJobStatus(status);
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          loadData(); // Refresh models list
        }
      } catch (err) {
        console.error(err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [activeJobId]);

  const handleStartTraining = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      const res = await startTraining({
        model_type: selectedModel,
        dataset_id: selectedDataset,
        epochs,
        batch_size: batchSize,
        learning_rate: learningRate,
        sequence_length: sequenceLength,
        hidden_dim: hiddenDim,
        dropout
      });
      setActiveJobId(res.job_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start model training.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Build loss curve chart data
  const lossData = jobStatus?.train_loss_history.map((tLoss, i) => ({
    epoch: i + 1,
    trainLoss: tLoss,
    valLoss: jobStatus.val_loss_history?.[i] ?? null
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-2">
        <div className="flex items-center space-x-2">
          <Cpu className="w-5 h-5 text-teal-600" />
          <h2 className="font-bold text-slate-900 text-base">PyTorch Model Training Laboratory</h2>
          <span className="text-[10px] font-bold bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full">
            Real Backend Execution
          </span>
        </div>
        <p className="text-xs text-slate-500">
          Train custom deep learning time-series architectures with chronological validation and automatic checkpointing.
        </p>

        {/* Validation notice */}
        <div className="p-3 bg-emerald-50/60 border border-emerald-200/60 rounded-xl text-xs text-emerald-900 flex items-start space-x-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          <span>
            <b>Zero Data Leakage Guarantee:</b> Models are trained on the chronological 70% earliest records, validated on the subsequent 15%, and tested on the most recent 15%. Preprocessing scalers are fitted strictly on the training partition.
          </span>
        </div>
      </div>

      {/* Main Form & Live Training Monitor Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center space-x-2 text-slate-900 font-bold text-sm border-b border-slate-100 pb-3">
            <Sliders className="w-4 h-4 text-teal-600" />
            <span>Training Configuration</span>
          </div>

          <div className="space-y-3 text-xs">
            {/* Model Architecture */}
            <div>
              <label className="block text-slate-600 font-semibold mb-1">Architecture</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium text-slate-800 focus:outline-none focus:border-teal-500"
              >
                <option value="lstm">Standard LSTM (Deep Recurrent Forecaster)</option>
                <option value="encoder_decoder">LSTM Encoder-Decoder (Seq2Seq)</option>
                <option value="autoencoder">Sequence Autoencoder (Anomaly Detector)</option>
              </select>
            </div>

            {/* Dataset */}
            <div>
              <label className="block text-slate-600 font-semibold mb-1">Dataset</label>
              <select
                value={selectedDataset}
                onChange={(e) => setSelectedDataset(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl font-medium text-slate-800 focus:outline-none focus:border-teal-500"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.total_rows} rows)
                  </option>
                ))}
              </select>
            </div>

            {/* Epochs Slider */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-slate-600 font-medium">Epochs</span>
                <span className="font-bold text-teal-700">{epochs}</span>
              </div>
              <input
                type="range"
                min="10"
                max="60"
                step="5"
                value={epochs}
                onChange={(e) => setEpochs(parseInt(e.target.value))}
                className="w-full accent-teal-600"
              />
            </div>

            {/* Batch Size & Learning Rate */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Batch Size</label>
                <select
                  value={batchSize}
                  onChange={(e) => setBatchSize(parseInt(e.target.value))}
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-800"
                >
                  <option value={8}>8</option>
                  <option value={16}>16</option>
                  <option value={32}>32</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-1">Learning Rate</label>
                <select
                  value={learningRate}
                  onChange={(e) => setLearningRate(parseFloat(e.target.value))}
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-800"
                >
                  <option value={0.001}>0.001</option>
                  <option value={0.003}>0.003</option>
                  <option value={0.005}>0.005</option>
                  <option value={0.01}>0.01</option>
                </select>
              </div>
            </div>

            {/* Hidden Dim & Dropout */}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Hidden Units</label>
                <select
                  value={hiddenDim}
                  onChange={(e) => setHiddenDim(parseInt(e.target.value))}
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-800"
                >
                  <option value={32}>32 units</option>
                  <option value={64}>64 units</option>
                  <option value={128}>128 units</option>
                </select>
              </div>
              <div>
                <label className="block text-slate-600 font-medium mb-1">Dropout Rate</label>
                <select
                  value={dropout}
                  onChange={(e) => setDropout(parseFloat(e.target.value))}
                  className="w-full px-2.5 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-800"
                >
                  <option value={0.1}>0.10</option>
                  <option value={0.15}>0.15</option>
                  <option value={0.25}>0.25</option>
                </select>
              </div>
            </div>

            {/* Sequence Length */}
            <div>
              <label className="block text-slate-600 font-medium mb-1">Lookback Window (Sequence Length)</label>
              <select
                value={sequenceLength}
                onChange={(e) => setSequenceLength(parseInt(e.target.value))}
                className="w-full px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-800"
              >
                <option value={6}>6 Months Lookback</option>
                <option value={12}>12 Months Lookback (Annual cycle)</option>
                <option value={18}>18 Months Lookback</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleStartTraining}
            disabled={isSubmitting || jobStatus?.status === 'training'}
            className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2.5 rounded-xl text-xs flex items-center justify-center space-x-2 shadow-sm transition-all disabled:opacity-50"
          >
            {isSubmitting || jobStatus?.status === 'training' ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin" />
                <span>Training in Background...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Start Model Training</span>
              </>
            )}
          </button>

          {error && (
            <div className="p-2.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Live Training Progress & Loss Curves */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Real-Time Training Monitor</h3>
                <p className="text-xs text-slate-500">Live loss tracking and validation metrics convergence.</p>
              </div>

              {jobStatus && (
                <span
                  className={`text-xs font-bold px-2.5 py-1 rounded-full border ${
                    jobStatus.status === 'completed'
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : jobStatus.status === 'training'
                      ? 'bg-teal-50 text-teal-700 border-teal-200 animate-pulse'
                      : jobStatus.status === 'failed'
                      ? 'bg-red-50 text-red-700 border-red-200'
                      : 'bg-slate-100 text-slate-700 border-slate-200'
                  }`}
                >
                  Status: {jobStatus.status.toUpperCase()}
                </span>
              )}
            </div>

            {/* Progress Bar */}
            {jobStatus && jobStatus.status === 'training' && (
              <div className="mt-3 space-y-1">
                <div className="flex justify-between text-xs text-slate-500 font-semibold">
                  <span>Epoch {jobStatus.current_epoch} of {jobStatus.total_epochs}</span>
                  <span>{Math.round(((jobStatus.current_epoch || 0) / (jobStatus.total_epochs || 1)) * 100)}%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-teal-600 transition-all duration-300"
                    style={{ width: `${Math.round(((jobStatus.current_epoch || 0) / (jobStatus.total_epochs || 1)) * 100)}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Loss Chart */}
            <div className="h-64 w-full mt-4">
              {lossData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={lossData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="epoch" tick={{ fontSize: 11, fill: '#64748b' }} unit=" ep" />
                    <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#ffffff', borderRadius: '0.75rem', border: '1px solid #e2e8f0', fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                    <Line
                      type="monotone"
                      dataKey="trainLoss"
                      stroke="#0f766e"
                      strokeWidth={2}
                      dot={false}
                      name="Training Loss (Huber / MSE)"
                    />
                    <Line
                      type="monotone"
                      dataKey="valLoss"
                      stroke="#f59e0b"
                      strokeWidth={2}
                      dot={false}
                      name="Validation Loss"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
                  <TrendingDown className="w-8 h-8 mb-2 stroke-1" />
                  <span>No active training loss history to render. Click "Start Model Training".</span>
                </div>
              )}
            </div>
          </div>

          {/* Training Results Footer */}
          {jobStatus?.metrics && (
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 text-xs">
              <span className="font-bold text-slate-800">Test Split Evaluation Results:</span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-slate-600 pt-1 font-mono text-[11px]">
                <div>MAE: <b className="text-teal-700">{jobStatus.metrics.mae || 'N/A'} kg</b></div>
                <div>RMSE: <b className="text-teal-700">{jobStatus.metrics.rmse || 'N/A'} kg</b></div>
                <div>WAPE: <b className="text-teal-700">{jobStatus.metrics.wape_pct || 'N/A'}%</b></div>
                <div>R²: <b className="text-teal-700">{jobStatus.metrics.r2 || 'N/A'}</b></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
