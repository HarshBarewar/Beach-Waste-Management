"""
Beach Explorer and Comparison API endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import numpy as np

from backend.app.database.database import get_db
from backend.app.database.models import Beach, Observation
from backend.app.schemas.beach import BeachResponse, BeachDetailResponse, ObservationSchema
from backend.app.data_pipeline.synthetic_generator import GLOBAL_BEACHES

router = APIRouter(prefix="/beaches", tags=["Beaches"])

@router.get("", response_model=List[BeachResponse])
def list_beaches(
    search: Optional[str] = Query(None, description="Search by beach or country name"),
    country: Optional[str] = Query(None, description="Filter by country"),
    region: Optional[str] = Query(None, description="Filter by region"),
    favorites_only: bool = Query(False, description="Filter favorites"),
    db: Session = Depends(get_db)
):
    query = db.query(Beach)
    if search:
        s_pattern = f"%{search}%"
        query = query.filter((Beach.name.ilike(s_pattern)) | (Beach.country.ilike(s_pattern)))
    if country:
        query = query.filter(Beach.country.ilike(f"%{country}%"))
    if region:
        query = query.filter(Beach.region == region)
    if favorites_only:
        query = query.filter(Beach.is_favorite == True)

    beaches = query.order_by(Beach.name).all()
    return beaches

@router.get("/compare")
def compare_beaches(
    beach_ids: str = Query(..., description="Comma-separated beach IDs (up to 5)"),
    db: Session = Depends(get_db)
):
    ids = [i.strip() for i in beach_ids.split(",") if i.strip()][:5]
    if not ids:
        raise HTTPException(status_code=400, detail="Please provide at least one beach_id")

    results = []
    for b_id in ids:
        beach = db.query(Beach).filter(Beach.id == b_id).first()
        if not beach:
            continue
        
        observations = db.query(Observation).filter(Observation.beach_id == b_id).order_by(Observation.observation_date).all()
        if not observations:
            continue

        masses = [o.waste_mass_kg for o in observations]
        areas = [o.surveyed_area_m2 for o in observations if o.surveyed_area_m2]
        avg_area = float(np.mean(areas)) if areas else 10000.0

        avg_mass = float(np.mean(masses))
        max_mass = float(np.max(masses))
        latest_mass = masses[-1]

        # Normalized intensity
        avg_intensity_kg_m2 = avg_mass / avg_area if avg_area > 0 else 0.0

        # Plastic and recyclable shares
        plastic_masses = [o.plastic_mass_kg for o in observations if o.plastic_mass_kg]
        rec_masses = [o.recyclable_mass_kg for o in observations if o.recyclable_mass_kg]

        avg_plastic_pct = (sum(plastic_masses) / sum(masses) * 100.0) if sum(masses) > 0 and plastic_masses else 55.0
        avg_recyclable_pct = (sum(rec_masses) / sum(masses) * 100.0) if sum(masses) > 0 and rec_masses else 38.0

        results.append({
            "beach_id": beach.id,
            "beach_name": beach.name,
            "country": beach.country,
            "region": beach.region,
            "coastal_type": beach.coastal_type,
            "total_observations": len(observations),
            "data_start_date": beach.data_start_date,
            "data_end_date": beach.data_end_date,
            "latest_waste_kg": round(latest_mass, 1),
            "avg_monthly_waste_kg": round(avg_mass, 1),
            "peak_recorded_waste_kg": round(max_mass, 1),
            "surveyed_area_m2": avg_area,
            "avg_waste_intensity_kg_m2": round(avg_intensity_kg_m2, 4),
            "avg_plastic_pct": round(avg_plastic_pct, 1),
            "avg_recyclable_pct": round(avg_recyclable_pct, 1),
            "data_quality_flag": beach.data_source_type,
            "sufficient_data": beach.sufficient_data_for_forecasting,
            "recent_12m_trend": masses[-12:] if len(masses) >= 12 else masses
        })

    return {
        "compared_beaches": results,
        "comparability_warning": (
            "Caution: Direct comparison between beaches with different surveyed area sizes, cleanup frequencies, "
            "or sampling methods must consider normalized intensity (kg/m²) rather than raw mass."
        )
    }

@router.get("/{beach_id}", response_model=BeachDetailResponse)
def get_beach(beach_id: str, db: Session = Depends(get_db)):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if not beach:
        raise HTTPException(status_code=404, detail=f"Beach '{beach_id}' not found")

    observations = db.query(Observation).filter(Observation.beach_id == beach_id).order_by(Observation.observation_date).all()
    
    obs_schemas = []
    masses = []
    for o in observations:
        kg_m2 = (o.waste_mass_kg / o.surveyed_area_m2) if (o.surveyed_area_m2 and o.surveyed_area_m2 > 0) else None
        kg_hr = (o.waste_mass_kg / o.observation_duration_hours) if (o.observation_duration_hours and o.observation_duration_hours > 0) else None
        masses.append(o.waste_mass_kg)
        obs_schemas.append(ObservationSchema(
            observation_id=o.observation_id,
            beach_id=o.beach_id,
            observation_date=o.observation_date,
            year=o.year,
            month=o.month,
            waste_mass_kg=o.waste_mass_kg,
            waste_mass_unit=o.waste_mass_unit,
            observation_duration_hours=o.observation_duration_hours,
            surveyed_area_m2=o.surveyed_area_m2,
            plastic_mass_kg=o.plastic_mass_kg,
            metal_mass_kg=o.metal_mass_kg,
            glass_mass_kg=o.glass_mass_kg,
            paper_mass_kg=o.paper_mass_kg,
            organic_waste_mass_kg=o.organic_waste_mass_kg,
            textile_mass_kg=o.textile_mass_kg,
            other_waste_mass_kg=o.other_waste_mass_kg,
            recyclable_mass_kg=o.recyclable_mass_kg,
            non_recyclable_mass_kg=o.non_recyclable_mass_kg,
            biodegradable_mass_kg=o.biodegradable_mass_kg,
            visitor_count=o.visitor_count,
            tourism_season=o.tourism_season,
            rainfall_mm=o.rainfall_mm,
            temperature_c=o.temperature_c,
            wind_speed=o.wind_speed,
            storm_indicator=o.storm_indicator,
            cleanup_frequency=o.cleanup_frequency,
            collection_method=o.collection_method,
            source_name=o.source_name,
            data_quality_flag=o.data_quality_flag,
            is_synthetic=o.is_synthetic,
            kg_per_m2=round(kg_m2, 4) if kg_m2 else None,
            kg_per_hour=round(kg_hr, 2) if kg_hr else None
        ))

    return BeachDetailResponse(
        id=beach.id,
        name=beach.name,
        country=beach.country,
        region=beach.region,
        latitude=beach.latitude,
        longitude=beach.longitude,
        coastal_type=beach.coastal_type,
        is_favorite=beach.is_favorite,
        sufficient_data_for_forecasting=beach.sufficient_data_for_forecasting,
        total_observations=len(obs_schemas),
        data_start_date=beach.data_start_date,
        data_end_date=beach.data_end_date,
        data_source_type=beach.data_source_type,
        notes=beach.notes,
        observations=obs_schemas,
        latest_monthly_waste_kg=masses[-1] if masses else None,
        avg_monthly_waste_kg=round(float(np.mean(masses)), 2) if masses else None,
        highest_recorded_waste_kg=round(float(np.max(masses)), 2) if masses else None,
        total_historical_waste_kg=round(float(np.sum(masses)), 2) if masses else None,
        data_coverage_months=len(masses)
    )

@router.post("/{beach_id}/favorite")
def toggle_favorite(beach_id: str, db: Session = Depends(get_db)):
    beach = db.query(Beach).filter(Beach.id == beach_id).first()
    if not beach:
        raise HTTPException(status_code=404, detail="Beach not found")
    beach.is_favorite = not beach.is_favorite
    db.commit()
    return {"id": beach.id, "is_favorite": beach.is_favorite}
