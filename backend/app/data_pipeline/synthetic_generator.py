"""
Synthetic Demonstration Dataset Generator for BeachWaste AI.

Generates realistic, physically-grounded historical monthly beach waste time series
for multiple global beaches across diverse geographical and climatic zones.
All generated records are explicitly labeled as SYNTHETIC_DEMO.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from backend.app.core.config import settings

GLOBAL_BEACHES = [
    {
        "beach_id": "beach_miami_south",
        "beach_name": "South Beach, Miami",
        "country": "United States",
        "region": "North America",
        "latitude": 25.7826,
        "longitude": -80.1341,
        "coastal_type": "Subtropical Barrier Island",
        "hemisphere": "north",
        "base_waste_kg": 2400.0,
        "peak_months": [3, 4, 6, 7],  # Spring break & Summer
        "hurricane_months": [8, 9, 10],
        "surveyed_area_m2": 15000.0,
        "base_duration_hours": 6.0,
        "avg_temp_base": 25.0,
        "plastic_share": 0.58,
        "metal_share": 0.12,
        "glass_share": 0.14,
        "paper_share": 0.08,
        "organic_share": 0.05,
        "other_share": 0.03,
        "notes": "Popular urban tourist beach with major spring break and summer visitor influxes."
    },
    {
        "beach_id": "beach_copacabana",
        "beach_name": "Copacabana Beach, Rio de Janeiro",
        "country": "Brazil",
        "region": "South America",
        "latitude": -22.9711,
        "longitude": -43.1822,
        "coastal_type": "Tropical Atlantic Urban Shore",
        "hemisphere": "south",
        "base_waste_kg": 3800.0,
        "peak_months": [12, 1, 2],  # Southern summer & Carnaval
        "hurricane_months": [],
        "surveyed_area_m2": 24000.0,
        "base_duration_hours": 8.0,
        "avg_temp_base": 27.0,
        "plastic_share": 0.62,
        "metal_share": 0.15,  # beverage cans
        "glass_share": 0.09,
        "paper_share": 0.06,
        "organic_share": 0.05,
        "other_share": 0.03,
        "notes": "High-density urban beach renowned for New Year's Eve and Carnaval visitor waves."
    },
    {
        "beach_id": "beach_bondi",
        "beach_name": "Bondi Beach, Sydney",
        "country": "Australia",
        "region": "Oceania",
        "latitude": -33.8915,
        "longitude": 151.2767,
        "coastal_type": "Ocean Surf Beach",
        "hemisphere": "south",
        "base_waste_kg": 1850.0,
        "peak_months": [12, 1, 2],
        "hurricane_months": [],
        "surveyed_area_m2": 12000.0,
        "base_duration_hours": 5.0,
        "avg_temp_base": 22.0,
        "plastic_share": 0.52,
        "metal_share": 0.14,
        "glass_share": 0.12,
        "paper_share": 0.11,
        "organic_share": 0.07,
        "other_share": 0.04,
        "notes": "Iconic Australian surf beach with structured council cleaning and volunteer cleanups."
    },
    {
        "beach_id": "beach_kuta_bali",
        "beach_name": "Kuta Beach, Bali",
        "country": "Indonesia",
        "region": "Southeast Asia",
        "latitude": -8.7185,
        "longitude": 115.1686,
        "coastal_type": "Tropical Coral Coast",
        "hemisphere": "south",
        "base_waste_kg": 4200.0,
        "peak_months": [7, 8, 12],
        "hurricane_months": [11, 12, 1, 2],  # Monsoon season plastic surge
        "surveyed_area_m2": 18000.0,
        "base_duration_hours": 7.0,
        "avg_temp_base": 28.0,
        "plastic_share": 0.68,
        "metal_share": 0.08,
        "glass_share": 0.07,
        "paper_share": 0.05,
        "organic_share": 0.08,
        "other_share": 0.04,
        "notes": "Faces heavy seasonal west monsoon marine litter accumulation from December through February."
    },
    {
        "beach_id": "beach_nice_promenade",
        "beach_name": "Promenade des Anglais, Nice",
        "country": "France",
        "region": "Europe",
        "latitude": 43.6960,
        "longitude": 7.2520,
        "coastal_type": "Mediterranean Pebble Shore",
        "hemisphere": "north",
        "base_waste_kg": 1400.0,
        "peak_months": [6, 7, 8],
        "hurricane_months": [],
        "surveyed_area_m2": 10000.0,
        "base_duration_hours": 4.5,
        "avg_temp_base": 18.0,
        "plastic_share": 0.49,
        "metal_share": 0.16,
        "glass_share": 0.18,
        "paper_share": 0.09,
        "organic_share": 0.04,
        "other_share": 0.04,
        "notes": "Pebble Mediterranean shoreline with high summer tourist traffic and daily municipal maintenance."
    },
    {
        "beach_id": "beach_fujisawa_shonan",
        "beach_name": "Shonan Katase Kaigan, Fujisawa",
        "country": "Japan",
        "region": "East Asia",
        "latitude": 35.3090,
        "longitude": 139.4878,
        "coastal_type": "Temperate Volcanic Sand",
        "hemisphere": "north",
        "base_waste_kg": 1600.0,
        "peak_months": [7, 8],
        "hurricane_months": [8, 9],  # Typhoon season
        "surveyed_area_m2": 11000.0,
        "base_duration_hours": 5.0,
        "avg_temp_base": 16.0,
        "plastic_share": 0.54,
        "metal_share": 0.13,
        "glass_share": 0.11,
        "paper_share": 0.12,
        "organic_share": 0.06,
        "other_share": 0.04,
        "notes": "High Tokyo-weekend visitor beach near Enoshima Island; vulnerable to late summer typhoons."
    },
    {
        "beach_id": "beach_coxs_bazar",
        "beach_name": "Cox's Bazar Sea Beach",
        "country": "Bangladesh",
        "region": "South Asia",
        "latitude": 21.4272,
        "longitude": 91.9702,
        "coastal_type": "Longest Natural Sandy Beach",
        "hemisphere": "north",
        "base_waste_kg": 3600.0,
        "peak_months": [11, 12, 1, 2],  # Winter domestic tourism peak
        "hurricane_months": [5, 6, 9, 10],  # Bay of Bengal cyclone season
        "surveyed_area_m2": 25000.0,
        "base_duration_hours": 8.0,
        "avg_temp_base": 26.0,
        "plastic_share": 0.64,
        "metal_share": 0.09,
        "glass_share": 0.08,
        "paper_share": 0.08,
        "organic_share": 0.07,
        "other_share": 0.04,
        "notes": "120-km unbroken natural beach experiencing dense domestic tourism during winter dry months."
    },
    {
        "beach_id": "beach_scheveningen",
        "beach_name": "Scheveningen Beach, The Hague",
        "country": "Netherlands",
        "region": "Western Europe",
        "latitude": 52.1130,
        "longitude": 4.2810,
        "coastal_type": "North Sea Dune & Pier Shore",
        "hemisphere": "north",
        "base_waste_kg": 1500.0,
        "peak_months": [6, 7, 8],
        "hurricane_months": [10, 11, 1],  # North Sea winter gales
        "surveyed_area_m2": 14000.0,
        "base_duration_hours": 5.0,
        "avg_temp_base": 11.0,
        "plastic_share": 0.51,
        "metal_share": 0.15,
        "glass_share": 0.13,
        "paper_share": 0.11,
        "organic_share": 0.05,
        "other_share": 0.05,
        "notes": "Popular North Sea resort beach featuring extensive mechanical sweeping in summer."
    },
    {
        "beach_id": "beach_zanzibar_nungwi",
        "beach_name": "Nungwi Beach, Zanzibar",
        "country": "Tanzania",
        "region": "East Africa",
        "latitude": -5.7247,
        "longitude": 39.2974,
        "coastal_type": "Coral Sand Lagoon",
        "hemisphere": "south",
        "base_waste_kg": 1900.0,
        "peak_months": [7, 8, 12, 1],
        "hurricane_months": [4, 5],  # Heavy rains 'Masika'
        "surveyed_area_m2": 13000.0,
        "base_duration_hours": 6.0,
        "avg_temp_base": 28.0,
        "plastic_share": 0.63,
        "metal_share": 0.08,
        "glass_share": 0.10,
        "paper_share": 0.06,
        "organic_share": 0.09,
        "other_share": 0.04,
        "notes": "Pristine white coral sands supporting luxury resort tourism and traditional dhow fishing."
    },
    {
        "beach_id": "beach_phuket_patong",
        "beach_name": "Patong Beach, Phuket",
        "country": "Thailand",
        "region": "Southeast Asia",
        "latitude": 7.8967,
        "longitude": 98.2965,
        "coastal_type": "Andaman Sea Bay",
        "hemisphere": "north",
        "base_waste_kg": 3400.0,
        "peak_months": [11, 12, 1, 2],
        "hurricane_months": [6, 7, 8, 9],  # Southwest monsoon
        "surveyed_area_m2": 16000.0,
        "base_duration_hours": 7.0,
        "avg_temp_base": 28.5,
        "plastic_share": 0.66,
        "metal_share": 0.10,
        "glass_share": 0.09,
        "paper_share": 0.06,
        "organic_share": 0.05,
        "other_share": 0.04,
        "notes": "High-intensity international tourist hotspot with distinct dry peak season and rainy monsoon season."
    },
    {
        "beach_id": "beach_waikiki",
        "beach_name": "Waikiki Beach, Honolulu",
        "country": "United States",
        "region": "Pacific Islands",
        "latitude": 21.2766,
        "longitude": -157.8272,
        "coastal_type": "Pacific Tropical Urban Beach",
        "hemisphere": "north",
        "base_waste_kg": 2900.0,
        "peak_months": [6, 7, 8, 12],
        "hurricane_months": [],
        "surveyed_area_m2": 17000.0,
        "base_duration_hours": 6.5,
        "avg_temp_base": 26.5,
        "plastic_share": 0.55,
        "metal_share": 0.14,
        "glass_share": 0.13,
        "paper_share": 0.09,
        "organic_share": 0.05,
        "other_share": 0.04,
        "notes": "World-famous urban tourist beach with year-round heavy visitor traffic."
    },
    {
        "beach_id": "beach_clifton_cape_town",
        "beach_name": "Clifton 4th Beach, Cape Town",
        "country": "South Africa",
        "region": "Southern Africa",
        "latitude": -33.9392,
        "longitude": 18.3758,
        "coastal_type": "Granite Boulder Cove",
        "hemisphere": "south",
        "base_waste_kg": 1350.0,
        "peak_months": [12, 1, 2],
        "hurricane_months": [],
        "surveyed_area_m2": 8000.0,
        "base_duration_hours": 4.0,
        "avg_temp_base": 21.0,
        "plastic_share": 0.50,
        "metal_share": 0.16,
        "glass_share": 0.15,
        "paper_share": 0.10,
        "organic_share": 0.05,
        "other_share": 0.04,
        "notes": "Blue Flag sheltered cove popular with locals and international tourists during southern summer."
    }
]

def generate_synthetic_dataset(
    start_year: int = 2021,
    end_year: int = 2025,
    random_seed: int = 42,
    output_path: Path = None
) -> pd.DataFrame:
    """
    Generates monthly synthetic observations for all configured beaches.
    Uses reproducible random generation with sinusoidal seasonality, tourist factors,
    weather covariates, storm effects, and intentional realistic anomalies.
    """
    np.random.seed(random_seed)
    records = []

    # Monthly dates: 2021-01 to 2025-12 (60 months per beach)
    dates = pd.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-01", freq="MS")

    for beach in GLOBAL_BEACHES:
        b_id = beach["beach_id"]
        b_name = beach["beach_name"]
        country = beach["country"]
        lat = beach["latitude"]
        lon = beach["longitude"]
        base_waste = beach["base_waste_kg"]
        area = beach["surveyed_area_m2"]
        base_dur = beach["base_duration_hours"]

        for idx, dt in enumerate(dates):
            month = dt.month
            year = dt.year
            date_str = dt.strftime("%Y-%m-%d")
            obs_id = f"{b_id}_{dt.strftime('%Y%m')}"

            # 1. Seasonality effect
            if beach["hemisphere"] == "north":
                # Peak in July (m=7), trough in January (m=1)
                temp = beach["avg_temp_base"] + 8.0 * np.sin((month - 4) * np.pi / 6.0) + np.random.normal(0, 1.0)
            else:
                # Peak in Jan (m=1), trough in July (m=7)
                temp = beach["avg_temp_base"] + 8.0 * np.sin((month + 2) * np.pi / 6.0) + np.random.normal(0, 1.0)

            # Tourism visitor factor
            is_peak = month in beach["peak_months"]
            visitor_base = 25000 if is_peak else 8000
            tourism_season = "peak" if is_peak else ("shoulder" if month in [4, 5, 9, 10] else "low")
            visitor_count = int(visitor_base * (1.0 + 0.05 * (year - start_year)) + np.random.normal(0, 1500))
            visitor_count = max(visitor_count, 1200)

            # Weather covariates
            is_rainy_season = month in beach["hurricane_months"]
            rainfall = np.random.gamma(shape=3.0, scale=35.0) if is_rainy_season else np.random.gamma(shape=1.5, scale=18.0)
            wind_speed = np.random.normal(16.0, 4.0) if not is_rainy_season else np.random.normal(26.0, 7.0)
            wind_speed = max(wind_speed, 3.0)

            # Storm occurrence (probabilistic based on storm months)
            storm_prob = 0.35 if is_rainy_season else 0.04
            is_storm = 1 if np.random.random() < storm_prob else 0

            # Trend: mild upward trend over years due to rising global plastic & tourism (+2.5%/yr)
            trend_factor = 1.0 + 0.025 * (year - start_year)

            # Seasonal waste curve
            seasonal_multiplier = 1.35 if is_peak else (0.80 if tourism_season == "low" else 1.05)
            storm_multiplier = 1.30 if is_storm else 1.0

            # Base waste formula with realistic physical factors
            waste_kg = base_waste * trend_factor * seasonal_multiplier * storm_multiplier
            # Add stochastic variance
            waste_kg += np.random.normal(0, 0.08 * waste_kg)
            waste_kg = max(waste_kg, 200.0)

            # INTENTIONAL ANOMALY 1: Fujisawa Shonan (Sep 2023 - Typhoon Surge: 2.8x waste)
            is_anomaly = False
            quality_flag = "SYNTHETIC_DEMO"
            if b_id == "beach_fujisawa_shonan" and year == 2023 and month == 9:
                waste_kg *= 2.85
                is_storm = 1
                rainfall = 340.0
                wind_speed = 52.0
                is_anomaly = True
                quality_flag = "SYNTHETIC_DEMO_ANOMALY"

            # INTENTIONAL ANOMALY 2: Kuta Beach Bali (Jan 2024 - Massive West Monsoon Marine Debris: 2.6x waste)
            if b_id == "beach_kuta_bali" and year == 2024 and month == 1:
                waste_kg *= 2.65
                is_storm = 1
                rainfall = 410.0
                wind_speed = 44.0
                is_anomaly = True
                quality_flag = "SYNTHETIC_DEMO_ANOMALY"

            waste_kg = round(float(waste_kg), 2)

            # Material shares with slight month-to-month jitter
            p_share = max(0.40, min(0.75, beach["plastic_share"] + np.random.normal(0, 0.02)))
            m_share = max(0.05, min(0.20, beach["metal_share"] + np.random.normal(0, 0.01)))
            g_share = max(0.04, min(0.20, beach["glass_share"] + np.random.normal(0, 0.01)))
            pap_share = max(0.03, min(0.15, beach["paper_share"] + np.random.normal(0, 0.01)))
            org_share = max(0.02, min(0.12, beach["organic_share"] + np.random.normal(0, 0.01)))
            oth_share = max(0.01, 1.0 - (p_share + m_share + g_share + pap_share + org_share))
            
            # Re-normalize material sum to 1.0
            total_share = p_share + m_share + g_share + pap_share + org_share + oth_share
            p_share /= total_share
            m_share /= total_share
            g_share /= total_share
            pap_share /= total_share
            org_share /= total_share
            oth_share /= total_share

            plastic_kg = round(waste_kg * p_share, 2)
            metal_kg = round(waste_kg * m_share, 2)
            glass_kg = round(waste_kg * g_share, 2)
            paper_kg = round(waste_kg * pap_share, 2)
            org_kg = round(waste_kg * org_share, 2)
            other_kg = round(waste_kg - (plastic_kg + metal_kg + glass_kg + paper_kg + org_kg), 2)
            textile_kg = round(other_kg * 0.4, 2)
            other_residual_kg = round(other_kg - textile_kg, 2)

            # Recovery/Treatment breakdown:
            # Recyclable: ~40% of plastic (PET/HDPE bottles), 85% metal cans, 75% glass, 60% paper
            recyclable_kg = round(0.40 * plastic_kg + 0.85 * metal_kg + 0.75 * glass_kg + 0.60 * paper_kg, 2)
            # Biodegradable: organics and plain paper fibers
            biodegradable_kg = round(0.90 * org_kg + 0.25 * paper_kg, 2)
            # Non-recyclable: residual soiled plastics, composites, textiles, broken non-container glass
            non_recyclable_kg = round(max(0.0, waste_kg - recyclable_kg - biodegradable_kg), 2)

            duration = round(float(base_dur + np.random.normal(0, 0.4)), 1)
            duration = max(duration, 2.0)

            records.append({
                "observation_id": obs_id,
                "beach_id": b_id,
                "beach_name": b_name,
                "country": country,
                "latitude": lat,
                "longitude": lon,
                "observation_date": date_str,
                "year": year,
                "month": month,
                "waste_mass_kg": waste_kg,
                "waste_mass_unit": "kg",
                "observation_duration_hours": duration,
                "surveyed_area_m2": area,
                "plastic_mass_kg": plastic_kg,
                "metal_mass_kg": metal_kg,
                "glass_mass_kg": glass_kg,
                "paper_mass_kg": paper_kg,
                "organic_waste_mass_kg": org_kg,
                "textile_mass_kg": textile_kg,
                "other_waste_mass_kg": other_residual_kg,
                "recyclable_mass_kg": recyclable_kg,
                "non_recyclable_mass_kg": non_recyclable_kg,
                "biodegradable_mass_kg": biodegradable_kg,
                "visitor_count": visitor_count,
                "tourism_season": tourism_season,
                "rainfall_mm": round(float(rainfall), 1),
                "temperature_c": round(float(temp), 1),
                "wind_speed": round(float(wind_speed), 1),
                "storm_indicator": is_storm,
                "cleanup_frequency": "weekly" if is_peak else "monthly",
                "collection_method": "manual_and_mechanical" if is_peak else "manual_volunteer",
                "source_name": "BeachWaste-AI-Synthetic-Demo-v1",
                "data_quality_flag": quality_flag,
                "is_synthetic": True,
            })

    df = pd.DataFrame(records)

    target_file = output_path or (settings.DEMO_DATA_DIR / "beach_waste_demo.csv")
    df.to_csv(target_file, index=False)
    print(f"Generated {len(df)} synthetic observations across {len(GLOBAL_BEACHES)} beaches to {target_file}")
    return df

if __name__ == "__main__":
    generate_synthetic_dataset()
