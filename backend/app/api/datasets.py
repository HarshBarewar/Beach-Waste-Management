"""
Dataset Management API endpoints (List, Upload CSV, Download Sample).
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
from pathlib import Path
import pandas as pd

from backend.app.database.database import get_db
from backend.app.database.models import DatasetRecord
from backend.app.data_pipeline.ingestion import ingest_csv_upload
from backend.app.core.config import settings

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.get("")
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(DatasetRecord).order_by(DatasetRecord.uploaded_at.desc()).all()
    return {"datasets": datasets}

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are accepted.")

    name = dataset_name or file.filename.replace(".csv", "")
    temp_path = settings.RAW_DATA_DIR / f"upload_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        res = ingest_csv_upload(temp_path, name, db)
        if not res["success"]:
            raise HTTPException(status_code=422, detail={"errors": res["errors"]})
        return res
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/sample.csv")
def download_sample_csv():
    """
    Returns a downloadable sample CSV template matching BeachWaste AI schema.
    """
    sample_data = [
        {
            "observation_id": "beach_demo_202401",
            "beach_id": "beach_demo_cove",
            "beach_name": "Demo Cove Beach",
            "country": "Sample Country",
            "latitude": 28.5383,
            "longitude": -81.3792,
            "observation_date": "2024-01-01",
            "waste_mass_kg": 1450.5,
            "waste_mass_unit": "kg",
            "observation_duration_hours": 5.0,
            "surveyed_area_m2": 12000.0,
            "plastic_mass_kg": 820.0,
            "metal_mass_kg": 180.5,
            "glass_mass_kg": 190.0,
            "paper_mass_kg": 110.0,
            "organic_waste_mass_kg": 80.0,
            "textile_mass_kg": 40.0,
            "other_waste_mass_kg": 30.0,
            "recyclable_mass_kg": 540.0,
            "non_recyclable_mass_kg": 760.0,
            "biodegradable_mass_kg": 150.5,
            "visitor_count": 14000,
            "tourism_season": "peak",
            "rainfall_mm": 45.2,
            "temperature_c": 24.5,
            "wind_speed": 14.2,
            "storm_indicator": 0,
            "cleanup_frequency": "weekly",
            "collection_method": "manual_volunteer",
            "source_name": "Sample-Coastal-Survey",
            "data_quality_flag": "ESTIMATED"
        },
        {
            "observation_id": "beach_demo_202402",
            "beach_id": "beach_demo_cove",
            "beach_name": "Demo Cove Beach",
            "country": "Sample Country",
            "latitude": 28.5383,
            "longitude": -81.3792,
            "observation_date": "2024-02-01",
            "waste_mass_kg": 1520.0,
            "waste_mass_unit": "kg",
            "observation_duration_hours": 5.0,
            "surveyed_area_m2": 12000.0,
            "plastic_mass_kg": 860.0,
            "metal_mass_kg": 190.0,
            "glass_mass_kg": 200.0,
            "paper_mass_kg": 115.0,
            "organic_waste_mass_kg": 85.0,
            "textile_mass_kg": 40.0,
            "other_waste_mass_kg": 30.0,
            "recyclable_mass_kg": 570.0,
            "non_recyclable_mass_kg": 790.0,
            "biodegradable_mass_kg": 160.0,
            "visitor_count": 15500,
            "tourism_season": "peak",
            "rainfall_mm": 38.0,
            "temperature_c": 25.0,
            "wind_speed": 12.0,
            "storm_indicator": 0,
            "cleanup_frequency": "weekly",
            "collection_method": "manual_volunteer",
            "source_name": "Sample-Coastal-Survey",
            "data_quality_flag": "ESTIMATED"
        }
    ]
    df = pd.DataFrame(sample_data)
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=beachwaste_sample_template.csv"}
    )
