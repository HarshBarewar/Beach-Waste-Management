"""
Baseline Forecasting Models for Benchmark Comparisons.

1. Persistence Baseline: future waste equals latest observed monthly waste.
2. Seasonal Naive Baseline: future waste equals waste observed 12 months prior.
"""
import numpy as np
from typing import Optional

class PersistenceBaseline:
    """
    Persistence (Naive) Forecast:
    y_hat_{t+h} = y_t for all h in horizon.
    """
    def __init__(self, horizon: int = 6):
        self.horizon = horizon

    def predict(self, recent_history_unscaled: np.ndarray) -> np.ndarray:
        """
        recent_history_unscaled: 1D array of historical monthly waste values.
        Returns: 1D array of length `horizon` where each value is recent_history_unscaled[-1].
        """
        last_val = recent_history_unscaled[-1]
        return np.full((self.horizon,), last_val, dtype=np.float32)

class SeasonalNaiveBaseline:
    """
    Seasonal Naive Forecast:
    y_hat_{t+h} = y_{t + h - 12}.
    Assumes repeating 12-month annual seasonality.
    """
    def __init__(self, horizon: int = 6, seasonal_period: int = 12):
        self.horizon = horizon
        self.seasonal_period = seasonal_period

    def predict(self, recent_history_unscaled: np.ndarray) -> np.ndarray:
        """
        recent_history_unscaled: 1D array of at least `seasonal_period` values.
        """
        if len(recent_history_unscaled) < self.seasonal_period:
            # Fall back to persistence if fewer than 12 months available
            last_val = recent_history_unscaled[-1]
            return np.full((self.horizon,), last_val, dtype=np.float32)

        predictions = []
        for h in range(self.horizon):
            # Target month offset back by seasonal_period
            lookback_idx = -(self.seasonal_period - (h % self.seasonal_period))
            predictions.append(recent_history_unscaled[lookback_idx])

        return np.array(predictions, dtype=np.float32)
