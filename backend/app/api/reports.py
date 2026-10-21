"""
Assessment Report Generation and Data Export API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

from backend.app.database.database import get_db
from backend.app.database.models import Beach, Observation
from backend.app.reporting.pdf_generator import generate_pdf_report
from backend.app.composition.estimator import estimate_waste_composition
from backend.app.cost_estimation.calculator import calculate_costs
from backend.app.core.config import settings
from backend.app.api.predict import generate_forecast
from backend.app.schemas.forecast import ForecastRequest

router = APIRouter(prefix="/reports", tags=["Reports"])

class PDFReportRequest(BaseModel):
    beach_id: str
    model_type: str = "lstm"
    horizon_months: int = 6
    currency: str = "USD"

@router.post("/generate-pdf")
def create_pdf_report(req: PDFReportRequest, db: Session = Depends(get_db)):
    beach = db.query(Beach).filter(Beach.id == req.beach_id).first()
    if not beach:
        raise HTTPException(status_code=404, detail="Beach not found")

    beach_info = {
        "id": beach.id,
        "name": beach.name,
        "country": beach.country,
        "region": beach.region,
        "latitude": beach.latitude,
        "longitude": beach.longitude,
        "coastal_type": beach.coastal_type,
        "total_observations": beach.total_observations,
        "data_source_type": beach.data_source_type
    }

    # Run forecast
    forecast_req = ForecastRequest(
        beach_id=beach.id,
        model_type=req.model_type,
        horizon_months=req.horizon_months,
        currency=req.currency
    )
    forecast_resp = generate_forecast(forecast_req, db)
    forecast_dict = forecast_resp.dict()

    # Get overall composition for the total predicted mass
    comp_dict = estimate_waste_composition(
        total_waste_kg=forecast_resp.cumulative_predicted_waste_kg,
        beach_id=beach.id,
        region=beach.region,
        method="historical_beach_profile"
    )

    # Get cost calculations
    cost_dict = calculate_costs(
        total_waste_kg=forecast_resp.cumulative_predicted_waste_kg,
        currency=req.currency
    )

    filename = f"BeachWaste_{beach.id}_{req.horizon_months}M_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    file_path = generate_pdf_report(
        beach_info=beach_info,
        forecast_data=forecast_dict,
        composition_data=comp_dict,
        cost_data=cost_dict,
        output_filename=filename
    )

    return {
        "success": True,
        "filename": filename,
        "download_url": f"/api/reports/download/{filename}",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@router.get("/download/{filename}")
def download_pdf_file(filename: str):
    file_path = settings.REPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(
        str(file_path),
        media_type="application/pdf",
        filename=filename
    )

@router.get("/export-csv/{beach_id}")
def export_beach_csv(
    beach_id: str,
    include_forecast: bool = Query(True),
    db: Session = Depends(get_db)
):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if not beach:
        raise HTTPException(status_code=404, detail="Beach not found")

    observations = db.query(Observation).filter(Observation.beach_id == beach_id).order_by(Observation.observation_date).all()
    rows = []
    for o in observations:
        rows.append({
            "record_type": "HISTORICAL_OBSERVATION",
            "beach_id": o.beach_id,
            "beach_name": beach.name,
            "country": beach.country,
            "date": o.observation_date,
            "waste_mass_kg": o.waste_mass_kg,
            "plastic_mass_kg": o.plastic_mass_kg,
            "metal_mass_kg": o.metal_mass_kg,
            "glass_mass_kg": o.glass_mass_kg,
            "paper_mass_kg": o.paper_mass_kg,
            "organic_waste_mass_kg": o.organic_waste_mass_kg,
            "recyclable_mass_kg": o.recyclable_mass_kg,
            "non_recyclable_mass_kg": o.non_recyclable_mass_kg,
            "biodegradable_mass_kg": o.biodegradable_mass_kg,
            "visitor_count": o.visitor_count,
            "rainfall_mm": o.rainfall_mm,
            "temperature_c": o.temperature_c,
            "wind_speed": o.wind_speed,
            "data_quality_flag": o.data_quality_flag
        })

    if include_forecast:
        try:
            forecast_req = ForecastRequest(beach_id=beach.id, model_type="lstm", horizon_months=6)
            forecast_resp = generate_forecast(forecast_req, db)
            for pt in forecast_resp.monthly_forecasts:
                rows.append({
                    "record_type": "MODEL_FORECAST",
                    "beach_id": beach.id,
                    "beach_name": beach.name,
                    "country": beach.country,
                    "date": pt.forecast_date,
                    "waste_mass_kg": pt.predicted_waste_kg,
                    "plastic_mass_kg": pt.predicted_plastic_kg,
                    "metal_mass_kg": pt.predicted_metal_kg,
                    "glass_mass_kg": pt.predicted_glass_kg,
                    "paper_mass_kg": pt.predicted_paper_kg,
                    "organic_waste_mass_kg": pt.predicted_organic_kg,
                    "recyclable_mass_kg": pt.predicted_recyclable_kg,
                    "non_recyclable_mass_kg": pt.predicted_non_recyclable_kg,
                    "biodegradable_mass_kg": pt.predicted_biodegradable_kg,
                    "visitor_count": None,
                    "rainfall_mm": None,
                    "temperature_c": None,
                    "wind_speed": None,
                    "data_quality_flag": "MODEL_PREDICTION"
                })
        except Exception:
            pass

    df = pd.DataFrame(rows)
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=beachwaste_{beach_id}_data.csv"}
    )
