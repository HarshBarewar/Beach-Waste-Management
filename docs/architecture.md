# System Architecture — BeachWaste AI

## 1. High-Level System Overview

**BeachWaste AI** is engineered as a decoupled, multi-tier deep learning and full-stack web application designed for environmental science labs, municipal coastal management authorities, and marine ecology researchers.

```
+-----------------------------------------------------------------------------------+
|                                  USER BROWSER                                     |
|  React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons + Recharts + Leaflet  |
+-----------------------------------------------------------------------------------+
                                         │  HTTP / REST (JSON)
                                         ▼
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND SERVER                               |
|                     (Asynchronous ASGI on Python 3.13 / Uvicorn)                   |
|                                                                                   |
|  [ Routers ]                                                                      |
|  ├── /api/beaches        (Explorer, Search, Geolocation, Comparison)             |
|  ├── /api/predict        (Deep Learning & Baseline Multi-Step Forecasters)        |
|  ├── /api/composition    (Dual Stream Material & Recovery Estimators)             |
|  ├── /api/cost           (Multi-Currency Operational Lifecycle Costing)           |
|  ├── /api/models         (Async Background Trainer, Metrics, Anomaly Detection)   |
|  ├── /api/datasets       (CSV Ingestion, Schema Validator, Sample Generator)     |
|  └── /api/reports        (ReportLab PDF Generator & Clean CSV Exporters)          |
+-----------------------------------------------------------------------------------+
        │                             │                              │
        ▼                             ▼                              ▼
+─────────────────+         +──────────────────+           +──────────────────+
|  SQLITE STORAGE |         |  PYTORCH DL CORE |           |  ARTIFACT STORE  |
|  (SQLAlchemy)   |         |                  |           |                  |
|  - Beaches      |         |  - LSTM Forecast |           |  - *.pt weights  |
|  - Observations |         |  - Seq2Seq EncDec|           |  - *.pkl scalers |
|  - Jobs         |         |  - Autoencoder   |           |  - metrics JSON  |
|  - Datasets     |         |  - MC Dropout CI |           |  - compiled PDFs |
+─────────────────+         +──────────────────+           +──────────────────+
```

---

## 2. Component Subsystems

### 2.1 Backend Services
1. **Data Ingestion & Validation Pipeline (`backend/app/data_pipeline/`)**:
   - `schema.py`: Canonical column schema enforcement, coordinate validity checks, negative mass guards, missing value audits.
   - `preprocessor.py`: Cyclic trigonometric month encoding, strictly chronological train/validation/test partitioning (70% / 15% / 15%), anti-leakage feature scaling (MinMaxScaler fitted strictly on training observations).
   - `synthetic_generator.py`: Physics-calibrated generator producing 5-year demonstration data across 12 diverse global beaches with realistic meteorological storm debris surges.

2. **Deep Learning Core (`backend/app/forecasting/`)**:
   - `lstm.py`: Deep recurrent architecture for direct multi-horizon forecasting with Monte Carlo Dropout uncertainty propagation.
   - `encoder_decoder.py`: Sequence-to-sequence LSTM mapping historical context states to multi-step future sequences.
   - `autoencoder.py`: Deep latent bottleneck autoencoder trained on normal patterns to detect severe meteorological and marine litter surges via reconstruction error (MSE).
   - `baselines.py`: Persistence and Seasonal Naive reference benchmarks.

3. **Domain Modules**:
   - `backend/app/composition/estimator.py`: Strict separation of physical material categories from practical municipal recovery classifications.
   - `backend/app/cost_estimation/calculator.py`: Transparent lifecycle cost formulas with currency conversion.
   - `backend/app/reporting/pdf_generator.py`: ReportLab document building engine generating publication-grade PDF assessment reports.

### 2.2 Frontend Client Architecture
- Built with **React 18**, **TypeScript**, **Vite**, and **Tailwind CSS**.
- **State Management**: Reactive local hooks and clean service layer decoupling (`services/api.ts`).
- **Interactive Mapping**: Leaflet with OpenStreetMap tiles displaying worldwide beach coordinates, data sufficiency indicators, and coastal characteristics.
- **Data Visualization**: Recharts for time-series lines with confidence intervals, cumulative bar charts, and dual recovery/material donut charts.
