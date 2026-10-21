# Dataset Guide & Schema Reference — BeachWaste AI

## 1. Data Provenance & Realism Notice

The demonstration benchmark bundled with this release consists of **720 monthly observations** across **12 global coastal beaches** spanning 5 continuous years (2021 to 2025).

All demonstration records carry the explicit flag:
`data_quality_flag: "SYNTHETIC_DEMO"` or `"SYNTHETIC_DEMO_ANOMALY"`

The dataset incorporates real-world physical and climatic parameters:
- **Sinusoidal Seasonality**: Adjusted for northern hemisphere summer (July peak) vs southern hemisphere summer (January peak).
- **Meteorological Storm Runoff**: Probabilistic storm events generating elevated rainfall, wind speed, and marine debris influxes.
- **Tourism Surges**: Seasonal visitor waves calibrated against regional municipal tourism statistics.
- **Injected Physical Anomalies**:
  - *Fujisawa Shonan (Japan, Sep 2023)*: Category 4 Typhoon surge producing 2.85x normal beach debris.
  - *Kuta Beach Bali (Indonesia, Jan 2024)*: Severe West Monsoon oceanic plastic wave producing 2.65x debris.

---

## 2. Standard Schema Specification

Every ingested observation complies with the standardized schema:

| Column Name | Data Type | Constraint / Unit | Description |
| :--- | :--- | :--- | :--- |
| `observation_id` | String | Unique Primary Key | Format: `{beach_id}_{YYYYMM}` |
| `beach_id` | String | Foreign Key | Beach identifier (e.g., `beach_bondi`) |
| `beach_name` | String | Non-empty | Official name of the beach |
| `country` | String | Non-empty | Sovereign country of location |
| `latitude` | Float | [-90.0, 90.0] | Decimal latitude coordinate |
| `longitude` | Float | [-180.0, 180.0] | Decimal longitude coordinate |
| `observation_date` | String | YYYY-MM-DD | Date of observation/survey |
| `waste_mass_kg` | Float | $\ge 0.0$, kg | Total mass of waste collected |
| `surveyed_area_m2` | Float | $> 0.0$, $\text{m}^2$ | Beach survey area for density calculation |
| `observation_duration_hours` | Float | $> 0.0$, hours | Survey/cleanup event duration |
| `plastic_mass_kg` | Float | $\ge 0.0$, kg | Mass of plastic debris |
| `metal_mass_kg` | Float | $\ge 0.0$, kg | Mass of aluminium and steel cans |
| `glass_mass_kg` | Float | $\ge 0.0$, kg | Mass of glass bottles and cullet |
| `paper_mass_kg` | Float | $\ge 0.0$, kg | Mass of paper, cartons, cardboard |
| `organic_waste_mass_kg` | Float | $\ge 0.0$, kg | Mass of driftwood, food waste, seaweed |
| `textile_mass_kg` | Float | $\ge 0.0$, kg | Mass of discarded clothing, fishing nets |
| `other_waste_mass_kg` | Float | $\ge 0.0$, kg | Residual composites and miscellaneous items |
| `recyclable_mass_kg` | Float | $\ge 0.0$, kg | Reclaimable container fractions |
| `non_recyclable_mass_kg` | Float | $\ge 0.0$, kg | Residual destined for landfill or incineration |
| `biodegradable_mass_kg` | Float | $\ge 0.0$, kg | Organic fractions suitable for composting |
| `visitor_count` | Integer | $\ge 0$ | Estimated monthly beach visitors |
| `tourism_season` | String | low, shoulder, peak | Qualitative tourism classification |
| `rainfall_mm` | Float | $\ge 0.0$, mm | Monthly precipitation |
| `temperature_c` | Float | °Celsius | Mean monthly coastal ambient temperature |
| `wind_speed` | Float | km/h | Mean surface onshore wind velocity |
| `storm_indicator` | Integer | 0 or 1 | Severe coastal storm occurrence flag |
| `cleanup_frequency` | String | daily, weekly, monthly | Cadence of beach cleanup sweeps |
| `collection_method` | String | manual, mechanical | Municipal sweeps, volunteer, or raking |
| `source_name` | String | Non-empty | Origin organization / survey title |
| `data_quality_flag` | String | Quality classification | `VERIFIED`, `ESTIMATED`, `SYNTHETIC_DEMO` |

---

## 3. Uploading User Datasets

Users may upload proprietary coastal survey CSV files via the **Dataset Management** interface or API endpoint:
`POST /api/datasets/upload`

Incoming files are automatically checked for:
- Required column presence.
- Coordinate validity boundaries.
- Non-negative mass values.
- Consistent date formats.
- High missing-value alerts.
