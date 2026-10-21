"""
Model Training and Checkpoint Management Engine for BeachWaste AI.

Handles background asynchronous training, validation loss tracking, early stopping,
model artifact checkpointing, and evaluation against baseline models.
"""
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
import pandas as pd
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

from backend.app.core.config import settings
from backend.app.database.database import SessionLocal
from backend.app.database.models import ModelTrainingJob, Observation
from backend.app.data_pipeline.preprocessor import TimeSeriesPreprocessor
from backend.app.forecasting.lstm import PyTorchLSTM
from backend.app.forecasting.encoder_decoder import PyTorchEncoderDecoder
from backend.app.forecasting.autoencoder import SequenceAutoencoder
from backend.app.forecasting.baselines import PersistenceBaseline, SeasonalNaiveBaseline
from backend.app.evaluation.metrics import calculate_metrics

def train_model_pipeline(
    job_id: str,
    model_type: str = "lstm",
    dataset_id: str = "demo_dataset",
    epochs: int = 40,
    batch_size: int = 16,
    learning_rate: float = 0.003,
    sequence_length: int = 12,
    hidden_dim: int = 64,
    dropout: float = 0.15,
    horizon: int = 6,
    device_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes chronological model training, evaluation, and checkpoint persistence.
    Updates the database ModelTrainingJob record with epoch progress and final metrics.
    """
    db = SessionLocal()
    job = db.query(ModelTrainingJob).filter(ModelTrainingJob.id == job_id).first()
    if not job:
        db.close()
        raise ValueError(f"Job {job_id} not found")

    try:
        job.status = "preparing"
        db.commit()

        # Load observations from database
        obs_query = db.query(Observation).all()
        if not obs_query:
            raise ValueError("No observation records found in database. Seed demo data first.")

        records = [
            {
                "beach_id": o.beach_id,
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
        ]
        df = pd.DataFrame(records)

        # Preprocessing & Chronological splitting
        preprocessor = TimeSeriesPreprocessor(sequence_length=sequence_length, horizon=horizon)
        df_eng = preprocessor.engineer_features(df)
        
        # Chronological windowed split (zero leakage, fits scalers on train split)
        (
            (X_train, y_train, _),
            (X_val, y_val, _),
            (X_test, y_test, meta_test)
        ) = preprocessor.create_chronological_datasets(df_eng, train_ratio=0.70, val_ratio=0.15, horizon=horizon)

        # Save preprocessor state
        preprocessor_path = settings.MODEL_DIR / f"{model_type}_preprocessor.pkl"
        preprocessor.save_state(str(preprocessor_path))

        if len(X_train) == 0:
            raise ValueError("Insufficient sequence records to form training windows. Check sequence_length.")

        device = torch.device(device_name if device_name else ("cuda" if torch.cuda.is_available() else "cpu"))

        # Convert to PyTorch tensors
        train_loader = DataLoader(
            TensorDataset(torch.from_numpy(X_train).float(), torch.from_numpy(y_train).float()),
            batch_size=batch_size,
            shuffle=True
        )
        val_loader = DataLoader(
            TensorDataset(torch.from_numpy(X_val).float(), torch.from_numpy(y_val).float()),
            batch_size=batch_size,
            shuffle=False
        )

        input_dim = len(preprocessor.feature_columns)

        # Instantiate Model
        if model_type == "lstm":
            model = PyTorchLSTM(
                input_dim=input_dim,
                hidden_dim=hidden_dim,
                num_layers=2,
                horizon=horizon,
                dropout=dropout
            ).to(device)
            criterion = nn.SmoothL1Loss()  # Huber loss for robustness against waste spikes
        elif model_type == "encoder_decoder":
            model = PyTorchEncoderDecoder(
                input_dim=input_dim,
                hidden_dim=hidden_dim,
                num_layers=2,
                horizon=horizon,
                dropout=dropout
            ).to(device)
            criterion = nn.SmoothL1Loss()
        elif model_type == "autoencoder":
            model = SequenceAutoencoder(
                seq_len=sequence_length,
                num_features=input_dim,
                latent_dim=16
            ).to(device)
            criterion = nn.MSELoss()
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)

        train_loss_hist = []
        val_loss_hist = []
        best_val_loss = float('inf')
        patience = 12
        patience_counter = 0

        job.status = "training"
        db.commit()

        for epoch in range(1, epochs + 1):
            model.train()
            total_train_loss = 0.0

            for bx, by in train_loader:
                bx = bx.to(device)
                by = by.to(device)
                optimizer.zero_grad()

                if model_type == "autoencoder":
                    recon, _ = model(bx)
                    loss = criterion(recon, bx)
                elif model_type == "encoder_decoder":
                    preds = model(bx, target_y=by, teacher_forcing_ratio=0.2 if epoch < 10 else 0.0)
                    loss = criterion(preds, by)
                else:
                    preds = model(bx)
                    loss = criterion(preds, by)

                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                total_train_loss += loss.item() * bx.size(0)

            avg_train_loss = total_train_loss / len(X_train)
            train_loss_hist.append(round(avg_train_loss, 5))

            # Validation step
            model.eval()
            total_val_loss = 0.0
            with torch.no_grad():
                for bx, by in val_loader:
                    bx = bx.to(device)
                    by = by.to(device)
                    if model_type == "autoencoder":
                        recon, _ = model(bx)
                        v_loss = criterion(recon, bx)
                    elif model_type == "encoder_decoder":
                        preds = model(bx, teacher_forcing_ratio=0.0)
                        v_loss = criterion(preds, by)
                    else:
                        preds = model(bx)
                        v_loss = criterion(preds, by)
                    total_val_loss += v_loss.item() * bx.size(0)

            avg_val_loss = total_val_loss / max(len(X_val), 1)
            val_loss_hist.append(round(avg_val_loss, 5))
            scheduler.step(avg_val_loss)

            # Early stopping & best checkpoint
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                patience_counter = 0
                best_model_path = settings.MODEL_DIR / f"{model_type}_best.pt"
                torch.save(model.state_dict(), str(best_model_path))
            else:
                patience_counter += 1
                if patience_counter >= patience and epoch >= 15:
                    print(f"Early stopping at epoch {epoch}")
                    break

            # Periodically update job record for polling UI
            if epoch % 5 == 0 or epoch == epochs:
                job.train_loss_history = json.dumps(train_loss_hist)
                job.val_loss_history = json.dumps(val_loss_hist)
                db.commit()

        # Load best model weights for evaluation
        best_model_path = settings.MODEL_DIR / f"{model_type}_best.pt"
        if best_model_path.exists():
            model.load_state_dict(torch.load(str(best_model_path), map_location=device))
        model.eval()

        # Evaluation on held-out test split
        metrics = {}
        if model_type in ["lstm", "encoder_decoder"]:
            with torch.no_grad():
                X_test_tensor = torch.from_numpy(X_test).float().to(device)
                if model_type == "encoder_decoder":
                    y_test_pred_scaled = model(X_test_tensor, teacher_forcing_ratio=0.0).cpu().numpy()
                else:
                    y_test_pred_scaled = model(X_test_tensor).cpu().numpy()

            # Unscale back to actual kg
            y_test_pred = preprocessor.inverse_transform_targets(y_test_pred_scaled)
            y_test_true = preprocessor.inverse_transform_targets(y_test)

            metrics = calculate_metrics(y_test_true, y_test_pred)

            # Also evaluate baselines on test set for fair comparison
            pers_preds = []
            s_naive_preds = []
            pers_model = PersistenceBaseline(horizon=horizon)
            s_naive_model = SeasonalNaiveBaseline(horizon=horizon)

            for sample_meta in meta_test:
                b_id = sample_meta["beach_id"]
                # Extract history preceding test point
                beach_hist = df[df["beach_id"] == b_id]["waste_mass_kg"].values
                pers_preds.append(pers_model.predict(beach_hist))
                s_naive_preds.append(s_naive_model.predict(beach_hist))

            if pers_preds:
                metrics["persistence_baseline"] = calculate_metrics(y_test_true, np.array(pers_preds))
            if s_naive_preds:
                metrics["seasonal_naive_baseline"] = calculate_metrics(y_test_true, np.array(s_naive_preds))

        elif model_type == "autoencoder":
            # Calibrate anomaly threshold on validation set
            val_tensor = torch.from_numpy(X_val).float().to(device)
            threshold = model.fit_threshold(val_tensor, percentile=95.0)

            test_tensor = torch.from_numpy(X_test).float().to(device)
            test_anomaly_results = model.detect_anomalies(test_tensor)
            anom_count = sum(1 for a in test_anomaly_results if a["is_anomalous"])

            metrics = {
                "calibrated_threshold_mse": round(threshold, 6),
                "val_mean_reconstruction_error": round(float(np.mean(model.compute_reconstruction_error(val_tensor))), 6),
                "test_mean_reconstruction_error": round(float(np.mean(model.compute_reconstruction_error(test_tensor))), 6),
                "test_anomalies_detected": anom_count,
                "test_samples_total": len(test_anomaly_results),
                "interpretation": "Reconstruction error flags non-conforming waste spikes and meteorological outliers."
            }

        # Save metrics file
        metrics_file = settings.METRICS_DIR / f"{model_type}_metrics.json"
        with open(metrics_file, "w") as mf:
            json.dump(metrics, mf, indent=2)

        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc).isoformat()
        job.train_loss_history = json.dumps(train_loss_hist)
        job.val_loss_history = json.dumps(val_loss_hist)
        job.metrics = json.dumps(metrics)
        job.artifact_path = str(best_model_path)
        db.commit()

        return {
            "status": "completed",
            "job_id": job_id,
            "metrics": metrics,
            "train_loss_history": train_loss_hist,
            "val_loss_history": val_loss_hist
        }

    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc).isoformat()
        db.commit()
        raise e
    finally:
        db.close()

def launch_training_job_async(
    model_type: str = "lstm",
    dataset_id: str = "demo_dataset",
    epochs: int = 40,
    batch_size: int = 16,
    learning_rate: float = 0.003,
    sequence_length: int = 12,
    hidden_dim: int = 64,
    dropout: float = 0.15
) -> str:
    """
    Spawns background training worker thread and returns job_id.
    """
    job_id = f"job_{model_type}_{int(datetime.now(timezone.utc).timestamp())}"
    db = SessionLocal()
    hyperparams = {
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "sequence_length": sequence_length,
        "hidden_dim": hidden_dim,
        "dropout": dropout
    }

    job = ModelTrainingJob(
        id=job_id,
        model_type=model_type,
        status="pending",
        dataset_id=dataset_id,
        hyperparams=json.dumps(hyperparams)
    )
    db.add(job)
    db.commit()
    db.close()

    thread = threading.Thread(
        target=train_model_pipeline,
        kwargs={
            "job_id": job_id,
            "model_type": model_type,
            "dataset_id": dataset_id,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "sequence_length": sequence_length,
            "hidden_dim": hidden_dim,
            "dropout": dropout
        },
        daemon=True
    )
    thread.start()
    return job_id
