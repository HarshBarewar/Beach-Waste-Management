"""
Waste Composition API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.database import get_db
from backend.app.database.models import Beach, Observation
from backend.app.schemas.forecast import CompositionEstimateRequest, CompositionEstimateResponse
from backend.app.composition.estimator import estimate_waste_composition

router = APIRouter(prefix="/composition", tags=["Composition"])

@router.post("/estimate", response_model=CompositionEstimateResponse)
def estimate_composition(req: CompositionEstimateRequest, db: Session = Depends(get_db)):
    beach_observations = None
    region = None

    if req.beach_id:
        beach = db.query(Beach).filter(Beach.id == req.beach_id).first()
        if beach:
            region = beach.region
            obs = db.query(Observation).filter(Observation.beach_id == req.beach_id).all()
            beach_observations = [
                {
                    "waste_mass_kg": o.waste_mass_kg,
                    "plastic_mass_kg": o.plastic_mass_kg,
                    "metal_mass_kg": o.metal_mass_kg,
                    "glass_mass_kg": o.glass_mass_kg,
                    "paper_mass_kg": o.paper_mass_kg,
                    "organic_waste_mass_kg": o.organic_waste_mass_kg,
                    "textile_mass_kg": o.textile_mass_kg,
                    "other_waste_mass_kg": o.other_waste_mass_kg,
                }
                for o in obs
            ]

    result = estimate_waste_composition(
        total_waste_kg=req.total_waste_kg,
        beach_id=req.beach_id,
        region=region,
        method=req.method,
        user_shares=req.user_shares,
        beach_observations=beach_observations
    )

    return CompositionEstimateResponse(**result)
