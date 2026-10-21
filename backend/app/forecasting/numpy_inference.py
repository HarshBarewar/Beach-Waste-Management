"""
Pure NumPy Deep Learning Inference Engine for BeachWaste AI.

Enables fast, lightweight inference on serverless environments (such as Vercel)
without requiring the 500MB+ PyTorch binary, while producing mathematically
identical predictions from exported weights.
"""
import numpy as np
from pathlib import Path
from typing import Tuple, List, Dict, Any

def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30.0, 30.0)))

def _lstm_cell(xt: np.ndarray, h_prev: np.ndarray, c_prev: np.ndarray, w_ih: np.ndarray, w_hh: np.ndarray, bias: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Standard PyTorch LSTM Cell computation:
    Gates order in PyTorch: (i, f, g, o)
    """
    hidden_dim = w_hh.shape[1]
    gates = xt @ w_ih.T + h_prev @ w_hh.T + bias
    
    i = _sigmoid(gates[:, 0:hidden_dim])
    f = _sigmoid(gates[:, hidden_dim:2*hidden_dim])
    g = np.tanh(gates[:, 2*hidden_dim:3*hidden_dim])
    o = _sigmoid(gates[:, 3*hidden_dim:4*hidden_dim])

    c = f * c_prev + i * g
    h = o * np.tanh(c)
    return h, c

def _run_lstm_layer(x: np.ndarray, w_ih: np.ndarray, w_hh: np.ndarray, b_ih: np.ndarray, b_hh: np.ndarray) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
    batch_size, seq_len, _ = x.shape
    hidden_dim = w_hh.shape[1]
    bias = b_ih + b_hh

    h = np.zeros((batch_size, hidden_dim), dtype=np.float32)
    c = np.zeros((batch_size, hidden_dim), dtype=np.float32)
    outputs = []

    for t in range(seq_len):
        h, c = _lstm_cell(x[:, t, :], h, c, w_ih, w_hh, bias)
        outputs.append(h)

    return np.stack(outputs, axis=1), (h, c)

def predict_lstm_numpy(
    x_input: np.ndarray,
    weights_path: Path,
    horizon: int = 6,
    num_samples: int = 30,
    dropout_rate: float = 0.15
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    x_input shape: (batch_size, seq_len, input_dim)
    """
    weights = np.load(weights_path)
    
    w_ih_l0 = weights['lstm.weight_ih_l0']
    w_hh_l0 = weights['lstm.weight_hh_l0']
    b_ih_l0 = weights['lstm.bias_ih_l0']
    b_hh_l0 = weights['lstm.bias_hh_l0']

    w_ih_l1 = weights['lstm.weight_ih_l1']
    w_hh_l1 = weights['lstm.weight_hh_l1']
    b_ih_l1 = weights['lstm.bias_ih_l1']
    b_hh_l1 = weights['lstm.bias_hh_l1']

    fc1_w = weights['fc1.weight']
    fc1_b = weights['fc1.bias']
    fc_out_w = weights['fc_out.weight']
    fc_out_b = weights['fc_out.bias']

    # Deterministic forward pass
    l0_out, _ = _run_lstm_layer(x_input, w_ih_l0, w_hh_l0, b_ih_l0, b_hh_l0)
    l1_out, (hn, _) = _run_lstm_layer(l0_out, w_ih_l1, w_hh_l1, b_ih_l1, b_hh_l1)
    
    dense = np.maximum(0, hn @ fc1_w.T + fc1_b)
    pred_mean = dense @ fc_out_w.T + fc_out_b

    # Monte Carlo Dropout sampling for prediction intervals
    preds = []
    batch_size = x_input.shape[0]
    hidden_dim = fc1_w.shape[0]

    for _ in range(num_samples):
        # Apply dropout mask to dense representations
        mask = (np.random.random((batch_size, hidden_dim)) > dropout_rate).astype(np.float32) / (1.0 - dropout_rate)
        sampled_dense = dense * mask
        pred_sample = sampled_dense @ fc_out_w.T + fc_out_b
        preds.append(pred_sample)

    preds = np.array(preds)
    lower = np.percentile(preds, 10, axis=0)
    upper = np.percentile(preds, 90, axis=0)

    return np.clip(pred_mean, 0, None), np.clip(lower, 0, None), np.clip(upper, 0, None)

def predict_encoder_decoder_numpy(
    x_input: np.ndarray,
    weights_path: Path,
    horizon: int = 6
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    weights = np.load(weights_path)
    batch_size = x_input.shape[0]

    # Encoder
    enc_w_ih_l0 = weights['encoder.lstm.weight_ih_l0']
    enc_w_hh_l0 = weights['encoder.lstm.weight_hh_l0']
    enc_b_ih_l0 = weights['encoder.lstm.bias_ih_l0']
    enc_b_hh_l0 = weights['encoder.lstm.bias_hh_l0']

    enc_w_ih_l1 = weights['encoder.lstm.weight_ih_l1']
    enc_w_hh_l1 = weights['encoder.lstm.weight_hh_l1']
    enc_b_ih_l1 = weights['encoder.lstm.bias_ih_l1']
    enc_b_hh_l1 = weights['encoder.lstm.bias_hh_l1']

    l0_out, (h0, c0) = _run_lstm_layer(x_input, enc_w_ih_l0, enc_w_hh_l0, enc_b_ih_l0, enc_b_hh_l0)
    _, (h1, c1) = _run_lstm_layer(l0_out, enc_w_ih_l1, enc_w_hh_l1, enc_b_ih_l1, enc_b_hh_l1)

    # Decoder
    dec_w_ih_l0 = weights['decoder.lstm.weight_ih_l0']
    dec_w_hh_l0 = weights['decoder.lstm.weight_hh_l0']
    dec_b_l0 = weights['decoder.lstm.bias_ih_l0'] + weights['decoder.lstm.bias_hh_l0']

    dec_w_ih_l1 = weights['decoder.lstm.weight_ih_l1']
    dec_w_hh_l1 = weights['decoder.lstm.weight_hh_l1']
    dec_b_l1 = weights['decoder.lstm.bias_ih_l1'] + weights['decoder.lstm.bias_hh_l1']

    dec_fc_w = weights['decoder.fc_out.weight']
    dec_fc_b = weights['decoder.fc_out.bias']

    step_input = x_input[:, -1, 0:1] # Target is feature 0
    cur_h0, cur_c0 = h0, c0
    cur_h1, cur_c1 = h1, c1

    outputs = []
    for _ in range(horizon):
        cur_h0, cur_c0 = _lstm_cell(step_input, cur_h0, cur_c0, dec_w_ih_l0, dec_w_hh_l0, dec_b_l0)
        cur_h1, cur_c1 = _lstm_cell(cur_h0, cur_h1, cur_c1, dec_w_ih_l1, dec_w_hh_l1, dec_b_l1)
        pred_val = cur_h1 @ dec_fc_w.T + dec_fc_b
        outputs.append(pred_val.squeeze(1))
        step_input = pred_val

    pred_mean = np.column_stack(outputs)
    lower = pred_mean * 0.88
    upper = pred_mean * 1.12
    return np.clip(pred_mean, 0, None), np.clip(lower, 0, None), np.clip(upper, 0, None)

def reconstruct_autoencoder_numpy(x_seq: np.ndarray, weights_path: Path) -> np.ndarray:
    """
    x_seq: (batch_size, seq_len, num_features)
    Returns: reconstructed sequence of same shape
    """
    w = np.load(weights_path)
    b, s, f = x_seq.shape
    flat_x = x_seq.reshape(b, -1)

    # Encoder
    h0 = flat_x @ w['encoder.0.weight'].T + w['encoder.0.bias']
    h1 = (h0 - w['encoder.1.running_mean']) / np.sqrt(w['encoder.1.running_var'] + 1e-5) * w['encoder.1.weight'] + w['encoder.1.bias']
    h2 = np.where(h1 > 0, h1, 0.2 * h1)
    h3 = h2 @ w['encoder.3.weight'].T + w['encoder.3.bias']
    h4 = np.where(h3 > 0, h3, 0.2 * h3)
    z = h4 @ w['encoder.5.weight'].T + w['encoder.5.bias']

    # Decoder
    d0 = z @ w['decoder.0.weight'].T + w['decoder.0.bias']
    d1 = np.where(d0 > 0, d0, 0.2 * d0)
    d2 = d1 @ w['decoder.2.weight'].T + w['decoder.2.bias']
    d3 = (d2 - w['decoder.3.running_mean']) / np.sqrt(w['decoder.3.running_var'] + 1e-5) * w['decoder.3.weight'] + w['decoder.3.bias']
    d4 = np.where(d3 > 0, d3, 0.2 * d3)
    d5 = d4 @ w['decoder.5.weight'].T + w['decoder.5.bias']
    recon_flat = 1.0 / (1.0 + np.exp(-np.clip(d5, -30.0, 30.0)))
    return recon_flat.reshape(b, s, f)

def detect_autoencoder_anomalies_numpy(x_seq: np.ndarray, weights_path: Path, threshold: float = 0.045) -> List[Dict[str, Any]]:
    """
    Reconstructs sequence and calculates per-sample MSE.
    """
    reconstructed = reconstruct_autoencoder_numpy(x_seq, weights_path)
    errors = np.mean((x_seq - reconstructed) ** 2, axis=(1, 2))
    
    results = []
    for i, err in enumerate(errors):
        is_anomaly = bool(err > threshold)
        results.append({
            "sample_index": i,
            "reconstruction_error": float(err),
            "threshold": float(threshold),
            "is_anomalous": is_anomaly,
            "severity_ratio": float(err / max(1e-5, threshold)),
            "interpretation": (
                "Unusual waste pattern detected (possible storm aftermath, visitor surge, or sampling discrepancy)"
                if is_anomaly else "Normal recurring seasonal pattern"
            )
        })
    return results
