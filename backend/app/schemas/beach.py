"""
Pydantic schemas for Beach and Observation data.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class BeachBase(BaseModel):
    id: str
    name: str
    country: str
    region: str
    latitude: float
    longitude: float
    coastal_type: Optional[str] = "Sandy Shore"
    is_favorite: Optional[bool] = False
    sufficient_data_for_forecasting: Optional[bool] = True
    total_observations: Optional[int] = 0
    data_start_date: Optional[str] = None
    data_end_date: Optional[str] = None
    data_source_type: Optional[str] = "SYNTHETIC_DEMO"
    notes: Optional[str] = None

class BeachResponse(BeachBase):
    class Config:
        from_attributes = True

class ObservationSchema(BaseModel):
    observation_id: str
    beach_id: str
    observation_date: str
    year: int
    month: int
    waste_mass_kg: float
    waste_mass_unit: str = "kg"
    observation_duration_hours: Optional[float] = None
    surveyed_area_m2: Optional[float] = None
    
    # Material breakdown
    plastic_mass_kg: Optional[float] = None
    metal_mass_kg: Optional[float] = None
    glass_mass_kg: Optional[float] = None
    paper_mass_kg: Optional[float] = None
    organic_waste_mass_kg: Optional[float] = None
    textile_mass_kg: Optional[float] = None
    other_waste_mass_kg: Optional[float] = None

    # Recovery breakdown
    recyclable_mass_kg: Optional[float] = None
    non_recyclable_mass_kg: Optional[float] = None
    biodegradable_mass_kg: Optional[float] = None

    # Environmental covariates
    visitor_count: Optional[int] = None
    tourism_season: Optional[str] = None
    rainfall_mm: Optional[float] = None
    temperature_c: Optional[float] = None
    wind_speed: Optional[float] = None
    storm_indicator: Optional[int] = 0
    cleanup_frequency: Optional[str] = "monthly"
    collection_method: Optional[str] = "manual_volunteer"
    
    source_name: str = "BeachWaste-AI-Synthetic-Demo"
    data_quality_flag: str = "SYNTHETIC_DEMO"
    is_synthetic: bool = True

    # Calculated metrics
    kg_per_m2: Optional[float] = None
    kg_per_hour: Optional[float] = None

    class Config:
        from_attributes = True

class BeachDetailResponse(BeachResponse):
    observations: List[ObservationSchema] = []
    latest_monthly_waste_kg: Optional[float] = None
    avg_monthly_waste_kg: Optional[float] = None
    highest_recorded_waste_kg: Optional[float] = None
    total_historical_waste_kg: Optional[float] = None
    data_coverage_months: Optional[int] = None
