"""
Time-Series Data Preprocessor for BeachWaste AI.

Enforces strict chronological train/val/test splitting, anti-leakage scaling,
cyclic time encoding, and windowed sequence generation for PyTorch models.
"""
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from sklearn.preprocessing import MinMaxScaler
import pickle

FEATURE_COLUMNS = [
    "waste_mass_kg",
    "visitor_count",
    "temperature_c",
    "rainfall_mm",
    "wind_speed",
    "storm_indicator",
    "month_sin",
    "month_cos",
]

TARGET_COLUMN = "waste_mass_kg"

class TimeSeriesPreprocessor:
    def __init__(self, sequence_length: int = 12, horizon: int = 6):
        self.sequence_length = sequence_length
        self.horizon = horizon
        self.feature_columns = FEATURE_COLUMNS
        self.feature_scaler = MinMaxScaler(feature_range=(0, 1))
        self.target_scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_fitted = False

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds cyclic month encoding and normalized intensity columns.
        """
        data = df.copy()
        data["observation_date"] = pd.to_datetime(data["observation_date"])
        data = data.sort_values(["beach_id", "observation_date"]).reset_index(drop=True)

        # Month cyclic encoding
        month = data["observation_date"].dt.month
        data["month_sin"] = np.sin(2 * np.pi * month / 12.0)
        data["month_cos"] = np.cos(2 * np.pi * month / 12.0)

        # Normalized intensities (preserved for reporting/comparisons)
        if "surveyed_area_m2" in data.columns:
            data["kg_per_m2"] = np.where(
                data["surveyed_area_m2"] > 0,
                data["waste_mass_kg"] / data["surveyed_area_m2"],
                np.nan
            )
        if "observation_duration_hours" in data.columns:
            data["kg_per_hour"] = np.where(
                data["observation_duration_hours"] > 0,
                data["waste_mass_kg"] / data["observation_duration_hours"],
                np.nan
            )

        # Fill any missing environmental values with median computed from train if not fitted
        for col in ["visitor_count", "temperature_c", "rainfall_mm", "wind_speed", "storm_indicator"]:
            if col in data.columns:
                data[col] = data[col].ffill().bfill().fillna(0.0)

        return data

    def chronological_split(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Splits dataset chronologically per beach to avoid data leakage across time.
        """
        train_dfs = []
        val_dfs = []
        test_dfs = []

        for beach_id, group in df.groupby("beach_id"):
            group_sorted = group.sort_values("observation_date").reset_index(drop=True)
            n = len(group_sorted)
            train_end = int(n * train_ratio)
            val_end = int(n * (train_ratio + val_ratio))

            train_dfs.append(group_sorted.iloc[:train_end])
            val_dfs.append(group_sorted.iloc[train_end:val_end])
            test_dfs.append(group_sorted.iloc[val_end:])

        train_df = pd.concat(train_dfs, ignore_index=True)
        val_df = pd.concat(val_dfs, ignore_index=True)
        test_df = pd.concat(test_dfs, ignore_index=True)

        return train_df, val_df, test_df

    def fit_scalers(self, train_df: pd.DataFrame):
        """
        Fits MinMaxScaler strictly on the training partition.
        """
        X_train_raw = train_df[self.feature_columns].values
        y_train_raw = train_df[[TARGET_COLUMN]].values

        self.feature_scaler.fit(X_train_raw)
        self.target_scaler.fit(y_train_raw)
        self.is_fitted = True

    def transform_features(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor scalers have not been fitted. Call fit_scalers on train_df first.")
        return self.feature_scaler.transform(df[self.feature_columns].values)

    def inverse_transform_targets(self, y_scaled: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor scalers have not been fitted.")
        orig_shape = y_scaled.shape
        flat = y_scaled.reshape(-1, 1)
        inv = self.target_scaler.inverse_transform(flat)
        return inv.reshape(orig_shape)

    def create_chronological_datasets(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        horizon: Optional[int] = None
    ) -> Tuple[
        Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]],
        Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]],
        Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]
    ]:
        """
        Creates windowed chronological splits across all beaches without data leakage.
        Scalers are fitted strictly on the training partition.
        """
        h = horizon or self.horizon

        # 1. Partition raw observations chronologically to fit scalers on training observations only
        train_df, _, _ = self.chronological_split(df, train_ratio=train_ratio, val_ratio=val_ratio)
        self.fit_scalers(train_df)

        X_train_list, y_train_list, meta_train_list = [], [], []
        X_val_list, y_val_list, meta_val_list = [], [], []
        X_test_list, y_test_list, meta_test_list = [], [], []

        for beach_id, group in df.groupby("beach_id"):
            group_sorted = group.sort_values("observation_date").reset_index(drop=True)
            if len(group_sorted) < (self.sequence_length + h):
                continue

            scaled_feats = self.transform_features(group_sorted)
            target_vals = group_sorted[TARGET_COLUMN].values
            scaled_targets = self.target_scaler.transform(target_vals.reshape(-1, 1)).flatten()

            total_windows = len(group_sorted) - self.sequence_length - h + 1
            n_train = max(1, int(total_windows * train_ratio))
            n_val = max(1, int(total_windows * val_ratio))

            for i in range(total_windows):
                X_w = scaled_feats[i : i + self.sequence_length]
                y_w = scaled_targets[i + self.sequence_length : i + self.sequence_length + h]
                target_dates = group_sorted["observation_date"].iloc[
                    i + self.sequence_length : i + self.sequence_length + h
                ].dt.strftime("%Y-%m-%d").tolist()
                last_in_date = group_sorted["observation_date"].iloc[i + self.sequence_length - 1].strftime("%Y-%m-%d")
                act_y = target_vals[i + self.sequence_length : i + self.sequence_length + h]

                meta = {
                    "beach_id": beach_id,
                    "target_dates": target_dates,
                    "last_input_date": last_in_date,
                    "actual_unscaled_y": act_y
                }

                if i < n_train:
                    X_train_list.append(X_w)
                    y_train_list.append(y_w)
                    meta_train_list.append(meta)
                elif i < (n_train + n_val):
                    X_val_list.append(X_w)
                    y_val_list.append(y_w)
                    meta_val_list.append(meta)
                else:
                    X_test_list.append(X_w)
                    y_test_list.append(y_w)
                    meta_test_list.append(meta)

        return (
            (np.array(X_train_list, dtype=np.float32), np.array(y_train_list, dtype=np.float32), meta_train_list),
            (np.array(X_val_list, dtype=np.float32), np.array(y_val_list, dtype=np.float32), meta_val_list),
            (np.array(X_test_list, dtype=np.float32), np.array(y_test_list, dtype=np.float32), meta_test_list),
        )

    def create_sliding_windows(
        self,
        df: pd.DataFrame,
        horizon: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Creates windowed (X, y) samples per beach.
        X shape: (num_samples, sequence_length, num_features)
        y shape: (num_samples, horizon)
        """
        h = horizon or self.horizon
        X_list = []
        y_list = []
        meta_list = []

        for beach_id, group in df.groupby("beach_id"):
            group_sorted = group.sort_values("observation_date").reset_index(drop=True)
            if len(group_sorted) < (self.sequence_length + h):
                continue

            scaled_feats = self.transform_features(group_sorted)
            target_vals = group_sorted[TARGET_COLUMN].values

            # Scale targets using target_scaler
            scaled_targets = self.target_scaler.transform(target_vals.reshape(-1, 1)).flatten()

            for i in range(len(group_sorted) - self.sequence_length - h + 1):
                X_window = scaled_feats[i : i + self.sequence_length]
                y_window = scaled_targets[i + self.sequence_length : i + self.sequence_length + h]

                target_dates = group_sorted["observation_date"].iloc[
                    i + self.sequence_length : i + self.sequence_length + h
                ].dt.strftime("%Y-%m-%d").tolist()

                X_list.append(X_window)
                y_list.append(y_window)
                meta_list.append({
                    "beach_id": beach_id,
                    "target_dates": target_dates,
                    "last_input_date": group_sorted["observation_date"].iloc[i + self.sequence_length - 1].strftime("%Y-%m-%d"),
                    "actual_unscaled_y": target_vals[i + self.sequence_length : i + self.sequence_length + h]
                })

        if not X_list:
            return np.empty((0, self.sequence_length, len(self.feature_columns))), np.empty((0, h)), []

        return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.float32), meta_list

    def save_state(self, file_path: str):
        with open(file_path, "wb") as f:
            pickle.dump({
                "sequence_length": self.sequence_length,
                "horizon": self.horizon,
                "feature_columns": self.feature_columns,
                "feature_scaler": self.feature_scaler,
                "target_scaler": self.target_scaler,
                "is_fitted": self.is_fitted
            }, f)

    def load_state(self, file_path: str):
        with open(file_path, "rb") as f:
            state = pickle.load(f)
            self.sequence_length = state["sequence_length"]
            self.horizon = state["horizon"]
            self.feature_columns = state["feature_columns"]
            self.feature_scaler = state["feature_scaler"]
            self.target_scaler = state["target_scaler"]
            self.is_fitted = state["is_fitted"]
