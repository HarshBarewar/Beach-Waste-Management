"""
CLI script to train deep learning models (LSTM, Encoder-Decoder, Autoencoder)
and baseline models, saving model checkpoints and evaluation metrics.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.database.database import engine, Base, SessionLocal
from backend.app.data_pipeline.ingestion import seed_demo_data
from backend.app.training.trainer import train_model_pipeline
from backend.app.database.models import ModelTrainingJob

def main():
    print("=" * 70)
    print("BeachWaste AI — Deep Learning Model Training Suite")
    print("=" * 70)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db, force_regenerate=False)
    finally:
        db.close()

    models_to_train = [
        ("lstm", 35, 64, 0.003),
        ("encoder_decoder", 35, 64, 0.003),
        ("autoencoder", 35, 16, 0.005)
    ]

    for model_type, epochs, hidden_dim, lr in models_to_train:
        print(f"\n>>> Starting training for: {model_type.upper()} ({epochs} epochs, lr={lr}, hidden_dim={hidden_dim})")
        job_id = f"cli_{model_type}_{int(datetime.now(timezone.utc).timestamp())}"
        
        db = SessionLocal()
        job = ModelTrainingJob(
            id=job_id,
            model_type=model_type,
            status="pending",
            dataset_id="demo_dataset"
        )
        db.add(job)
        db.commit()
        db.close()

        result = train_model_pipeline(
            job_id=job_id,
            model_type=model_type,
            dataset_id="demo_dataset",
            epochs=epochs,
            batch_size=16,
            learning_rate=lr,
            sequence_length=12,
            hidden_dim=hidden_dim,
            dropout=0.15,
            horizon=6
        )

        print(f"Status: {result['status']}")
        if "metrics" in result and result["metrics"]:
            print(f"Test Metrics: {result['metrics']}")

    print("\n" + "=" * 70)
    print("All models successfully trained, evaluated, and saved to artifacts/models!")
    print("=" * 70)

if __name__ == "__main__":
    main()
