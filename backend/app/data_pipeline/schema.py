"""
Data schema definitions and validation standards for BeachWaste AI.
"""
from typing import List, Dict, Any
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "observation_id",
    "beach_id",
    "beach_name",
    "country",
    "latitude",
    "longitude",
    "observation_date",
    "waste_mass_kg",
]

NUMERIC_COLUMNS = [
    "latitude",
    "longitude",
    "waste_mass_kg",
    "observation_duration_hours",
    "surveyed_area_m2",
    "plastic_mass_kg",
    "metal_mass_kg",
    "glass_mass_kg",
    "paper_mass_kg",
    "organic_waste_mass_kg",
    "textile_mass_kg",
    "other_waste_mass_kg",
    "recyclable_mass_kg",
    "non_recyclable_mass_kg",
    "biodegradable_mass_kg",
    "visitor_count",
    "rainfall_mm",
    "temperature_c",
    "wind_speed",
    "storm_indicator",
]

MATERIAL_CATEGORIES = [
    "plastic_mass_kg",
    "metal_mass_kg",
    "glass_mass_kg",
    "paper_mass_kg",
    "organic_waste_mass_kg",
    "textile_mass_kg",
    "other_waste_mass_kg",
]

RECOVERY_CATEGORIES = [
    "recyclable_mass_kg",
    "non_recyclable_mass_kg",
    "biodegradable_mass_kg",
]

def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validates an ingested beach waste DataFrame against schema rules.
    Returns status dict with errors, warnings, and summary stats.
    """
    errors = []
    warnings = []

    # Check required columns
    missing_required = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_required:
        errors.append(f"Missing mandatory columns: {', '.join(missing_required)}")

    if errors:
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "row_count": len(df),
            "columns": list(df.columns)
        }

    # Date parsing check
    try:
        df["parsed_date"] = pd.to_datetime(df["observation_date"])
    except Exception as e:
        errors.append(f"Date parsing failed: {str(e)}")

    # Check negative values in waste_mass_kg
    if (df["waste_mass_kg"] < 0).any():
        errors.append("Column 'waste_mass_kg' contains negative values.")

    # Check lat/lon bounds
    if not (df["latitude"].between(-90, 90)).all():
        errors.append("Latitude values must be within [-90, 90].")
    if not (df["longitude"].between(-180, 180)).all():
        errors.append("Longitude values must be within [-180, 180].")

    # Missing values analysis
    missing_counts = df.isnull().sum().to_dict()
    high_missing = [k for k, v in missing_counts.items() if v > (0.4 * len(df))]
    if high_missing:
        warnings.append(f"Columns with >40% missing data: {', '.join(high_missing)}")

    # Material sum consistency check
    available_mat = [c for c in MATERIAL_CATEGORIES if c in df.columns and df[c].notnull().any()]
    if len(available_mat) >= 3:
        mat_sum = df[available_mat].sum(axis=1)
        discrepancy = (np.abs(mat_sum - df["waste_mass_kg"]) > (0.15 * df["waste_mass_kg"] + 5.0)).sum()
        if discrepancy > 0:
            warnings.append(f"{discrepancy} records have material sum differing significantly from total waste_mass_kg (treated as non-exclusive or incomplete sampling).")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "row_count": len(df),
        "total_beaches": df["beach_id"].nunique() if "beach_id" in df.columns else 0,
        "columns": list(df.columns)
    }
