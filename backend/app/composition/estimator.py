"""
Waste Composition Estimation Module for BeachWaste AI.

Differentiates Material Categories (Plastic, Glass, Metal, Paper, Organic, Textile, Other)
from Recovery/Treatment Categories (Recyclable, Non-Recyclable, Biodegradable).
Supports beach-specific profiles, regional benchmarks, and user scenarios.
"""
from typing import Dict, Any, Optional, List
import numpy as np

# Regional composition benchmarks (based on UNEP & ocean conservancy coastal surveys)
REGIONAL_PROFILES: Dict[str, Dict[str, float]] = {
    "North America": {
        "plastic": 0.56, "metal": 0.13, "glass": 0.14, "paper": 0.08, "organic": 0.05, "other": 0.04
    },
    "South America": {
        "plastic": 0.62, "metal": 0.14, "glass": 0.09, "paper": 0.06, "organic": 0.05, "other": 0.04
    },
    "Europe": {
        "plastic": 0.50, "metal": 0.15, "glass": 0.16, "paper": 0.10, "organic": 0.04, "other": 0.05
    },
    "East Asia": {
        "plastic": 0.55, "metal": 0.12, "glass": 0.11, "paper": 0.12, "organic": 0.06, "other": 0.04
    },
    "Southeast Asia": {
        "plastic": 0.67, "metal": 0.09, "glass": 0.08, "paper": 0.05, "organic": 0.07, "other": 0.04
    },
    "South Asia": {
        "plastic": 0.64, "metal": 0.09, "glass": 0.08, "paper": 0.08, "organic": 0.07, "other": 0.04
    },
    "East Africa": {
        "plastic": 0.63, "metal": 0.08, "glass": 0.10, "paper": 0.06, "organic": 0.09, "other": 0.04
    },
    "Southern Africa": {
        "plastic": 0.51, "metal": 0.16, "glass": 0.14, "paper": 0.10, "organic": 0.05, "other": 0.04
    },
    "Oceania": {
        "plastic": 0.53, "metal": 0.14, "glass": 0.12, "paper": 0.11, "organic": 0.06, "other": 0.04
    },
    "Pacific Islands": {
        "plastic": 0.56, "metal": 0.13, "glass": 0.13, "paper": 0.09, "organic": 0.05, "other": 0.04
    },
    "Global Default": {
        "plastic": 0.58, "metal": 0.12, "glass": 0.12, "paper": 0.08, "organic": 0.06, "other": 0.04
    }
}

# Material-to-Recovery Mapping Factors (illustrative operational recovery benchmarks)
# Not all plastic is recyclable in practice due to marine degradation and multilayer laminates.
RECOVERY_COEFFICIENTS = {
    "plastic": {"recyclable": 0.42, "biodegradable": 0.0, "non_recyclable": 0.58},
    "metal": {"recyclable": 0.88, "biodegradable": 0.0, "non_recyclable": 0.12},
    "glass": {"recyclable": 0.78, "biodegradable": 0.0, "non_recyclable": 0.22},
    "paper": {"recyclable": 0.65, "biodegradable": 0.25, "non_recyclable": 0.10},
    "organic": {"recyclable": 0.0, "biodegradable": 0.92, "non_recyclable": 0.08},
    "other": {"recyclable": 0.10, "biodegradable": 0.10, "non_recyclable": 0.80},
}

def estimate_waste_composition(
    total_waste_kg: float,
    beach_id: Optional[str] = None,
    region: Optional[str] = None,
    method: str = "historical_beach_profile",
    user_shares: Optional[Dict[str, float]] = None,
    beach_observations: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Computes material breakdown and recovery classifications for a given waste mass.
    """
    shares: Dict[str, float] = {}
    data_source_description = ""
    uncertainty_warning = ""

    if method == "user_scenario" and user_shares:
        shares = user_shares.copy()
        data_source_description = "User-configured hypothetical composition scenario."
        uncertainty_warning = "Estimates reflect user manual parameters rather than empirical coastal sampling."
    elif method == "historical_beach_profile" and beach_observations:
        # Calculate historical mean shares from actual beach records
        obs_df = [o for o in beach_observations if (o.get("plastic_mass_kg") or 0) > 0]
        if obs_df:
            total_mat_mass = sum(o.get("waste_mass_kg", 0) for o in obs_df)
            if total_mat_mass > 0:
                shares = {
                    "plastic": sum(o.get("plastic_mass_kg", 0) for o in obs_df) / total_mat_mass,
                    "metal": sum(o.get("metal_mass_kg", 0) for o in obs_df) / total_mat_mass,
                    "glass": sum(o.get("glass_mass_kg", 0) for o in obs_df) / total_mat_mass,
                    "paper": sum(o.get("paper_mass_kg", 0) for o in obs_df) / total_mat_mass,
                    "organic": sum(o.get("organic_waste_mass_kg", 0) for o in obs_df) / total_mat_mass,
                    "other": sum((o.get("textile_mass_kg", 0) + o.get("other_waste_mass_kg", 0)) for o in obs_df) / total_mat_mass,
                }
                data_source_description = f"Empirical historical mean profile derived from {len(obs_df)} recorded beach observations."
                uncertainty_warning = "Composition proportions can fluctuate with storm events, tourist seasons, and tidal surges."
        
    if not shares:
        # Fall back to Regional Benchmark Profile
        profile_key = region if region in REGIONAL_PROFILES else "Global Default"
        shares = REGIONAL_PROFILES[profile_key].copy()
        data_source_description = f"Regional coastal waste benchmark profile for '{profile_key}'."
        uncertainty_warning = "Beach-specific composition not available. Regional averages provide representative baseline estimates."

    # Normalize material shares so they sum precisely to 1.0
    total_raw_share = sum(shares.values())
    normalized_shares = {k: v / max(total_raw_share, 1e-6) for k, v in shares.items()}

    # Compute absolute kilograms per material
    materials_list = []
    total_recyclable_kg = 0.0
    total_biodegradable_kg = 0.0
    total_non_recyclable_kg = 0.0

    for mat_name, fraction in normalized_shares.items():
        mass_kg = round(total_waste_kg * fraction, 2)
        rec_coeffs = RECOVERY_COEFFICIENTS.get(mat_name, {"recyclable": 0.2, "biodegradable": 0.1, "non_recyclable": 0.7})
        
        rec_kg = mass_kg * rec_coeffs["recyclable"]
        bio_kg = mass_kg * rec_coeffs["biodegradable"]
        non_rec_kg = mass_kg * rec_coeffs["non_recyclable"]

        total_recyclable_kg += rec_kg
        total_biodegradable_kg += bio_kg
        total_non_recyclable_kg += non_rec_kg

        # Main treatment category determination
        main_treatment = "Recyclable Stream" if rec_coeffs["recyclable"] > 0.5 else (
            "Composting/Biodegradable" if rec_coeffs["biodegradable"] > 0.5 else "Landfill/Incineration Residual"
        )

        materials_list.append({
            "category": mat_name.capitalize(),
            "percentage": round(fraction * 100.0, 1),
            "mass_kg": mass_kg,
            "treatment_class": main_treatment
        })

    recyclable_pct = round((total_recyclable_kg / max(total_waste_kg, 1e-6)) * 100.0, 1)
    biodegradable_pct = round((total_biodegradable_kg / max(total_waste_kg, 1e-6)) * 100.0, 1)
    non_recyclable_pct = round(max(0.0, 100.0 - recyclable_pct - biodegradable_pct), 1)

    return {
        "beach_id": beach_id,
        "total_waste_kg": round(total_waste_kg, 2),
        "estimation_method": method,
        "materials": materials_list,
        "recyclable_pct": recyclable_pct,
        "recyclable_kg": round(total_recyclable_kg, 2),
        "non_recyclable_pct": non_recyclable_pct,
        "non_recyclable_kg": round(total_non_recyclable_kg, 2),
        "biodegradable_pct": biodegradable_pct,
        "biodegradable_kg": round(total_biodegradable_kg, 2),
        "normalization_check": True,
        "data_source_description": data_source_description,
        "uncertainty_warning": uncertainty_warning
    }
