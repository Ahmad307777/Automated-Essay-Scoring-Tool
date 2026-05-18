"""
utils.py — Shared helper utilities for the Essay Scoring system.
"""

import os
import json
import random
import numpy as np
import torch


# ─── Score Ranges per ASAP Essay Set ────────────────────────────────────────
ASAP_SCORE_RANGES = {
    1: (2, 12),
    2: (1, 6),
    3: (0, 3),
    4: (0, 3),
    5: (0, 4),
    6: (0, 4),
    7: (0, 30),
    8: (0, 60),
}


def normalize_score(score: float, essay_set: int) -> float:
    """Normalize a raw score to [0, 1] based on the ASAP essay set range."""
    lo, hi = ASAP_SCORE_RANGES.get(essay_set, (0, 10))
    if hi == lo:
        return 0.0
    return (score - lo) / (hi - lo)


def denormalize_score(norm_score: float, essay_set: int) -> float:
    """Convert a normalized [0,1] score back to the original scale."""
    lo, hi = ASAP_SCORE_RANGES.get(essay_set, (0, 10))
    return norm_score * (hi - lo) + lo


def set_seed(seed: int = 42):
    """Fix random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> torch.device:
    """Return CUDA if available, else CPU."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Device] Using: {device}")
    return device


def save_json(obj: dict, path: str):
    def sanitize(v):
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            return 0.0  # Or None/null if preferred, but 0.0 is safer for metrics
        if isinstance(v, dict):
            return {k: sanitize(v2) for k, v2 in v.items()}
        if isinstance(v, list):
            return [sanitize(v2) for v2 in v]
        return v

    sanitized_obj = sanitize(obj)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sanitized_obj, f, indent=2)
    print(f"[Saved] {path}")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
