"""
Waste Treatment and Recycling Cost Calculator for BeachWaste AI.

Implements transparent, configurable financial models for beach waste cleanup,
transportation, sorting, material recycling, composting, and landfill disposal.
Supports multiple global currencies and uncertainty propagation.
"""
from typing import Dict, Any, Optional, List
from backend.app.core.config import settings

# Material unit treatment costs in USD per kg
DEFAULT_MATERIAL_UNIT_COSTS = {
    "Plastic": 0.38,
    "Metal": 0.22,
    "Glass": 0.25,
    "Paper": 0.20,
    "Organic": 0.18,
    "Other": 0.48
}

def calculate_costs(
    total_waste_kg: float,
    currency: str = "USD",
    collection_cost_per_kg: Optional[float] = None,
    transport_cost_per_kg: Optional[float] = None,
    sorting_cost_per_kg: Optional[float] = None,
    recycling_processing_per_kg: Optional[float] = None,
    non_recyclable_disposal_per_kg: Optional[float] = None,
    organic_composting_per_kg: Optional[float] = None,
    material_revenue_per_kg: Optional[float] = None,
    fixed_monthly_cost: float = 0.0,
    composition_shares: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes detailed treatment and recycling costs with currency conversion.
    """
    rate = settings.CURRENCY_RATES.get(currency.upper(), 1.0)

    # Base USD unit costs (fall back to settings defaults if not supplied)
    c_coll = collection_cost_per_kg if collection_cost_per_kg is not None else settings.DEFAULT_COLLECTION_COST_PER_KG
    c_trans = transport_cost_per_kg if transport_cost_per_kg is not None else settings.DEFAULT_TRANSPORT_COST_PER_KG
    c_sort = sorting_cost_per_kg if sorting_cost_per_kg is not None else settings.DEFAULT_SORTING_COST_PER_KG
    c_rec = recycling_processing_per_kg if recycling_processing_per_kg is not None else settings.DEFAULT_RECYCLING_PROCESSING_PER_KG
    c_disp = non_recyclable_disposal_per_kg if non_recyclable_disposal_per_kg is not None else settings.DEFAULT_NON_RECYCLABLE_DISPOSAL_PER_KG
    c_comp = organic_composting_per_kg if organic_composting_per_kg is not None else settings.DEFAULT_ORGANIC_COMPOSTING_PER_KG
    c_rev = material_revenue_per_kg if material_revenue_per_kg is not None else settings.DEFAULT_MATERIAL_REVENUE_PER_KG

    # Approximate stream fractions if not provided
    rec_frac = 0.38
    disp_frac = 0.46
    comp_frac = 0.16

    # Operational cost items in USD
    collection_cost_usd = total_waste_kg * c_coll
    transport_cost_usd = total_waste_kg * c_trans
    sorting_cost_usd = total_waste_kg * c_sort
    recycling_processing_usd = (total_waste_kg * rec_frac) * c_rec
    non_recyclable_disposal_usd = (total_waste_kg * disp_frac) * c_disp
    organic_composting_usd = (total_waste_kg * comp_frac) * c_comp
    fixed_usd = fixed_monthly_cost
    material_credits_usd = (total_waste_kg * rec_frac) * c_rev

    gross_usd = (
        collection_cost_usd
        + transport_cost_usd
        + sorting_cost_usd
        + recycling_processing_usd
        + non_recyclable_disposal_usd
        + organic_composting_usd
        + fixed_usd
    )
    net_usd = max(0.0, gross_usd - material_credits_usd)

    # Material-specific breakdown table
    shares = composition_shares or {
        "Plastic": 0.58, "Metal": 0.12, "Glass": 0.12, "Paper": 0.08, "Organic": 0.06, "Other": 0.04
    }

    materials_breakdown = []
    for mat_cat, fraction in shares.items():
        mat_mass = total_waste_kg * fraction
        base_unit_cost = DEFAULT_MATERIAL_UNIT_COSTS.get(mat_cat, 0.30)
        # Combine sorting and treatment for material specific cost
        unit_cost_currency = round(base_unit_cost * rate, 2)
        tot_cost_currency = round(mat_mass * base_unit_cost * rate, 2)
        materials_breakdown.append({
            "category": mat_cat,
            "mass_kg": round(mat_mass, 2),
            "unit_treatment_cost": unit_cost_currency,
            "total_treatment_cost": tot_cost_currency
        })

    # Convert operational totals to requested currency
    return {
        "currency": currency.upper(),
        "currency_exchange_rate_to_usd": rate,
        "total_waste_kg": round(total_waste_kg, 2),
        "collection_cost": round(collection_cost_usd * rate, 2),
        "transport_cost": round(transport_cost_usd * rate, 2),
        "sorting_cost": round(sorting_cost_usd * rate, 2),
        "recycling_processing_cost": round(recycling_processing_usd * rate, 2),
        "non_recyclable_disposal_cost": round(non_recyclable_disposal_usd * rate, 2),
        "organic_composting_cost": round(organic_composting_usd * rate, 2),
        "fixed_operating_cost": round(fixed_usd * rate, 2),
        "gross_total_cost": round(gross_usd * rate, 2),
        "material_credits_or_revenue": round(material_credits_usd * rate, 2),
        "net_total_cost": round(net_usd * rate, 2),
        "effective_cost_per_kg": round((net_usd * rate) / max(total_waste_kg, 1e-6), 3),
        "materials_cost_breakdown": materials_breakdown,
        "is_illustrative_estimate": True,
        "assumptions": [
            f"Financial calculations rendered in {currency.upper()} using conversion rate of {rate} per USD.",
            "Material revenue credit applies only to cleanly separated high-grade recyclables.",
            "Unit rates reflect standard municipal and coastal NGO waste management benchmarks and do not represent contractual quotes."
        ]
    }
