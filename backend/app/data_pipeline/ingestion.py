"""
Data Ingestion Service for BeachWaste AI.

Handles parsing, validating, normalizing, and inserting beach waste datasets
into the SQLite database.
"""
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from backend.app.database.models import Beach, Observation, DatasetRecord
from backend.app.data_pipeline.schema import validate_dataframe
from backend.app.data_pipeline.synthetic_generator import GLOBAL_BEACHES, generate_synthetic_dataset
from backend.app.core.config import settings

def seed_demo_data(db: Session, force_regenerate: bool = False) -> int:
    """
    Seeds database with initial demonstration beaches and multi-year observations.
    """
    demo_file = settings.DEMO_DATA_DIR / "beach_waste_demo.csv"
    if force_regenerate or not demo_file.exists():
        generate_synthetic_dataset(output_path=demo_file)

    df = pd.read_csv(demo_file)
    val_report = validate_dataframe(df)
    if not val_report["valid"]:
        raise ValueError(f"Demo data invalid: {val_report['errors']}")

    # Insert Beach records
    beach_meta_map = {b["beach_id"]: b for b in GLOBAL_BEACHES}
    for b_id, group in df.groupby("beach_id"):
        meta = beach_meta_map.get(b_id, {})
        existing = db.query(Beach).filter(Beach.id == b_id).first()
        min_date = group["observation_date"].min()
        max_date = group["observation_date"].max()
        count_obs = len(group)

        if not existing:
            beach = Beach(
                id=b_id,
                name=group["beach_name"].iloc[0],
                country=group["country"].iloc[0],
                region=meta.get("region", "Global"),
                latitude=float(group["latitude"].iloc[0]),
                longitude=float(group["longitude"].iloc[0]),
                coastal_type=meta.get("coastal_type", "Sandy Shore"),
                is_favorite=False,
                sufficient_data_for_forecasting=(count_obs >= 24),
                total_observations=count_obs,
                data_start_date=min_date,
                data_end_date=max_date,
                data_source_type="SYNTHETIC_DEMO",
                notes=meta.get("notes", "Demonstration beach record.")
            )
            db.add(beach)
        else:
            existing.total_observations = count_obs
            existing.data_start_date = min_date
            existing.data_end_date = max_date

    db.commit()

    # Clear existing demo observations if re-seeding
    if force_regenerate:
        db.query(Observation).filter(Observation.data_quality_flag.like("%SYNTHETIC%")).delete()
        db.commit()

    # Bulk insert observations
    existing_obs_ids = set(o[0] for o in db.query(Observation.observation_id).all())
    new_obs = []
    for _, row in df.iterrows():
        if row["observation_id"] in existing_obs_ids:
            continue
        new_obs.append(Observation(
            observation_id=str(row["observation_id"]),
            beach_id=str(row["beach_id"]),
            observation_date=str(row["observation_date"]),
            year=int(row["year"]),
            month=int(row["month"]),
            waste_mass_kg=float(row["waste_mass_kg"]),
            waste_mass_unit="kg",
            observation_duration_hours=float(row.get("observation_duration_hours", 4.0)),
            surveyed_area_m2=float(row.get("surveyed_area_m2", 10000.0)),
            plastic_mass_kg=float(row.get("plastic_mass_kg", 0.0)),
            metal_mass_kg=float(row.get("metal_mass_kg", 0.0)),
            glass_mass_kg=float(row.get("glass_mass_kg", 0.0)),
            paper_mass_kg=float(row.get("paper_mass_kg", 0.0)),
            organic_waste_mass_kg=float(row.get("organic_waste_mass_kg", 0.0)),
            textile_mass_kg=float(row.get("textile_mass_kg", 0.0)),
            other_waste_mass_kg=float(row.get("other_waste_mass_kg", 0.0)),
            recyclable_mass_kg=float(row.get("recyclable_mass_kg", 0.0)),
            non_recyclable_mass_kg=float(row.get("non_recyclable_mass_kg", 0.0)),
            biodegradable_mass_kg=float(row.get("biodegradable_mass_kg", 0.0)),
            visitor_count=int(row.get("visitor_count", 0)),
            tourism_season=str(row.get("tourism_season", "shoulder")),
            rainfall_mm=float(row.get("rainfall_mm", 0.0)),
            temperature_c=float(row.get("temperature_c", 20.0)),
            wind_speed=float(row.get("wind_speed", 10.0)),
            storm_indicator=int(row.get("storm_indicator", 0)),
            cleanup_frequency=str(row.get("cleanup_frequency", "monthly")),
            collection_method=str(row.get("collection_method", "manual_volunteer")),
            source_name=str(row.get("source_name", "BeachWaste-AI-Synthetic-Demo-v1")),
            data_quality_flag=str(row.get("data_quality_flag", "SYNTHETIC_DEMO")),
            is_synthetic=True
        ))

    if new_obs:
        db.bulk_save_objects(new_obs)
        db.commit()

    # Register Dataset Record
    dataset_rec = db.query(DatasetRecord).filter(DatasetRecord.id == "demo_dataset").first()
    if not dataset_rec:
        dataset_rec = DatasetRecord(
            id="demo_dataset",
            name="Global Demonstration Benchmark Dataset (5-Year)",
            filename="beach_waste_demo.csv",
            uploaded_at=datetime.now(timezone.utc).isoformat(),
            total_rows=len(df),
            total_beaches=df["beach_id"].nunique(),
            date_range_start=str(df["observation_date"].min()),
            date_range_end=str(df["observation_date"].max()),
            validation_status="VALIDATED",
            is_synthetic=True,
            description="Multi-year calibrated benchmark spanning 12 beaches across 6 continents with seasonal and meteorological covariates."
        )
        db.add(dataset_rec)
        db.commit()

    return len(new_obs)

def ingest_csv_upload(file_path: Path, dataset_name: str, db: Session) -> dict:
    """
    Ingests an uploaded CSV file, validates columns, inserts observations and updates beaches.
    """
    df = pd.read_csv(file_path)
    val = validate_dataframe(df)
    if not val["valid"]:
        return {"success": False, "errors": val["errors"]}

    dataset_id = f"ds_{int(datetime.now(timezone.utc).timestamp())}"
    
    # Insert new beaches or update existing
    for b_id, group in df.groupby("beach_id"):
        existing = db.query(Beach).filter(Beach.id == b_id).first()
        min_date = str(group["observation_date"].min())
        max_date = str(group["observation_date"].max())
        count_obs = len(group)

        if not existing:
            beach = Beach(
                id=str(b_id),
                name=str(group["beach_name"].iloc[0]),
                country=str(group["country"].iloc[0]),
                region="Uploaded Dataset",
                latitude=float(group["latitude"].iloc[0]),
                longitude=float(group["longitude"].iloc[0]),
                coastal_type=str(group.get("coastal_type", pd.Series(["Sandy Shore"])).iloc[0]),
                sufficient_data_for_forecasting=(count_obs >= 18),
                total_observations=count_obs,
                data_start_date=min_date,
                data_end_date=max_date,
                data_source_type="USER_UPLOAD",
                notes=f"Ingested from user upload: {dataset_name}"
            )
            db.add(beach)
        else:
            existing.total_observations += count_obs

    db.commit()

    # Bulk insert observations
    obs_objects = []
    for _, row in df.iterrows():
        obs_id = str(row["observation_id"])
        # Avoid duplicate
        if db.query(Observation).filter(Observation.observation_id == obs_id).first():
            continue
        obs_objects.append(Observation(
            observation_id=obs_id,
            beach_id=str(row["beach_id"]),
            observation_date=str(row["observation_date"]),
            year=int(pd.to_datetime(row["observation_date"]).year),
            month=int(pd.to_datetime(row["observation_date"]).month),
            waste_mass_kg=float(row["waste_mass_kg"]),
            waste_mass_unit="kg",
            observation_duration_hours=float(row["observation_duration_hours"]) if "observation_duration_hours" in row and pd.notnull(row["observation_duration_hours"]) else None,
            surveyed_area_m2=float(row["surveyed_area_m2"]) if "surveyed_area_m2" in row and pd.notnull(row["surveyed_area_m2"]) else None,
            plastic_mass_kg=float(row["plastic_mass_kg"]) if "plastic_mass_kg" in row and pd.notnull(row["plastic_mass_kg"]) else None,
            metal_mass_kg=float(row["metal_mass_kg"]) if "metal_mass_kg" in row and pd.notnull(row["metal_mass_kg"]) else None,
            glass_mass_kg=float(row["glass_mass_kg"]) if "glass_mass_kg" in row and pd.notnull(row["glass_mass_kg"]) else None,
            paper_mass_kg=float(row["paper_mass_kg"]) if "paper_mass_kg" in row and pd.notnull(row["paper_mass_kg"]) else None,
            organic_waste_mass_kg=float(row["organic_waste_mass_kg"]) if "organic_waste_mass_kg" in row and pd.notnull(row["organic_waste_mass_kg"]) else None,
            textile_mass_kg=float(row["textile_mass_kg"]) if "textile_mass_kg" in row and pd.notnull(row["textile_mass_kg"]) else None,
            other_waste_mass_kg=float(row["other_waste_mass_kg"]) if "other_waste_mass_kg" in row and pd.notnull(row["other_waste_mass_kg"]) else None,
            recyclable_mass_kg=float(row["recyclable_mass_kg"]) if "recyclable_mass_kg" in row and pd.notnull(row["recyclable_mass_kg"]) else None,
            non_recyclable_mass_kg=float(row["non_recyclable_mass_kg"]) if "non_recyclable_mass_kg" in row and pd.notnull(row["non_recyclable_mass_kg"]) else None,
            biodegradable_mass_kg=float(row["biodegradable_mass_kg"]) if "biodegradable_mass_kg" in row and pd.notnull(row["biodegradable_mass_kg"]) else None,
            visitor_count=int(row["visitor_count"]) if "visitor_count" in row and pd.notnull(row["visitor_count"]) else None,
            tourism_season=str(row.get("tourism_season", "unknown")),
            rainfall_mm=float(row["rainfall_mm"]) if "rainfall_mm" in row and pd.notnull(row["rainfall_mm"]) else None,
            temperature_c=float(row["temperature_c"]) if "temperature_c" in row and pd.notnull(row["temperature_c"]) else None,
            wind_speed=float(row["wind_speed"]) if "wind_speed" in row and pd.notnull(row["wind_speed"]) else None,
            storm_indicator=int(row.get("storm_indicator", 0)),
            cleanup_frequency=str(row.get("cleanup_frequency", "monthly")),
            collection_method=str(row.get("collection_method", "manual")),
            source_name=dataset_name,
            data_quality_flag="USER_UPLOAD",
            is_synthetic=False
        ))

    if obs_objects:
        db.bulk_save_objects(obs_objects)
        db.commit()

    dataset_rec = DatasetRecord(
        id=dataset_id,
        name=dataset_name,
        filename=file_path.name,
        uploaded_at=datetime.now(timezone.utc).isoformat(),
        total_rows=len(df),
        total_beaches=df["beach_id"].nunique(),
        date_range_start=str(df["observation_date"].min()),
        date_range_end=str(df["observation_date"].max()),
        validation_status="VALIDATED",
        is_synthetic=False,
        description=f"User-provided upload containing {len(df)} records across {df['beach_id'].nunique()} beaches."
    )
    db.add(dataset_rec)
    db.commit()

    return {
        "success": True,
        "dataset_id": dataset_id,
        "records_inserted": len(obs_objects),
        "total_rows": len(df),
        "beaches_count": df["beach_id"].nunique(),
        "warnings": val["warnings"]
    }
