export interface Beach {
  id: string;
  name: string;
  country: string;
  region: string;
  latitude: number;
  longitude: number;
  coastal_type: string;
  is_favorite: boolean;
  sufficient_data_for_forecasting: boolean;
  total_observations: number;
  data_start_date: string | null;
  data_end_date: string | null;
  data_source_type: string;
  notes?: string;
  latest_monthly_waste_kg?: number;
  avg_monthly_waste_kg?: number;
  highest_recorded_waste_kg?: number;
  total_historical_waste_kg?: number;
  observations?: Observation[];
}

export interface Observation {
  observation_id: string;
  beach_id: string;
  observation_date: string;
  year: number;
  month: number;
  waste_mass_kg: number;
  waste_mass_unit: string;
  observation_duration_hours?: number;
  surveyed_area_m2?: number;
  plastic_mass_kg?: number;
  metal_mass_kg?: number;
  glass_mass_kg?: number;
  paper_mass_kg?: number;
  organic_waste_mass_kg?: number;
  textile_mass_kg?: number;
  other_waste_mass_kg?: number;
  recyclable_mass_kg?: number;
  non_recyclable_mass_kg?: number;
  biodegradable_mass_kg?: number;
  visitor_count?: number;
  tourism_season?: string;
  rainfall_mm?: number;
  temperature_c?: number;
  wind_speed?: number;
  storm_indicator?: number;
  cleanup_frequency?: string;
  collection_method?: string;
  source_name: string;
  data_quality_flag: string;
  is_synthetic: boolean;
  kg_per_m2?: number;
  kg_per_hour?: number;
}

export interface MonthlyForecastPoint {
  month_index: number;
  forecast_date: string;
  predicted_waste_kg: number;
  lower_bound_kg: number;
  upper_bound_kg: number;
  is_scenario_adjusted: boolean;
  predicted_recyclable_kg?: number;
  predicted_non_recyclable_kg?: number;
  predicted_biodegradable_kg?: number;
  predicted_plastic_kg?: number;
  predicted_metal_kg?: number;
  predicted_glass_kg?: number;
  predicted_paper_kg?: number;
  predicted_organic_kg?: number;
  predicted_other_kg?: number;
  estimated_cost_total?: number;
  currency: string;
}

export interface ForecastResponse {
  beach_id: string;
  beach_name: string;
  country: string;
  model_type: string;
  model_version: string;
  horizon_months: number;
  data_quality_notice: string;
  is_synthetic_baseline: boolean;
  monthly_forecasts: MonthlyForecastPoint[];
  cumulative_predicted_waste_kg: number;
  avg_monthly_predicted_kg: number;
  confidence_level: number;
  forecast_uncertainty_pct: number;
  test_mae?: number;
  test_rmse?: number;
  test_wape?: number;
  test_r2?: number;
  assumptions_and_notes: string[];
}

export interface MaterialShare {
  category: string;
  percentage: number;
  mass_kg: number;
  treatment_class: string;
}

export interface CompositionResponse {
  beach_id: string | null;
  total_waste_kg: number;
  estimation_method: string;
  materials: MaterialShare[];
  recyclable_pct: number;
  recyclable_kg: number;
  non_recyclable_pct: number;
  non_recyclable_kg: number;
  biodegradable_pct: number;
  biodegradable_kg: number;
  normalization_check: boolean;
  data_source_description: string;
  uncertainty_warning: string;
}

export interface MaterialCostDetail {
  category: string;
  mass_kg: number;
  unit_treatment_cost: number;
  total_treatment_cost: number;
}

export interface CostResponse {
  currency: string;
  currency_exchange_rate_to_usd: number;
  total_waste_kg: number;
  collection_cost: number;
  transport_cost: number;
  sorting_cost: number;
  recycling_processing_cost: number;
  non_recyclable_disposal_cost: number;
  organic_composting_cost: number;
  fixed_operating_cost: number;
  gross_total_cost: number;
  material_credits_or_revenue: number;
  net_total_cost: number;
  effective_cost_per_kg: number;
  materials_cost_breakdown: MaterialCostDetail[];
  is_illustrative_estimate: boolean;
  assumptions: string[];
}

export interface ModelInfo {
  model_type: string;
  name: string;
  is_trained: boolean;
  artifact_exists: boolean;
  last_trained_at?: string;
  metrics?: any;
  description: string;
}

export interface TrainingJobStatus {
  job_id: string;
  model_type: string;
  status: string;
  created_at: string;
  completed_at?: string;
  current_epoch?: number;
  total_epochs?: number;
  train_loss_history: number[];
  val_loss_history: number[];
  metrics?: any;
  error_message?: string;
}

export interface DatasetItem {
  id: string;
  name: string;
  filename: string;
  uploaded_at: string;
  total_rows: number;
  total_beaches: number;
  date_range_start?: string;
  date_range_end?: string;
  validation_status: string;
  is_synthetic: boolean;
  description?: string;
}

export interface ComparedBeach {
  beach_id: string;
  beach_name: string;
  country: string;
  region: string;
  coastal_type: string;
  total_observations: number;
  data_start_date: string;
  data_end_date: string;
  latest_waste_kg: number;
  avg_monthly_waste_kg: number;
  peak_recorded_waste_kg: number;
  surveyed_area_m2: number;
  avg_waste_intensity_kg_m2: number;
  avg_plastic_pct: number;
  avg_recyclable_pct: number;
  data_quality_flag: string;
  sufficient_data: boolean;
  recent_12m_trend: number[];
}
