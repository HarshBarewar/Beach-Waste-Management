"""
CLI script to inspect and compare evaluation metrics across trained models and baselines.
"""
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from backend.app.core.config import settings

def main():
    print("=" * 75)
    print("BeachWaste AI — Model Evaluation & Benchmark Summary")
    print("=" * 75)

    metrics_dir = settings.METRICS_DIR
    lstm_metrics_file = metrics_dir / "lstm_metrics.json"
    encdec_metrics_file = metrics_dir / "encoder_decoder_metrics.json"
    ae_metrics_file = metrics_dir / "autoencoder_metrics.json"

    print(f"\n{'Model / Benchmark':<28} | {'MAE (kg)':<10} | {'RMSE (kg)':<10} | {'WAPE (%)':<10} | {'R-Squared':<10}")
    print("-" * 75)

    if lstm_metrics_file.exists():
        with open(lstm_metrics_file) as f:
            data = json.load(f)
            print(f"{'PyTorch LSTM':<28} | {data.get('mae', 'N/A'):<10} | {data.get('rmse', 'N/A'):<10} | {data.get('wape_pct', 'N/A'):<10} | {data.get('r2', 'N/A'):<10}")

            if "persistence_baseline" in data:
                pb = data["persistence_baseline"]
                print(f"{'Persistence Baseline':<28} | {pb.get('mae', 'N/A'):<10} | {pb.get('rmse', 'N/A'):<10} | {pb.get('wape_pct', 'N/A'):<10} | {pb.get('r2', 'N/A'):<10}")
            if "seasonal_naive_baseline" in data:
                snb = data["seasonal_naive_baseline"]
                print(f"{'Seasonal Naive Baseline':<28} | {snb.get('mae', 'N/A'):<10} | {snb.get('rmse', 'N/A'):<10} | {snb.get('wape_pct', 'N/A'):<10} | {snb.get('r2', 'N/A'):<10}")

    if encdec_metrics_file.exists():
        with open(encdec_metrics_file) as f:
            data = json.load(f)
            print(f"{'PyTorch Encoder-Decoder':<28} | {data.get('mae', 'N/A'):<10} | {data.get('rmse', 'N/A'):<10} | {data.get('wape_pct', 'N/A'):<10} | {data.get('r2', 'N/A'):<10}")

    print("-" * 75)

    if ae_metrics_file.exists():
        with open(ae_metrics_file) as f:
            ae_data = json.load(f)
            print(f"\nAutoencoder Pattern Analysis:")
            print(f"  • Calibrated Threshold (MSE): {ae_data.get('calibrated_threshold_mse')}")
            print(f"  • Validation Mean Recon Error: {ae_data.get('val_mean_reconstruction_error')}")
            print(f"  • Test Mean Recon Error:       {ae_data.get('test_mean_reconstruction_error')}")
            print(f"  • Anomalies Detected:          {ae_data.get('test_anomalies_detected')} of {ae_data.get('test_samples_total')} test sequences")
    else:
        print("\nAutoencoder metrics not yet generated. Run scripts/train_models.py first.")

if __name__ == "__main__":
    main()
