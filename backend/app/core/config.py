"""
Configuration settings for BeachWaste AI application.
Supports local development and Vercel serverless environments.
"""
import os
from pathlib import Path
from pydantic import BaseModel

import tempfile

IS_VERCEL = "VERCEL" in os.environ
TEMP_DIR = Path(tempfile.gettempdir())

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if ROOT_DIR.name == "backend":
    ROOT_DIR = ROOT_DIR.parent

DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
DB_PATH = (TEMP_DIR / "beachwaste.db") if IS_VERCEL else (ROOT_DIR / "beachwaste.db")

class Settings(BaseModel):
    PROJECT_NAME: str = "BeachWaste AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    IS_VERCEL: bool = IS_VERCEL
    
    # Directories
    RAW_DATA_DIR: Path = (TEMP_DIR / "raw") if IS_VERCEL else (DATA_DIR / "raw")
    PROCESSED_DATA_DIR: Path = (TEMP_DIR / "processed") if IS_VERCEL else (DATA_DIR / "processed")
    DEMO_DATA_DIR: Path = DATA_DIR / "demo"
    MODEL_DIR: Path = ARTIFACTS_DIR / "models"
    METRICS_DIR: Path = ARTIFACTS_DIR / "metrics"
    REPORTS_DIR: Path = (TEMP_DIR / "reports") if IS_VERCEL else (ARTIFACTS_DIR / "reports")
    
    # Model defaults
    DEFAULT_SEQUENCE_LENGTH: int = 12
    DEFAULT_EPOCHS: int = 40
    DEFAULT_BATCH_SIZE: int = 16
    DEFAULT_LEARNING_RATE: float = 0.003
    DEFAULT_HIDDEN_DIM: int = 64
    DEFAULT_DROPOUT: float = 0.15
    RANDOM_SEED: int = 42

    # Cost Defaults (USD per kg)
    DEFAULT_COLLECTION_COST_PER_KG: float = 0.45
    DEFAULT_TRANSPORT_COST_PER_KG: float = 0.20
    DEFAULT_SORTING_COST_PER_KG: float = 0.15
    DEFAULT_RECYCLING_PROCESSING_PER_KG: float = 0.35
    DEFAULT_NON_RECYCLABLE_DISPOSAL_PER_KG: float = 0.50
    DEFAULT_ORGANIC_COMPOSTING_PER_KG: float = 0.18
    DEFAULT_MATERIAL_REVENUE_PER_KG: float = 0.12  # Credit for sorted high-grade recyclables

    # Currency conversion rates relative to USD (Illustrative reference)
    CURRENCY_RATES: dict = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "AUD": 1.52,
        "CAD": 1.36,
        "JPY": 152.0,
        "INR": 83.5
    }

settings = Settings()

# Ensure writable directories exist
for directory in [
    settings.RAW_DATA_DIR,
    settings.PROCESSED_DATA_DIR,
    settings.REPORTS_DIR,
]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
