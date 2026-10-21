"""
Vercel Serverless Function Entrypoint for BeachWaste AI API.
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Set VERCEL flag in environment
os.environ["VERCEL"] = "1"

from backend.app.main import app
from backend.app.database.database import engine, Base, SessionLocal
from backend.app.data_pipeline.ingestion import seed_demo_data

# Cold start initialization: ensure database and demo seeds exist in /tmp
try:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_demo_data(db, force_regenerate=False)
    db.close()
except Exception as e:
    print(f"[Vercel Cold Start] DB init note: {e}")
