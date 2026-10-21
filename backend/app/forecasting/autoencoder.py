"""
PyTorch Autoencoder for Waste Pattern Representation and Anomaly Detection.

Learns low-dimensional latent manifold of standard beach waste patterns.
Computes reconstruction error to detect anomalous events (e.g. extreme storm debris,
marine litter surges, or sensor/sampling anomalies).
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Dict, Any, List

class SequenceAutoencoder(nn.Module):
    def __init__(self, seq_len: int, num_features: int, latent_dim: int = 16):
        super(SequenceAutoencoder, self).__init__()
        self.seq_len = seq_len
        self.num_features = num_features
        self.input_dim = seq_len * num_features
        self.latent_dim = latent_dim

        # Encoder: Input -> 64 -> 32 -> latent_dim
        self.encoder = nn.Sequential(
            nn.Linear(self.input_dim, 64),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, 32),
            nn.LeakyReLU(0.2),
            nn.Linear(32, latent_dim)
        )

        # Decoder: latent_dim -> 32 -> 64 -> Input
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.LeakyReLU(0.2),
            nn.Linear(32, 64),
            nn.BatchNorm1d(64),
            nn.LeakyReLU(0.2),
            nn.Linear(64, self.input_dim),
            nn.Sigmoid()  # Data normalized in [0, 1]
        )

        self.anomaly_threshold = 0.05  # Calibrated on validation data

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x: (batch_size, seq_len, num_features)
        Returns: reconstructed_x, latent_z
        """
        batch_size = x.size(0)
        flat_x = x.view(batch_size, -1)
        z = self.encoder(flat_x)
        reconstruction = self.decoder(z)
        reconstructed_x = reconstruction.view(batch_size, self.seq_len, self.num_features)
        return reconstructed_x, z

    def compute_reconstruction_error(self, x: torch.Tensor) -> np.ndarray:
        """
        Calculates MSE reconstruction error per sequence.
        """
        self.eval()
        with torch.no_grad():
            reconstructed, _ = self.forward(x)
            mse = torch.mean((x - reconstructed) ** 2, dim=[1, 2]).cpu().numpy()
        return mse

    def fit_threshold(self, val_x: torch.Tensor, percentile: float = 95.0) -> float:
        """
        Calibrates anomaly threshold on held-out validation sequences without data leakage.
        """
        errors = self.compute_reconstruction_error(val_x)
        self.anomaly_threshold = float(np.percentile(errors, percentile))
        return self.anomaly_threshold

    def detect_anomalies(self, x: torch.Tensor) -> List[Dict[str, Any]]:
        errors = self.compute_reconstruction_error(x)
        results = []
        for i, err in enumerate(errors):
            is_anomaly = bool(err > self.anomaly_threshold)
            results.append({
                "sample_index": i,
                "reconstruction_error": float(err),
                "threshold": float(self.anomaly_threshold),
                "is_anomalous": is_anomaly,
                "severity_ratio": float(err / max(1e-5, self.anomaly_threshold)),
                "interpretation": (
                    "Unusual waste pattern detected (possible storm aftermath, visitor surge, or sampling discrepancy)"
                    if is_anomaly else "Normal recurring seasonal pattern"
                )
            })
        return results
