import {
  Beach,
  ForecastResponse,
  CompositionResponse,
  CostResponse,
  ModelInfo,
  TrainingJobStatus,
  DatasetItem,
  ComparedBeach
} from '../types';

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchBeaches(params?: {
  search?: string;
  country?: string;
  region?: string;
  favoritesOnly?: boolean;
}): Promise<Beach[]> {
  const query = new URLSearchParams();
  if (params?.search) query.append('search', params.search);
  if (params?.country) query.append('country', params.country);
  if (params?.region) query.append('region', params.region);
  if (params?.favoritesOnly) query.append('favorites_only', 'true');

  const res = await fetch(`${API_BASE}/beaches?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch beaches');
  return res.json();
}

export async function fetchBeachDetail(beachId: string): Promise<Beach> {
  const res = await fetch(`${API_BASE}/beaches/${beachId}`);
  if (!res.ok) throw new Error(`Failed to load beach details for ${beachId}`);
  return res.json();
}

export async function toggleFavorite(beachId: string): Promise<{ id: string; is_favorite: boolean }> {
  const res = await fetch(`${API_BASE}/beaches/${beachId}/favorite`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to toggle favorite');
  return res.json();
}

export async function compareBeaches(beachIds: string[]): Promise<{ compared_beaches: ComparedBeach[]; comparability_warning: string }> {
  const res = await fetch(`${API_BASE}/beaches/compare?beach_ids=${beachIds.join(',')}`);
  if (!res.ok) throw new Error('Failed to compare beaches');
  return res.json();
}

export async function generateForecast(payload: {
  beach_id: string;
  model_type: string;
  horizon_months: number;
  custom_scenario?: any;
  currency?: string;
}): Promise<ForecastResponse> {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Prediction failed');
  }
  return res.json();
}

export async function estimateComposition(payload: {
  beach_id?: string;
  total_waste_kg: number;
  method?: string;
  user_shares?: Record<string, number>;
}): Promise<CompositionResponse> {
  const res = await fetch(`${API_BASE}/composition/estimate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to estimate composition');
  return res.json();
}

export async function estimateCost(payload: {
  total_waste_kg: number;
  currency?: string;
  collection_cost_per_kg?: number;
  transport_cost_per_kg?: number;
  sorting_cost_per_kg?: number;
  recycling_processing_per_kg?: number;
  non_recyclable_disposal_per_kg?: number;
  organic_composting_per_kg?: number;
  material_revenue_per_kg?: number;
  fixed_monthly_cost?: number;
  material_breakdown?: Record<string, number>;
}): Promise<CostResponse> {
  const res = await fetch(`${API_BASE}/cost/estimate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to calculate cost');
  return res.json();
}

export async function fetchCurrencies() {
  const res = await fetch(`${API_BASE}/cost/currencies`);
  if (!res.ok) throw new Error('Failed to load currencies');
  return res.json();
}

export async function fetchModels(): Promise<{ models: ModelInfo[] }> {
  const res = await fetch(`${API_BASE}/models`);
  if (!res.ok) throw new Error('Failed to list models');
  return res.json();
}

export async function fetchModelMetrics(modelId: string) {
  const res = await fetch(`${API_BASE}/models/${modelId}/metrics`);
  if (!res.ok) throw new Error('Failed to load model metrics');
  return res.json();
}

export async function startTraining(payload: {
  model_type: string;
  dataset_id?: string;
  epochs: number;
  batch_size: number;
  learning_rate: number;
  sequence_length: number;
  hidden_dim: number;
  dropout: number;
}) {
  const res = await fetch(`${API_BASE}/models/train`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start training');
  }
  return res.json();
}

export async function fetchTrainingStatus(jobId: string): Promise<TrainingJobStatus> {
  const res = await fetch(`${API_BASE}/models/status/${jobId}`);
  if (!res.ok) throw new Error('Failed to poll training status');
  return res.json();
}

export async function fetchAutoencoderAnomalies() {
  const res = await fetch(`${API_BASE}/models/autoencoder/anomalies`);
  if (!res.ok) throw new Error('Failed to run anomaly detector');
  return res.json();
}

export async function fetchDatasets(): Promise<{ datasets: DatasetItem[] }> {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) throw new Error('Failed to fetch datasets');
  return res.json();
}

export async function uploadDataset(formData: FormData) {
  const res = await fetch(`${API_BASE}/datasets/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ? (typeof err.detail === 'object' ? JSON.stringify(err.detail) : err.detail) : 'Upload failed');
  }
  return res.json();
}

export async function generatePdfReport(payload: {
  beach_id: string;
  model_type: string;
  horizon_months: number;
  currency: string;
}) {
  const res = await fetch(`${API_BASE}/reports/generate-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to build PDF assessment report');
  return res.json();
}
