"""Evaluation helpers for the role classifier.

Usage:  python -m ml.evaluate     (re-scores saved artifacts on the test split)
"""
import os
import pickle

import numpy as np
import sklearn
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

from ml import augment, features


def _topk(proba: np.ndarray, y: np.ndarray, k: int = 3) -> float:
    top = np.argsort(-proba, axis=1)[:, :k]
    return float(np.mean([y[i] in top[i] for i in range(len(y))]))


def score(model, X, y) -> dict:
    proba = model.predict_proba(X)
    pred = proba.argmax(axis=1)
    return {
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "macro_f1": round(float(f1_score(y, pred, average="macro")), 4),
        "top3_accuracy": round(_topk(proba, y, 3), 4),
    }


def ece_score(y_true, proba, n_bins=10):
    # Pooled one-vs-rest ECE over all classes
    # Flatten everything
    y_true_ovr = np.zeros_like(proba)
    y_true_ovr[np.arange(len(y_true)), y_true] = 1
    
    y_true_flat = y_true_ovr.flatten()
    proba_flat = proba.flatten()
    
    prob_true, prob_pred = calibration_curve(y_true_flat, proba_flat, n_bins=n_bins)
    # compute counts in each bin to weight the ECE
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(proba_flat, bin_edges, right=True) - 1
    # fix edge case for exactly 0.0
    bin_indices[bin_indices == -1] = 0
    
    bin_counts = np.bincount(bin_indices, minlength=n_bins)
    valid_bins = bin_counts > 0
    
    # prob_true and prob_pred from calibration_curve only return for valid bins
    ece = np.sum(np.abs(prob_true - prob_pred) * bin_counts[valid_bins]) / len(y_true_flat)
    
    return float(ece), prob_true.tolist(), prob_pred.tolist()

def full_report(model, test_df, le, width: int) -> dict:
    X = features.to_matrix(test_df["skill_ids"], width)
    y = le.transform(test_df["role_family"])
    proba = model.predict_proba(X)
    pred = proba.argmax(axis=1)

    # Simulate a student typing only a few skills: keep ~40% of each posting.
    short_x, short_y = augment.drop_skills(test_df["skill_ids"].tolist(), y.tolist(),
                                           n_copies=1, keep_frac=(0.35, 0.45), seed=7)
    short_x, short_y = short_x[len(test_df):], np.array(short_y[len(test_df):])

    ece, prob_true, prob_pred = ece_score(y, proba, 10)
    
    # Calculate top_label_ece
    prob_max = proba.max(axis=1)
    y_true_top = (pred == y).astype(int)
    prob_true_top, prob_pred_top = calibration_curve(y_true_top, prob_max, n_bins=10)
    bin_edges = np.linspace(0.0, 1.0, 11)
    bin_indices = np.digitize(prob_max, bin_edges, right=True) - 1
    bin_indices[bin_indices == -1] = 0
    bin_counts = np.bincount(bin_indices, minlength=10)
    valid_bins = bin_counts > 0
    top_label_ece = float(np.sum(np.abs(prob_true_top - prob_pred_top) * bin_counts[valid_bins]) / len(y))

    try:
        import lightgbm
        lgb_ver = lightgbm.__version__
    except ImportError:
        lgb_ver = "unavailable"

    return {
        "test": score(model, X, y),
        "test_short_input": score(model, features.to_matrix(short_x, width), short_y),
        "majority_baseline_acc": round(float(np.mean(y == np.bincount(y).argmax())), 4),
        "per_class": classification_report(y, pred, target_names=list(le.classes_),
                                           output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y, pred).tolist(),
        "classes": list(le.classes_),
        "test_calibration": {
            "pooled_ovr_ece": round(ece, 4),
            "top_label_ece": round(top_label_ece, 4),
            "prob_true": prob_true,
            "prob_pred": prob_pred
        },
        "versions": {
            "scikit-learn": sklearn.__version__,
            "lightgbm": lgb_ver
        },
        "band_thresholds": {"Ready": 0.60, "Close": 0.30, "Not yet": 0.0},
        "data_release": "data-v4",
        "model_version": "model-v4",
        "rules_version": "rules-v2",
        "seed": 42
    }


def print_report(r: dict) -> None:
    print("\n=== Test results ===")
    print(f"Model: {r.get('model')}")
    print(f"Majority-class baseline accuracy: {r['majority_baseline_acc']:.3f}")
    for k in ("test", "test_short_input"):
        m = r[k]
        print(f"{k:17s} acc={m['accuracy']:.3f} macro-F1={m['macro_f1']:.3f} top3={m['top3_accuracy']:.3f}")
    print("\nPer-class F1:")
    for c in r["classes"]:
        pc = r["per_class"][c]
        print(f"  {c:30s} F1={pc['f1-score']:.3f}  n={int(pc['support'])}")


def main():
    from ml.train import ARTIFACTS_DIR, load_dataset, split
    with open(os.path.join(ARTIFACTS_DIR, "classifier.pkl"), "rb") as f:
        clf = pickle.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "label_encoder.pkl"), "rb") as f:
        le = pickle.load(f)
    width = features.n_features(features.load_vocab())
    df, _ = load_dataset()
    _, _, test = split(df)
    r = full_report(clf, test, le, width)
    print_report(r)
    
    metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
    if os.path.exists(metrics_path):
        import json
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        metrics.update(r) # r contains 'test', 'test_short_input', 'test_calibration', etc.
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
    else:
        import json
        with open(metrics_path, "w") as f:
            json.dump(r, f, indent=2)


if __name__ == "__main__":
    main()
