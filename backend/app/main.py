"""
Main FastAPI Application Entrypoint for BeachWaste AI.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from backend.app.core.config import settings
from backend.app.database.database import engine, Base, SessionLocal
from backend.app.data_pipeline.ingestion import seed_demo_data
from backend.app.api.beaches import router as beaches_router
from backend.app.api.predict import router as predict_router
from backend.app.api.composition import router as composition_router
from backend.app.api.cost import router as cost_router
from backend.app.api.models import router as models_router
from backend.app.api.datasets import router as datasets_router
from backend.app.api.reports import router as reports_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB tables and seed demo data if empty
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db, force_regenerate=False)
    except Exception as e:
        print(f"Demo data seeding notice: {e}")
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A Deep Learning-Based Global Beach Waste Prediction, Classification, and Recycling Cost Estimation System",
    lifespan=lifespan
)

# CORS configuration for local React Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(beaches_router, prefix=settings.API_V1_STR)
app.include_router(predict_router, prefix=settings.API_V1_STR)
app.include_router(composition_router, prefix=settings.API_V1_STR)
app.include_router(cost_router, prefix=settings.API_V1_STR)
app.include_router(models_router, prefix=settings.API_V1_STR)
app.include_router(datasets_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)

@app.get("/api/health", tags=["Health"])
def health_check():
    if TORCH_AVAILABLE:
        cuda_avail = torch.cuda.is_available()
        device = torch.cuda.get_device_name(0) if cuda_avail else "CPU"
        torch_ver = torch.__version__
        engine_mode = "PyTorch + NumPy Hybrid"
    else:
        cuda_avail = False
        device = "Serverless CPU (Pure NumPy Inference)"
        torch_ver = "N/A (Serverless Deployment)"
        engine_mode = "High-Performance Pure NumPy Matrix Engine"

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "compute_device": device,
        "cuda_available": cuda_avail,
        "pytorch_version": torch_ver,
        "inference_engine": engine_mode
    }

@app.get("/", tags=["Root"])
def root_redirect():
    return {
        "project": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "health_check": "/api/health"
    }
