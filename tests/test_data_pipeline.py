"""
Tests for Data Pipeline: Schema validation, synthetic generation, and preprocessor.
"""
import pytest
import pandas as pd
import numpy as np
from backend.app.data_pipeline.schema import validate_dataframe
from backend.app.data_pipeline.synthetic_generator import generate_synthetic_dataset
from backend.app.data_pipeline.preprocessor import TimeSeriesPreprocessor

def test_schema_validation_valid():
    df = pd.DataFrame([{
        "observation_id": "test_1",
        "beach_id": "beach_1",
        "beach_name": "Test Beach",
        "country": "Testland",
        "latitude": 10.0,
        "longitude": 20.0,
        "observation_date": "2024-01-01",
        "waste_mass_kg": 500.0,
    }])
    res = validate_dataframe(df)
    assert res["valid"] is True
    assert len(res["errors"]) == 0

def test_schema_validation_missing_columns():
    df = pd.DataFrame([{"observation_id": "test_1"}])
    res = validate_dataframe(df)
    assert res["valid"] is False
    assert any("Missing mandatory columns" in e for e in res["errors"])

def test_schema_validation_negative_waste():
    df = pd.DataFrame([{
        "observation_id": "test_1",
        "beach_id": "beach_1",
        "beach_name": "Test Beach",
        "country": "Testland",
        "latitude": 10.0,
        "longitude": 20.0,
        "observation_date": "2024-01-01",
        "waste_mass_kg": -50.0,
    }])
    res = validate_dataframe(df)
    assert res["valid"] is False
    assert any("negative values" in e for e in res["errors"])

def test_preprocessor_chronological_split():
    dates = pd.date_range("2021-01-01", "2024-12-01", freq="MS")
    df = pd.DataFrame({
        "beach_id": ["b1"] * len(dates),
        "observation_date": dates,
        "waste_mass_kg": np.random.uniform(500, 2000, len(dates)),
        "visitor_count": [1000] * len(dates),
        "temperature_c": [22.0] * len(dates),
        "rainfall_mm": [30.0] * len(dates),
        "wind_speed": [12.0] * len(dates),
        "storm_indicator": [0] * len(dates),
        "surveyed_area_m2": [10000.0] * len(dates),
        "observation_duration_hours": [5.0] * len(dates)
    })
    prep = TimeSeriesPreprocessor(sequence_length=12, horizon=6)
    df_eng = prep.engineer_features(df)
    (train_data, val_data, test_data) = prep.create_chronological_datasets(df_eng, 0.7, 0.15, horizon=6)

    X_tr, y_tr, _ = train_data
    X_te, y_te, _ = test_data

    assert len(X_tr) > 0
    assert len(X_te) > 0
    assert X_tr.shape[1] == 12
    assert y_tr.shape[1] == 6
