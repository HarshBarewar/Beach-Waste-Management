"""
Waste Treatment and Recycling Cost API endpoints.
"""
from fastapi import APIRouter
from typing import Dict, Any

from backend.app.schemas.forecast import CostCalculationRequest, CostCalculationResponse
from backend.app.cost_estimation.calculator import calculate_costs
from backend.app.core.config import settings

router = APIRouter(prefix="/cost", tags=["Cost Estimation"])

@router.post("/estimate", response_model=CostCalculationResponse)
def estimate_cost(req: CostCalculationRequest):
    result = calculate_costs(
        total_waste_kg=req.total_waste_kg,
        currency=req.currency,
        collection_cost_per_kg=req.collection_cost_per_kg,
        transport_cost_per_kg=req.transport_cost_per_kg,
        sorting_cost_per_kg=req.sorting_cost_per_kg,
        recycling_processing_per_kg=req.recycling_processing_per_kg,
        non_recyclable_disposal_per_kg=req.non_recyclable_disposal_per_kg,
        organic_composting_per_kg=req.organic_composting_per_kg,
        material_revenue_per_kg=req.material_revenue_per_kg,
        fixed_monthly_cost=req.fixed_monthly_cost or 0.0,
        composition_shares=req.material_breakdown
    )
    return CostCalculationResponse(**result)

@router.get("/currencies")
def get_supported_currencies() -> Dict[str, Any]:
    return {
        "currencies": [
            {"code": "USD", "name": "US Dollar", "symbol": "$", "rate": 1.0},
            {"code": "EUR", "name": "Euro", "symbol": "€", "rate": 0.92},
            {"code": "GBP", "name": "British Pound", "symbol": "£", "rate": 0.79},
            {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "rate": 1.52},
            {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "rate": 1.36},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "rate": 152.0},
            {"code": "INR", "name": "Indian Rupee", "symbol": "₹", "rate": 83.5},
        ]
    }
