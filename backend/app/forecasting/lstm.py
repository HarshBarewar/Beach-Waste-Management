"""
PyTorch Standard LSTM Forecasting Model for BeachWaste AI.

Direct multi-horizon time-series forecasting with configurable layers,
hidden dimensions, dropout regularization, and Monte-Carlo Dropout uncertainty.
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Optional, Tuple

class PyTorchLSTM(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        num_layers: int = 2,
        horizon: int = 6,
        dropout: float = 0.15
    ):
        super(PyTorchLSTM, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.horizon = horizon
        self.dropout_rate = dropout

        # LSTM Layer
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )

        # Fully connected projection layers
        self.fc1 = nn.Linear(hidden_dim, 32)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc_out = nn.Linear(32, horizon)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x shape: (batch_size, seq_len, input_dim)
        output shape: (batch_size, horizon)
        """
        lstm_out, (hn, cn) = self.lstm(x)
        # Use last time-step hidden state representation
        last_hidden = lstm_out[:, -1, :]  # (batch_size, hidden_dim)
        x_dense = self.relu(self.fc1(last_hidden))
        x_dense = self.dropout(x_dense)
        out = self.fc_out(x_dense)
        return out

    def predict_with_uncertainty(
        self,
        x: torch.Tensor,
        num_samples: int = 30
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Monte Carlo Dropout: runs forward pass with active dropout to produce
        mean prediction and empirical 10th/90th percentile prediction intervals.
        """
        self.train()  # Keep dropout active
        predictions = []
        with torch.no_grad():
            for _ in range(num_samples):
                preds = self.forward(x).cpu().numpy()
                predictions.append(preds)
        self.eval()

        predictions = np.array(predictions)  # (num_samples, batch_size, horizon)
        mean_pred = np.mean(predictions, axis=0)
        lower_bound = np.percentile(predictions, 10, axis=0)
        upper_bound = np.percentile(predictions, 90, axis=0)

        # Enforce physical non-negativity constraint
        mean_pred = np.clip(mean_pred, 0, None)
        lower_bound = np.clip(lower_bound, 0, None)
        upper_bound = np.clip(upper_bound, 0, None)

        return mean_pred, lower_bound, upper_bound
