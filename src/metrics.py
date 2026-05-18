"""
metrics.py — Evaluation metrics for essay scoring.
RMSE, MAE, Pearson Correlation, Quadratic Weighted Kappa (QWK)
"""

import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error, mean_absolute_error, cohen_kappa_score


def compute_rmse(y_true: list, y_pred: list) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def compute_mae(y_true: list, y_pred: list) -> float:
    """Mean Absolute Error."""
    return float(mean_absolute_error(y_true, y_pred))


def compute_pearson(y_true: list, y_pred: list) -> float:
    """Pearson Correlation Coefficient."""
    if len(set(y_true)) == 1 or len(set(y_pred)) == 1:
        return 0.0
    r, _ = pearsonr(y_true, y_pred)
    return float(r)


def compute_qwk(y_true: list, y_pred: list) -> float:
    """
    Quadratic Weighted Kappa (QWK) — the gold standard for essay scoring.
    Predictions are rounded to nearest integer before computing.
    """
    y_true_int = [int(round(y)) for y in y_true]
    y_pred_int = [int(round(y)) for y in y_pred]
    try:
        qwk = cohen_kappa_score(y_true_int, y_pred_int, weights="quadratic")
    except Exception:
        qwk = 0.0
    return float(qwk)


def compute_all_metrics(y_true: list, y_pred: list) -> dict:
    """Compute all evaluation metrics and return as a dict."""
    return {
        "RMSE": round(compute_rmse(y_true, y_pred), 4),
        "MAE": round(compute_mae(y_true, y_pred), 4),
        "Pearson_r": round(compute_pearson(y_true, y_pred), 4),
        "QWK": round(compute_qwk(y_true, y_pred), 4),
    }


def print_metrics(metrics: dict, model_name: str = "Model"):
    print(f"\n{'='*40}")
    print(f"  Evaluation Results: {model_name}")
    print(f"{'='*40}")
    for k, v in metrics.items():
        print(f"  {k:<15}: {v:.4f}")
    print(f"{'='*40}\n")


if __name__ == "__main__":
    # Quick test
    y_true = [2, 4, 6, 8, 10, 12]
    y_pred = [2, 4, 5, 9, 10, 11]
    metrics = compute_all_metrics(y_true, y_pred)
    print_metrics(metrics, "Demo Model")
