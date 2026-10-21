"""
Base interfaces and definitions for forecasting models.
"""
from abc import ABC, abstractmethod
import numpy as np

class BaseForecaster(ABC):
    @abstractmethod
    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray):
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Takes input sequence X of shape (batch, sequence_length, num_features)
        Returns predictions of shape (batch, horizon)
        """
        pass
