# Deep Learning Model Explanation — BeachWaste AI

## 1. Model 1: PyTorch Standard LSTM Forecaster

### 1.1 Architecture Details
- **Input Dimension**: 8 engineered temporal features:
  `[waste_mass_kg, visitor_count, temperature_c, rainfall_mm, wind_speed, storm_indicator, month_sin, month_cos]`
- **Lookback Window (Sequence Length)**: 12 months (capturing a full annual seasonal cycle).
- **Recurrent Core**: 2 stacked PyTorch `nn.LSTM` layers with hidden dimension $H = 64$ and inter-layer dropout $p = 0.15$.
- **Dense Projection**: `Linear(64 -> 32) -> ReLU -> Dropout(0.15) -> Linear(32 -> Horizon)`.
- **Loss Function**: `SmoothL1Loss` (Huber Loss, $\beta = 1.0$) for enhanced gradient stability against extreme storm outlier spikes.
- **Optimizer**: Adam with learning rate $\eta = 0.003$ and `ReduceLROnPlateau` scheduler (decaying LR on validation plateau).

### 1.2 Direct Multi-Horizon vs. Recursive Strategy
- **Direct Multi-Horizon Forecasting**: The output layer directly emits vector $\hat{y} \in \mathbb{R}^H$ for horizons $H \in \{1, 3, 6, 12\}$.
- **Why Direct is Preferred**: Recursive single-step autoregressive generation accumulates prediction errors across time steps (compounding error drift). Direct forecasting optimizes multi-step objectives end-to-end.

### 1.3 Monte Carlo Dropout Uncertainty Estimation
To produce defensive prediction intervals without assuming Gaussian residuals:
- The model runs $S = 30$ forward stochastic inference passes with active dropout ($p = 0.15$).
- The empirical 10th and 90th percentiles define the **90% Confidence Interval**:
  $$\text{Interval}_t = [\hat{y}_{t, 0.10}, \; \hat{y}_{t, 0.90}]$$

---

## 2. Model 2: PyTorch LSTM Encoder-Decoder (Seq2Seq)

### 2.1 Architecture Details
- **Encoder LSTM**: Processes historical window of length $T_{\text{in}} = 12$, producing context hidden representation $(h_n, c_n)$.
- **Decoder LSTM**: Takes context vector and sequentially unrolls predictions for $T_{\text{out}} = H$ steps.
- **Teacher Forcing**: Implemented with decaying schedule during initial training epochs ($p_{\text{tf}} = 0.2$ during epochs 1–10, then $0.0$) to stabilize recurrent autoregression.

---

## 3. Model 3: Sequence Autoencoder for Anomaly Detection

### 3.1 Architecture Details
- **Input**: Flattened sequence of historical window $X \in \mathbb{R}^{T \times F}$ (e.g., $12 \times 8 = 96$ features).
- **Encoder**: Compresses input through `Linear(96 -> 64) -> BatchNorm -> LeakyReLU -> Linear(64 -> 32) -> Linear(32 -> 16)`.
- **Latent Bottleneck**: $z \in \mathbb{R}^{16}$.
- **Decoder**: Reconstructs back to input space with `Sigmoid` activation: `Linear(16 -> 32) -> Linear(32 -> 64) -> BatchNorm -> Linear(64 -> 96)`.

### 3.2 Anomaly Threshold Calibration
- The reconstruction error per sequence is calculated:
  $$\text{MSE}(x, \hat{x}) = \frac{1}{T \cdot F} \sum_{i=1}^T \sum_{j=1}^F (x_{i,j} - \hat{x}_{i,j})^2$$
- The anomaly threshold $\tau$ is calibrated strictly on the held-out validation set at the **95th percentile**:
  $$\tau = \text{Percentile}_{95}(\text{MSE}_{\text{val}})$$
- Any sequence in testing with $\text{MSE} > \tau$ is flagged as an anomaly.
- **Scientific Interpretation**: An anomalous observation indicates a physical disruption—such as a typhoon surge or unexpected festival litter—rather than corrupted data.
