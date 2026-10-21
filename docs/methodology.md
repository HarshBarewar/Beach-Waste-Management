# Scientific Methodology — BeachWaste AI

## 1. Problem Statement
Beach litter and marine debris threaten coastal ecosystems, commercial fisheries, public health, and tourism-based economies. Traditional cleanup interventions are inherently reactive: municipal work crews or volunteer organizations respond only *after* beaches become overwhelmed with accumulated waste.

Accurate predictive modeling of beach waste allows:
- Proactive allocation of cleanup crews and mechanical beach rakes before peak accumulation.
- Pre-positioning of storm interceptor booms prior to forecasted cyclone/monsoon rain events.
- Transparent budgeting of waste hauling, sorting, and certified material recycling streams.

---

## 2. The Four Analytical Responsibilities

A key tenet of BeachWaste AI is strictly delineating four separate analytical objectives:

```
+───────────────────────────────────────────────────────────────────────────────+
| 1. Waste Quantity Forecasting (Deep Learning)                                 |
|    "How many kilograms of total coastal waste will accumulate next month?"    |
+───────────────────────────────────────┬───────────────────────────────────────+
                                        ▼
+───────────────────────────────────────────────────────────────────────────────+
| 2. Waste Composition Estimation (Physical & Recovery Streams)                 |
|    "What fraction of that mass is PET plastic, aluminium cans, or organics?" |
+───────────────────────────────────────┬───────────────────────────────────────+
                                        ▼
+───────────────────────────────────────────────────────────────────────────────+
| 3. Pattern Anomaly Detection (Latent Autoencoders)                            |
|    "Does this month exhibit unusual spikes indicative of storms or surges?"  |
+───────────────────────────────────────┬───────────────────────────────────────+
                                        ▼
+───────────────────────────────────────────────────────────────────────────────+
| 4. Treatment & Recycling Cost Modeling (Financial Accounting)                 |
|    "What is the net municipal operating budget needed to process this waste?" |
+───────────────────────────────────────────────────────────────────────────────+
```

### Why these tasks cannot be merged:
- Total waste mass alone **cannot** deduce whether a bottle is recyclable PET or non-recyclable composite multilayer film.
- An anomaly does **not** signify corrupt data; extreme storm events deposit massive natural driftwood and oceanic plastics that are physically valid observations.
- Financial costs depend on regional municipal tariffs and international scrap resin commodity values, requiring editable user parameters.

---

## 3. Data Ingestion & Preprocessing

### 3.1 Feature Engineering
To capture environmental dynamics, raw monthly records undergo feature transformation:
- **Cyclic Month Encoding**: 
  $$\sin\left(\frac{2\pi \cdot \text{month}}{12}\right), \quad \cos\left(\frac{2\pi \cdot \text{month}}{12}\right)$$
  ensuring seamless periodic transition from December ($m=12$) to January ($m=1$).
- **Normalized Waste Intensity**:
  $$\text{Intensity} = \frac{\text{waste\_mass\_kg}}{\text{surveyed\_area\_m}^2}$$
  preventing distorted comparisons between small volunteer transect surveys and multi-kilometer municipal beaches.

### 3.2 Anti-Leakage Chronological Validation
Time-series observations are strictly split chronologically per beach:
- **Earliest 70%**: Training split
- **Subsequent 15%**: Validation split (early stopping & threshold calibration)
- **Most Recent 15%**: Held-out Test split

**Rule**: Preprocessing scalers (MinMaxScaler) are fitted **only** on the training partition. The validation and test sets are transformed using the training parameters, preventing future information from leaking into the model.

---

## 4. Evaluation Metrics

Model performance is evaluated across five complementary metrics:

1. **Mean Absolute Error (MAE)**:
   $$\text{MAE} = \frac{1}{N} \sum_{t=1}^N |y_t - \hat{y}_t|$$

2. **Root Mean Squared Error (RMSE)**:
   $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{t=1}^N (y_t - \hat{y}_t)^2}$$

3. **Weighted Absolute Percentage Error (WAPE)**:
   $$\text{WAPE} = \frac{\sum_{t=1}^N |y_t - \hat{y}_t|}{\sum_{t=1}^N |y_t|} \times 100\%$$
   *Selected over MAPE because beach waste during extreme low season or cold months can approach zero, which causes MAPE division instability.*

4. **Coefficient of Determination ($R^2$)**:
   $$R^2 = 1 - \frac{\sum (y_t - \hat{y}_t)^2}{\sum (y_t - \bar{y})^2}$$

---

## 5. Empirical Results on Held-Out Test Set (N=504 Samples)

| Model / Benchmark | MAE (kg) | RMSE (kg) | WAPE (%) | $R^2$ Score | Rank |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **PyTorch Standard LSTM** | **434.20** | **578.08** | **14.99%** | **0.8031** | **#1 (Best)** |
| **PyTorch LSTM Encoder-Decoder** | 460.70 | 592.17 | 15.90% | 0.7934 | #2 |
| Seasonal Naive Baseline (12-Mo Lag) | 720.67 | 1006.82 | 24.88% | 0.4028 | #3 |
| Persistence Baseline (Last Value) | 900.05 | 1129.61 | 31.07% | 0.2482 | #4 |

**Conclusion**: The PyTorch deep learning models cut WAPE error in half compared to the Persistence baseline and explain over 80% of coastal waste variance ($R^2=0.803$).
