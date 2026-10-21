"""
Model Training, Status, Evaluation Metrics, and Anomaly Detection API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import numpy as np
import pandas as pd
from pathlib import Path

from backend.app.database.database import get_db
from backend.app.database.models import ModelTrainingJob, Observation
from backend.app.schemas.forecast import TrainingStartRequest, TrainingStatusResponse
from backend.app.data_pipeline.preprocessor import TimeSeriesPreprocessor
from backend.app.core.config import settings
from backend.app.forecasting.numpy_inference import detect_autoencoder_anomalies_numpy

try:
    import torch
    from backend.app.training.trainer import launch_training_job_async
    from backend.app.forecasting.autoencoder import SequenceAutoencoder
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    launch_training_job_async = None
    SequenceAutoencoder = None

router = APIRouter(prefix="/models", tags=["Models"])

@router.post("/train")
def start_model_training(req: TrainingStartRequest):
    if not TORCH_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="Model training requires the PyTorch runtime. On serverless deployments, models are pre-trained with bundled weights for fast inference. Run locally with PyTorch to train new models."
        )

    valid_types = ["lstm", "encoder_decoder", "autoencoder"]
    if req.model_type.lower() not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model_type '{req.model_type}'. Choose from {valid_types}."
        )

    job_id = launch_training_job_async(
        model_type=req.model_type.lower(),
        dataset_id=req.dataset_id,
        epochs=req.epochs,
        batch_size=req.batch_size,
        learning_rate=req.learning_rate,
        sequence_length=req.sequence_length,
        hidden_dim=req.hidden_dim,
        dropout=req.dropout
    )

    return {
        "job_id": job_id,
        "model_type": req.model_type.lower(),
        "status": "pending",
        "message": f"Training job initiated for {req.model_type.upper()} on background thread."
    }

@router.get("/status/{job_id}", response_model=TrainingStatusResponse)
def get_training_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ModelTrainingJob).filter(ModelTrainingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    train_loss = json.loads(job.train_loss_history) if job.train_loss_history else []
    val_loss = json.loads(job.val_loss_history) if job.val_loss_history else []
    metrics = json.loads(job.metrics) if job.metrics else None

    hp = json.loads(job.hyperparams) if job.hyperparams else {}
    total_epochs = hp.get("epochs", 40)
    current_epoch = len(train_loss)

    return TrainingStatusResponse(
        job_id=job.id,
        model_type=job.model_type,
        status=job.status,
        created_at=job.created_at,
        completed_at=job.completed_at,
        current_epoch=current_epoch,
        total_epochs=total_epochs,
        train_loss_history=train_loss,
        val_loss_history=val_loss,
        metrics=metrics,
        error_message=job.error_message
    )

@router.get("")
def list_models(db: Session = Depends(get_db)):
    """
    Returns available models, checkpoint files, and evaluation readiness.
    """
    model_types = ["lstm", "encoder_decoder", "autoencoder"]
    models_info = []

    for m_type in model_types:
        pt_path = settings.MODEL_DIR / f"{m_type}_best.pt"
        npz_path = settings.MODEL_DIR / f"{m_type}_weights.npz"
        metrics_path = settings.METRICS_DIR / f"{m_type}_metrics.json"

        is_trained = (TORCH_AVAILABLE and pt_path.exists()) or npz_path.exists()
        metrics = None
        if metrics_path.exists():
            try:
                with open(metrics_path, "r") as f:
                    metrics = json.load(f)
            except Exception:
                pass

        # Most recent training job
        last_job = db.query(ModelTrainingJob).filter(ModelTrainingJob.model_type == m_type).order_by(ModelTrainingJob.created_at.desc()).first()

        models_info.append({
            "model_type": m_type,
            "name": (
                "Standard LSTM Forecaster" if m_type == "lstm" else (
                    "LSTM Encoder-Decoder" if m_type == "encoder_decoder" else "Sequence Autoencoder Anomaly Detector"
                )
            ),
            "is_trained": is_trained,
            "artifact_exists": is_trained,
            "last_trained_at": last_job.completed_at if (last_job and last_job.status == "completed") else None,
            "metrics": metrics,
            "description": (
                "Deep recurrent network with dropout regularization for multi-step direct beach waste forecasting."
                if m_type == "lstm" else (
                    "Seq2Seq encoder-decoder architecture mapping historical series to future predictions."
                    if m_type == "encoder_decoder" else (
                        "Deep autoencoder learning recurring seasonal manifolds and detecting storm/litter anomalies."
                    )
                )
            )
        })

    return {"models": models_info}

@router.get("/{model_id}/metrics")
def get_model_metrics(model_id: str):
    m_type = model_id.lower()
    metrics_path = settings.METRICS_DIR / f"{m_type}_metrics.json"
    if not metrics_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation metrics for '{m_type}' not found. Please train the model first."
        )

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    return {
        "model_id": m_type,
        "metrics": metrics,
        "evaluation_strategy": "Chronological 70% Train, 15% Validation, 15% Test Split (Zero future data leakage)"
    }

@router.get("/autoencoder/anomalies")
def detect_autoencoder_anomalies(db: Session = Depends(get_db)):
    """
    Applies the trained SequenceAutoencoder across all beach observations
    to detect anomalous waste observations with reconstruction error breakdown.
    """
    pt_path = settings.MODEL_DIR / "autoencoder_best.pt"
    npz_path = settings.MODEL_DIR / "autoencoder_weights.npz"
    prep_path = settings.MODEL_DIR / "autoencoder_preprocessor.pkl"

    has_pt = TORCH_AVAILABLE and pt_path.exists()
    has_npz = npz_path.exists()

    if not (has_pt or has_npz) or not prep_path.exists():
        raise HTTPException(status_code=404, detail="Autoencoder model not trained yet. Train it on the Model Training page.")

    preprocessor = TimeSeriesPreprocessor(sequence_length=12, horizon=6)
    preprocessor.load_state(str(prep_path))

    obs_query = db.query(Observation).all()
    df = pd.DataFrame([
        {
            "beach_id": o.beach_id,
            "beach_name": o.beach.name if o.beach else o.beach_id,
            "country": o.beach.country if o.beach else "Global",
            "observation_date": o.observation_date,
            "waste_mass_kg": o.waste_mass_kg,
            "visitor_count": o.visitor_count or 0,
            "temperature_c": o.temperature_c or 20.0,
            "rainfall_mm": o.rainfall_mm or 0.0,
            "wind_speed": o.wind_speed or 10.0,
            "storm_indicator": o.storm_indicator or 0,
            "surveyed_area_m2": o.surveyed_area_m2 or 10000.0,
            "observation_duration_hours": o.observation_duration_hours or 4.0,
        }
        for o in obs_query
    ])

    df_eng = preprocessor.engineer_features(df)
    X, _, metas = preprocessor.create_sliding_windows(df_eng, horizon=1)

    if len(X) == 0:
        return {"anomalies": [], "total_checked": 0}

    # Load calibrated threshold from metrics file
    metrics_path = settings.METRICS_DIR / "autoencoder_metrics.json"
    threshold = 0.045
    if metrics_path.exists():
        with open(metrics_path, "r") as mf:
            threshold = json.load(mf).get("calibrated_threshold_mse", 0.045)

    if has_pt:
        input_dim = len(preprocessor.feature_columns)
        model = SequenceAutoencoder(seq_len=preprocessor.sequence_length, num_features=input_dim, latent_dim=16)
        model.load_state_dict(torch.load(str(pt_path), map_location="cpu"))
        model.eval()
        model.anomaly_threshold = threshold
        x_tensor = torch.from_numpy(X).float()
        anomaly_results = model.detect_anomalies(x_tensor)
    else:
        anomaly_results = detect_autoencoder_anomalies_numpy(X, npz_path, threshold=threshold)

    flagged = []
    for i, res in enumerate(anomaly_results):
        if res["is_anomalous"]:
            meta = metas[i]
            sample_beach_id = meta["beach_id"]
            beach_rec = db.query(Observation).filter(
                Observation.beach_id == sample_beach_id,
                Observation.observation_date == meta["last_input_date"]
            ).first()

            flagged.append({
                "beach_id": sample_beach_id,
                "beach_name": beach_rec.beach.name if (beach_rec and beach_rec.beach) else sample_beach_id,
                "country": beach_rec.beach.country if (beach_rec and beach_rec.beach) else "Global",
                "date": meta["last_input_date"],
                "observed_waste_kg": beach_rec.waste_mass_kg if beach_rec else 0.0,
                "reconstruction_error": round(res["reconstruction_error"], 5),
                "threshold": round(res["threshold"], 5),
                "severity_ratio": round(res["severity_ratio"], 2),
                "interpretation": res["interpretation"],
                "storm_flag": beach_rec.storm_indicator if beach_rec else 0,
                "rainfall_mm": beach_rec.rainfall_mm if beach_rec else 0.0
            })

    # Sort by reconstruction error descending
    flagged.sort(key=lambda x: x["reconstruction_error"], reverse=True)

    return {
        "threshold": round(threshold, 5),
        "total_sequences_inspected": len(anomaly_results),
        "anomalies_detected_count": len(flagged),
        "anomalies": flagged[:20],
        "methodology_note": (
            "Anomalies represent time windows where the autoencoder reconstruction error exceeds "
            "the 95th percentile validation threshold. These identify extreme storm surges, abnormal tourist debris, "
            "or sampling spikes without assuming the data is corrupted."
        )
    }
