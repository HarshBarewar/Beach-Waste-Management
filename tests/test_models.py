"""
Tests for PyTorch Deep Learning models: shapes, forward pass, and baselines.
"""
import torch
import numpy as np
from backend.app.forecasting.lstm import PyTorchLSTM
from backend.app.forecasting.encoder_decoder import PyTorchEncoderDecoder
from backend.app.forecasting.autoencoder import SequenceAutoencoder
from backend.app.forecasting.baselines import PersistenceBaseline, SeasonalNaiveBaseline

def test_lstm_forward_shape():
    batch_size = 4
    seq_len = 12
    input_dim = 8
    horizon = 6

    model = PyTorchLSTM(input_dim=input_dim, hidden_dim=32, num_layers=2, horizon=horizon)
    x = torch.randn(batch_size, seq_len, input_dim)
    out = model(x)
    assert out.shape == (batch_size, horizon)

def test_lstm_uncertainty():
    model = PyTorchLSTM(input_dim=8, hidden_dim=32, num_layers=2, horizon=6, dropout=0.2)
    x = torch.randn(2, 12, 8)
    mean, low, upp = model.predict_with_uncertainty(x, num_samples=10)
    assert mean.shape == (2, 6)
    assert low.shape == (2, 6)
    assert upp.shape == (2, 6)

def test_encoder_decoder_forward_shape():
    batch_size = 4
    seq_len = 12
    input_dim = 8
    horizon = 6

    model = PyTorchEncoderDecoder(input_dim=input_dim, hidden_dim=32, num_layers=2, horizon=horizon)
    x = torch.randn(batch_size, seq_len, input_dim)
    out = model(x)
    assert out.shape == (batch_size, horizon)

def test_autoencoder_reconstruction_shape():
    batch_size = 5
    seq_len = 12
    num_features = 8

    model = SequenceAutoencoder(seq_len=seq_len, num_features=num_features, latent_dim=8)
    x = torch.rand(batch_size, seq_len, num_features)
    recon, z = model(x)
    assert recon.shape == (batch_size, seq_len, num_features)
    assert z.shape == (batch_size, 8)

def test_persistence_baseline():
    history = np.array([100.0, 150.0, 200.0])
    model = PersistenceBaseline(horizon=4)
    pred = model.predict(history)
    assert len(pred) == 4
    assert np.all(pred == 200.0)

def test_seasonal_naive_baseline():
    history = np.arange(1, 25, dtype=np.float32)  # 24 months
    model = SeasonalNaiveBaseline(horizon=6, seasonal_period=12)
    pred = model.predict(history)
    assert len(pred) == 6
    # Should equal history[-12 : -6]
    assert np.array_equal(pred, history[12:18])
