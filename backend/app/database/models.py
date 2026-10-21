"""
SQLAlchemy ORM models for BeachWaste AI.
"""
from sqlalchemy import Column, Integer, Float, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.database.database import Base

class Beach(Base):
    __tablename__ = "beaches"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False, index=True)
    country = Column(String(64), nullable=False, index=True)
    region = Column(String(64), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    coastal_type = Column(String(64), default="Sandy Shore")
    is_favorite = Column(Boolean, default=False)
    sufficient_data_for_forecasting = Column(Boolean, default=True)
    total_observations = Column(Integer, default=0)
    data_start_date = Column(String(32), nullable=True)
    data_end_date = Column(String(32), nullable=True)
    data_source_type = Column(String(64), default="SYNTHETIC_DEMO")
    notes = Column(Text, nullable=True)

    observations = relationship("Observation", back_populates="beach", cascade="all, delete-orphan")

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    observation_id = Column(String(128), unique=True, index=True)
    beach_id = Column(String(64), ForeignKey("beaches.id"), nullable=False, index=True)
    observation_date = Column(String(32), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    waste_mass_kg = Column(Float, nullable=False)
    waste_mass_unit = Column(String(16), default="kg")
    
    # Normalization metrics
    observation_duration_hours = Column(Float, nullable=True)
    surveyed_area_m2 = Column(Float, nullable=True)
    
    # Material composition
    plastic_mass_kg = Column(Float, nullable=True)
    metal_mass_kg = Column(Float, nullable=True)
    glass_mass_kg = Column(Float, nullable=True)
    paper_mass_kg = Column(Float, nullable=True)
    organic_waste_mass_kg = Column(Float, nullable=True)
    textile_mass_kg = Column(Float, nullable=True)
    other_waste_mass_kg = Column(Float, nullable=True)

    # Treatment categories
    recyclable_mass_kg = Column(Float, nullable=True)
    non_recyclable_mass_kg = Column(Float, nullable=True)
    biodegradable_mass_kg = Column(Float, nullable=True)

    # Environmental & Human factors
    visitor_count = Column(Integer, nullable=True)
    tourism_season = Column(String(32), nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    storm_indicator = Column(Integer, default=0)
    cleanup_frequency = Column(String(32), default="monthly")
    collection_method = Column(String(64), default="manual_volunteer")
    
    # Metadata & Quality Flags
    source_name = Column(String(128), default="BeachWaste-AI-Synthetic-Demo")
    data_quality_flag = Column(String(64), default="SYNTHETIC_DEMO")
    is_synthetic = Column(Boolean, default=True)

    beach = relationship("Beach", back_populates="observations")

class DatasetRecord(Base):
    __tablename__ = "datasets"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    filename = Column(String(128), nullable=False)
    uploaded_at = Column(String(32), default=lambda: datetime.now(timezone.utc).isoformat())
    total_rows = Column(Integer, default=0)
    total_beaches = Column(Integer, default=0)
    date_range_start = Column(String(32), nullable=True)
    date_range_end = Column(String(32), nullable=True)
    validation_status = Column(String(32), default="VALIDATED")
    is_synthetic = Column(Boolean, default=False)
    description = Column(Text, nullable=True)

class ModelTrainingJob(Base):
    __tablename__ = "training_jobs"

    id = Column(String(64), primary_key=True)
    model_type = Column(String(64), nullable=False)  # lstm, encoder_decoder, autoencoder
    status = Column(String(32), default="pending")  # pending, training, completed, failed
    created_at = Column(String(32), default=lambda: datetime.now(timezone.utc).isoformat())
    completed_at = Column(String(32), nullable=True)
    dataset_id = Column(String(64), default="demo_dataset")
    hyperparams = Column(Text, nullable=True)  # JSON string
    train_loss_history = Column(Text, nullable=True)  # JSON string
    val_loss_history = Column(Text, nullable=True)  # JSON string
    metrics = Column(Text, nullable=True)  # JSON string (MAE, RMSE, WAPE, R2, etc.)
    artifact_path = Column(String(256), nullable=True)
    error_message = Column(Text, nullable=True)

class CostConfiguration(Base):
    __tablename__ = "cost_configurations"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    currency = Column(String(8), default="USD")
    collection_cost_per_kg = Column(Float, default=0.45)
    transport_cost_per_kg = Column(Float, default=0.20)
    sorting_cost_per_kg = Column(Float, default=0.15)
    recycling_processing_per_kg = Column(Float, default=0.35)
    non_recyclable_disposal_per_kg = Column(Float, default=0.50)
    organic_composting_per_kg = Column(Float, default=0.18)
    material_revenue_per_kg = Column(Float, default=0.12)
    fixed_monthly_cost = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
