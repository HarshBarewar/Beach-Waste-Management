"""
Time-Series Evaluation Metrics for BeachWaste AI.

Implements MAE, RMSE, WAPE, R-squared, step-by-step horizon errors,
and residual analysis for deep learning and baseline models.
"""
import numpy as np
from typing import Dict, Any, List

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Computes comprehensive evaluation metrics between true and predicted sequences.
    y_true shape: (N, horizon) or (N,)
    y_pred shape: (N, horizon) or (N,)
    """
    y_true = np.array(y_true, dtype=np.float64)
    y_pred = np.array(y_pred, dtype=np.float64)

    # Flatten for global metrics
    yt_flat = y_true.flatten()
    yp_flat = y_pred.flatten()

    residuals = yt_flat - yp_flat
    abs_errors = np.abs(residuals)
    sq_errors = residuals ** 2

    mae = float(np.mean(abs_errors))
    rmse = float(np.sqrt(np.mean(sq_errors)))

    # WAPE: sum(|y - y_hat|) / sum(y) * 100%
    sum_y = np.sum(np.abs(yt_flat))
    wape = float((np.sum(abs_errors) / max(sum_y, 1e-6)) * 100.0)

    # R-squared: 1 - SS_res / SS_tot
    ss_res = np.sum(sq_errors)
    ss_tot = np.sum((yt_flat - np.mean(yt_flat)) ** 2)
    r2 = float(1.0 - (ss_res / max(ss_tot, 1e-6)))

    # MAPE (with safe clipping to avoid divide-by-zero distortion)
    non_zero_mask = yt_flat > 1.0
    if np.any(non_zero_mask):
        mape = float(np.mean(np.abs((yt_flat[non_zero_mask] - yp_flat[non_zero_mask]) / yt_flat[non_zero_mask])) * 100.0)
    else:
        mape = 0.0

    # Step-by-step horizon errors (if multi-step)
    horizon_metrics = []
    if len(y_true.shape) > 1 and y_true.shape[1] > 1:
        horizon = y_true.shape[1]
        for step in range(horizon):
            step_true = y_true[:, step]
            step_pred = y_pred[:, step]
            step_res = step_true - step_pred
            step_mae = float(np.mean(np.abs(step_res)))
            step_rmse = float(np.sqrt(np.mean(step_res ** 2)))
            step_wape = float((np.sum(np.abs(step_res)) / max(np.sum(step_true), 1e-6)) * 100.0)
            horizon_metrics.append({
                "step_month": step + 1,
                "mae": round(step_mae, 2),
                "rmse": round(step_rmse, 2),
                "wape_pct": round(step_wape, 2)
            })

    # Residual summary
    residual_stats = {
        "mean_error": round(float(np.mean(residuals)), 2),
        "std_error": round(float(np.std(residuals)), 2),
        "min_error": round(float(np.min(residuals)), 2),
        "max_error": round(float(np.max(residuals)), 2),
    }

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "wape_pct": round(wape, 2),
        "r2": round(r2, 4),
        "mape_pct": round(mape, 2),
        "sample_count": int(len(yt_flat)),
        "horizon_breakdown": horizon_metrics,
        "residual_stats": residual_stats,
        "metric_explanation": {
            "wape": "Weighted Absolute Percentage Error (sum of errors divided by total actual waste; robust to zero or low waste months)",
            "mae": "Mean Absolute Error in kilograms",
            "rmse": "Root Mean Squared Error in kilograms (penalizes large outlier mistakes)",
            "r2": "Coefficient of determination (proportion of variance explained)"
        }
    }
