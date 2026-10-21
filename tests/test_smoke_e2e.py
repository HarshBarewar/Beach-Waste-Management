"""
End-to-end smoke test validating the complete BeachWaste AI workflow.
"""
import pytest
from pathlib import Path
from backend.app.data_pipeline.synthetic_generator import generate_synthetic_dataset
from backend.app.data_pipeline.preprocessor import TimeSeriesPreprocessor
from backend.app.forecasting.lstm import PyTorchLSTM
from backend.app.composition.estimator import estimate_waste_composition
from backend.app.cost_estimation.calculator import calculate_costs
from backend.app.reporting.pdf_generator import generate_pdf_report
from backend.app.core.config import settings

def test_full_end_to_end_smoke_workflow(tmp_path):
    # 1. Generate lightweight synthetic data
    demo_csv = tmp_path / "smoke_demo.csv"
    df = generate_synthetic_dataset(start_year=2023, end_year=2024, output_path=demo_csv)
    assert len(df) > 0
    assert df["beach_id"].nunique() >= 12

    # 2. Preprocess & Chronological windowing
    prep = TimeSeriesPreprocessor(sequence_length=6, horizon=3)
    df_eng = prep.engineer_features(df)
    (train_data, val_data, test_data) = prep.create_chronological_datasets(df_eng, 0.70, 0.15, horizon=3)
    X_tr, y_tr, _ = train_data
    assert len(X_tr) > 0

    # 3. Model init
    model = PyTorchLSTM(input_dim=len(prep.feature_columns), hidden_dim=16, num_layers=1, horizon=3)
    assert model is not None

    # 4. Multi-horizon forecast simulation
    test_beach_id = "beach_miami_south"
    b_records = df[df["beach_id"] == test_beach_id].to_dict("records")
    
    # 5. Composition estimation
    comp = estimate_waste_composition(
        total_waste_kg=3500.0,
        beach_id=test_beach_id,
        region="North America",
        method="historical_beach_profile",
        beach_observations=b_records
    )
    assert comp["recyclable_kg"] > 0
    assert comp["non_recyclable_kg"] > 0
    assert len(comp["materials"]) == 6

    # 6. Cost calculation
    cost = calculate_costs(
        total_waste_kg=3500.0,
        currency="USD"
    )
    assert cost["net_total_cost"] > 0
    assert cost["collection_cost"] > 0

    # 7. PDF Report Generation
    report_file = tmp_path / "smoke_report.pdf"
    pdf_out = generate_pdf_report(
        beach_info={"name": "Miami South Beach", "country": "USA", "region": "North America"},
        forecast_data={
            "horizon_months": 3,
            "model_type": "LSTM",
            "monthly_forecasts": [
                {"month_index": 1, "forecast_date": "2025-01-01", "predicted_waste_kg": 1200.0, "lower_bound_kg": 1000.0, "upper_bound_kg": 1400.0, "estimated_cost_total": 850.0},
                {"month_index": 2, "forecast_date": "2025-02-01", "predicted_waste_kg": 1300.0, "lower_bound_kg": 1100.0, "upper_bound_kg": 1500.0, "estimated_cost_total": 920.0},
                {"month_index": 3, "forecast_date": "2025-03-01", "predicted_waste_kg": 1400.0, "lower_bound_kg": 1200.0, "upper_bound_kg": 1600.0, "estimated_cost_total": 990.0},
            ]
        },
        composition_data=comp,
        cost_data=cost,
        output_filename=str(report_file)
    )
    assert Path(pdf_out).exists()
    assert Path(pdf_out).stat().st_size > 1000
