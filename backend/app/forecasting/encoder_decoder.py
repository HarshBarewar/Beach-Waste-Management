"""
PyTorch LSTM Encoder-Decoder Model for Multi-Step Time-Series Forecasting.

Encoder learns compressed temporal representation of historical multi-variable observations.
Decoder generates future sequence step-by-step or via autoregressive unrolling.
"""
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple

class EncoderLSTM(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.15):
        super(EncoderLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )

    def forward(self, x: torch.Tensor):
        # x: (batch_size, seq_len, input_dim)
        outputs, (hn, cn) = self.lstm(x)
        return hn, cn

class DecoderLSTM(nn.Module):
    def __init__(self, output_dim: int = 1, hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.15):
        super(DecoderLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=output_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.fc_out = nn.Linear(hidden_dim, output_dim)

    def forward(self, x_step: torch.Tensor, hn: torch.Tensor, cn: torch.Tensor):
        # x_step: (batch_size, 1, output_dim)
        out, (hn, cn) = self.lstm(x_step, (hn, cn))
        prediction = self.fc_out(out)
        return prediction, hn, cn

class PyTorchEncoderDecoder(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 64,
        num_layers: int = 2,
        horizon: int = 6,
        dropout: float = 0.15
    ):
        super(PyTorchEncoderDecoder, self).__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.horizon = horizon
        self.encoder = EncoderLSTM(input_dim, hidden_dim, num_layers, dropout)
        self.decoder = DecoderLSTM(output_dim=1, hidden_dim=hidden_dim, num_layers=num_layers, dropout=dropout)

    def forward(self, x: torch.Tensor, target_y: torch.Tensor = None, teacher_forcing_ratio: float = 0.0) -> torch.Tensor:
        """
        x: (batch_size, seq_len, input_dim)
        target_y: optional for teacher forcing (batch_size, horizon)
        returns: (batch_size, horizon)
        """
        batch_size = x.size(0)
        hn, cn = self.encoder(x)

        # Decoder start token: use last known target value from input sequence (feature 0 is target)
        decoder_input = x[:, -1:, 0:1]  # (batch_size, 1, 1)

        outputs = []
        for t in range(self.horizon):
            pred_step, hn, cn = self.decoder(decoder_input, hn, cn)
            outputs.append(pred_step.squeeze(1))  # (batch_size, 1)

            # Next step input: either teacher forcing (during training if enabled) or previous prediction
            use_teacher = (target_y is not None) and (np.random.random() < teacher_forcing_ratio)
            if use_teacher and t < (self.horizon - 1):
                decoder_input = target_y[:, t:t+1].unsqueeze(1)
            else:
                decoder_input = pred_step

        # Concatenate outputs: (batch_size, horizon)
        forecast = torch.cat(outputs, dim=1)
        return forecast

    def predict_with_uncertainty(
        self,
        x: torch.Tensor,
        num_samples: int = 30
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        self.train()
        predictions = []
        with torch.no_grad():
            for _ in range(num_samples):
                preds = self.forward(x, teacher_forcing_ratio=0.0).cpu().numpy()
                predictions.append(preds)
        self.eval()

        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        lower_bound = np.percentile(predictions, 10, axis=0)
        upper_bound = np.percentile(predictions, 90, axis=0)

        mean_pred = np.clip(mean_pred, 0, None)
        lower_bound = np.clip(lower_bound, 0, None)
        upper_bound = np.clip(upper_bound, 0, None)

        return mean_pred, lower_bound, upper_bound
