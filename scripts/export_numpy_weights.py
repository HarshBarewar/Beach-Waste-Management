"""
Export trained PyTorch models to lightweight NumPy .npz arrays for Vercel serverless deployment.
"""
import sys
from pathlib import Path
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

def export_weights():
    if not HAS_TORCH:
        print("PyTorch not installed, skipping export.")
        return

    models_dir = ROOT_DIR / "artifacts" / "models"

    # 1. Export LSTM
    lstm_pt = models_dir / "lstm_best.pt"
    if lstm_pt.exists():
        state = torch.load(lstm_pt, map_location="cpu")
        npz_dict = {k: v.cpu().numpy() for k, v in state.items()}
        target_npz = models_dir / "lstm_weights.npz"
        np.savez_compressed(target_npz, **npz_dict)
        print(f"Exported LSTM weights to {target_npz} ({target_npz.stat().st_size} bytes)")

    # 2. Export Encoder-Decoder
    encdec_pt = models_dir / "encoder_decoder_best.pt"
    if encdec_pt.exists():
        state = torch.load(encdec_pt, map_location="cpu")
        npz_dict = {k: v.cpu().numpy() for k, v in state.items()}
        target_npz = models_dir / "encoder_decoder_weights.npz"
        np.savez_compressed(target_npz, **npz_dict)
        print(f"Exported Encoder-Decoder weights to {target_npz} ({target_npz.stat().st_size} bytes)")

    # 3. Export Autoencoder
    ae_pt = models_dir / "autoencoder_best.pt"
    if ae_pt.exists():
        state = torch.load(ae_pt, map_location="cpu")
        npz_dict = {k: v.cpu().numpy() for k, v in state.items()}
        target_npz = models_dir / "autoencoder_weights.npz"
        np.savez_compressed(target_npz, **npz_dict)
        print(f"Exported Autoencoder weights to {target_npz} ({target_npz.stat().st_size} bytes)")

if __name__ == "__main__":
    export_weights()
