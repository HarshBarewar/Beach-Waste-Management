"""
Pydantic schemas for forecasting, composition, cost, and training workflows.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ForecastRequest(BaseModel):
    beach_id: str
    model_type: str = Field(default="lstm", description="lstm | encoder_decoder | persistence | seasonal_naive")
    horizon_months: int = Field(default=6, description="1, 3, 6, or 12 months ahead")
    custom_scenario: Optional[Dict[str, Any]] = None  # e.g. {"visitor_multiplier": 1.2, "storm_increase": 1}
    currency: Optional[str] = "USD"
    cost_config_id: Optional[str] = "default"

class MonthlyForecastPoint(BaseModel):
    month_index: int  # 1 to N
    forecast_date: str  # YYYY-MM-01
    predicted_waste_kg: float
    lower_bound_kg: float
    upper_bound_kg: float
    is_scenario_adjusted: bool = False
    
    # Optional composition breakdown for this predicted month
    predicted_recyclable_kg: Optional[float] = None
    predicted_non_recyclable_kg: Optional[float] = None
    predicted_biodegradable_kg: Optional[float] = None
    
    # Material breakdown
    predicted_plastic_kg: Optional[float] = None
    predicted_metal_kg: Optional[float] = None
    predicted_glass_kg: Optional[float] = None
    predicted_paper_kg: Optional[float] = None
    predicted_organic_kg: Optional[float] = None
    predicted_other_kg: Optional[float] = None

    # Cost breakdown for this month
    estimated_cost_total: Optional[float] = None
    currency: Optional[str] = "USD"

class ForecastResponse(BaseModel):
    beach_id: str
    beach_name: str
    country: str
    model_type: str
    model_version: str
    horizon_months: int
    data_quality_notice: str
    is_synthetic_baseline: bool
    
    # Forecast points
    monthly_forecasts: List[MonthlyForecastPoint]
    cumulative_predicted_waste_kg: float
    avg_monthly_predicted_kg: float
    
    # Uncertainty metric
    confidence_level: float = 0.90
    forecast_uncertainty_pct: float
    
    # Model evaluation metrics reference
    test_mae: Optional[float] = None
    test_rmse: Optional[float] = None
    test_wape: Optional[float] = None
    test_r2: Optional[float] = None
    
    assumptions_and_notes: List[str] = []

class CompositionEstimateRequest(BaseModel):
    beach_id: Optional[str] = None
    total_waste_kg: float
    method: str = "historical_beach_profile"  # historical_beach_profile | regional_profile | user_scenario
    user_shares: Optional[Dict[str, float]] = None

class MaterialShare(BaseModel):
    category: str
    percentage: float
    mass_kg: float
    treatment_class: str

class CompositionEstimateResponse(BaseModel):
    beach_id: Optional[str]
    total_waste_kg: float
    estimation_method: str
    materials: List[MaterialShare]
    
    # Recovery summary
    recyclable_pct: float
    recyclable_kg: float
    non_recyclable_pct: float
    non_recyclable_kg: float
    biodegradable_pct: float
    biodegradable_kg: float
    
    normalization_check: bool
    data_source_description: str
    uncertainty_warning: str

class CostCalculationRequest(BaseModel):
    total_waste_kg: float
    currency: str = "USD"
    collection_cost_per_kg: Optional[float] = None
    transport_cost_per_kg: Optional[float] = None
    sorting_cost_per_kg: Optional[float] = None
    recycling_processing_per_kg: Optional[float] = None
    non_recyclable_disposal_per_kg: Optional[float] = None
    organic_composting_per_kg: Optional[float] = None
    material_revenue_per_kg: Optional[float] = None
    fixed_monthly_cost: Optional[float] = 0.0
    material_breakdown: Optional[Dict[str, float]] = None

class MaterialCostDetail(BaseModel):
    category: str
    mass_kg: float
    unit_treatment_cost: float
    total_treatment_cost: float

class CostCalculationResponse(BaseModel):
    currency: str
    currency_exchange_rate_to_usd: float
    total_waste_kg: float
    
    # Breakdown by operational step
    collection_cost: float
    transport_cost: float
    sorting_cost: float
    recycling_processing_cost: float
    non_recyclable_disposal_cost: float
    organic_composting_cost: float
    fixed_operating_cost: float
    gross_total_cost: float
    material_credits_or_revenue: float
    net_total_cost: float
    effective_cost_per_kg: float
    
    # Material-specific table
    materials_cost_breakdown: List[MaterialCostDetail]
    
    is_illustrative_estimate: bool = True
    assumptions: List[str]

class TrainingStartRequest(BaseModel):
    model_type: str = "lstm"  # lstm | encoder_decoder | autoencoder
    dataset_id: str = "demo_dataset"
    epochs: int = 40
    batch_size: int = 16
    learning_rate: float = 0.003
    sequence_length: int = 12
    hidden_dim: int = 64
    dropout: float = 0.15

class TrainingStatusResponse(BaseModel):
    job_id: str
    model_type: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    train_loss_history: List[float] = []
    val_loss_history: List[float] = []
    metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class BeachComparisonRequest(BaseModel):
    beach_ids: List[str]
    forecast_horizon: int = 6
    currency: str = "USD"
