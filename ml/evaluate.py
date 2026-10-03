"""Evaluation helpers for the role classifier.

Usage:  python -m ml.evaluate     (re-scores saved artifacts on the test split)
"""
import json
import os
import pickle

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

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


def full_report(model, test_df, le, width: int) -> dict:
    X = features.to_matrix(test_df["skill_ids"], width)
    y = le.transform(test_df["role_family"])
    pred = model.predict_proba(X).argmax(axis=1)

    # Simulate a student typing only a few skills: keep ~40% of each posting.
    short_x, short_y = augment.drop_skills(test_df["skill_ids"].tolist(), y.tolist(),
                                           n_copies=1, keep_frac=(0.35, 0.45), seed=7)
    short_x, short_y = short_x[len(test_df):], np.array(short_y[len(test_df):])

    return {
        "test": score(model, X, y),
        "test_short_input": score(model, features.to_matrix(short_x, width), short_y),
        "majority_baseline_acc": round(float(np.mean(y == np.bincount(y).argmax())), 4),
        "per_class": classification_report(y, pred, target_names=list(le.classes_),
                                           output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y, pred).tolist(),
        "classes": list(le.classes_),
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
    _, _, test = split(load_dataset())
    r = full_report(clf, test, le, width)
    print_report(r)


if __name__ == "__main__":
    main()
