"""
CLI script to generate and seed the BeachWaste AI benchmark demonstration dataset.
"""
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.data_pipeline.synthetic_generator import generate_synthetic_dataset
from backend.app.database.database import engine, Base, SessionLocal
from backend.app.data_pipeline.ingestion import seed_demo_data
from backend.app.core.config import settings

def main():
    print("=" * 60)
    print("BeachWaste AI — Demonstration Data Generator")
    print("=" * 60)
    
    output_csv = settings.DEMO_DATA_DIR / "beach_waste_demo.csv"
    print(f"Generating synthetic observations across 12 global beaches to {output_csv}...")
    df = generate_synthetic_dataset(start_year=2021, end_year=2025, output_path=output_csv)
    print(f"Successfully generated {len(df)} records across {df['beach_id'].nunique()} beaches.")

    print("\nInitializing database schema and seeding tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = seed_demo_data(db, force_regenerate=True)
        print(f"Successfully populated database with {count} observations.")
    finally:
        db.close()

    print("\nDemo data generation complete!")

if __name__ == "__main__":
    main()
