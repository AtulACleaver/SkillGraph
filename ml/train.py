"""Train the role-family classifier.

Usage:  python -m ml.train

Reads   data/dataset.parquet, artifacts/skill_vocab.json
Writes  artifacts/classifier.pkl, artifacts/label_encoder.pkl,
        artifacts/role_profiles.json, artifacts/metrics.json
"""
import json
import os
import pickle
import time
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from etl.stats import write_stage_stats
from ml import augment, evaluate, features

DATASET_PATH = os.path.join("data", "dataset.parquet")
ARTIFACTS_DIR = "artifacts"
SEED = 42


def load_dataset(path: str = DATASET_PATH) -> tuple[pd.DataFrame, int]:
    df = pd.read_parquet(path)
    initial_len = len(df)
    df = df[df["skill_ids"].apply(lambda x: x is not None and len(x) > 0)]
    dropped = initial_len - len(df)
    if dropped > 0:
        print(f"Dropped {dropped} rows with no skill IDs")
    df = df.dropna(subset=["role_family"]).reset_index(drop=True)
    return df, dropped


def split(df: pd.DataFrame, seed: int = SEED):
    """Stratified 70 / 15 / 15 train / val / test split (deterministic)."""
    train, rest = train_test_split(df, test_size=0.30, stratify=df["role_family"], random_state=seed)
    val, test = train_test_split(rest, test_size=0.50, stratify=rest["role_family"], random_state=seed)
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)


def _candidate_models(n_classes: int) -> dict:
    models = {
        "logreg": LogisticRegression(max_iter=3000, C=1.0, class_weight="balanced"),
    }
    try:
        import lightgbm as lgb
        models["lightgbm"] = lgb.LGBMClassifier(
            objective="multiclass", num_class=n_classes, n_estimators=400,
            learning_rate=0.05, num_leaves=31, min_child_samples=10,
            class_weight="balanced", random_state=SEED, verbose=-1,
        )
    except Exception as e:  # noqa: BLE001
        print(f"[warn] LightGBM unavailable, skipping it: {type(e).__name__}: {str(e)[:120]}")
    return models


def build_role_profiles(df: pd.DataFrame, vocab: list[str], top_k: int = 20) -> dict:
    profiles = {}
    for role, g in df.groupby("role_family"):
        counts = Counter(i for ids in g["skill_ids"] for i in ids)
        n = len(g)
        top = [(vocab[int(i)], c / n) for i, c in counts.most_common(top_k) if 0 <= int(i) < len(vocab)]
        profiles[role] = {
            "n_postings": int(n),
            "top_skills": [name for name, _ in top],
            "skill_freq": [[name, round(f, 4)] for name, f in top],
        }
    return dict(sorted(profiles.items(), key=lambda kv: -kv[1]["n_postings"]))


def main():
    t0 = time.time()
    vocab = features.load_vocab()
    width = features.n_features(vocab)
    df, dropped_rows = load_dataset()
    print(f"Loaded {len(df):,} postings, {df.role_family.nunique()} role families, vocab={len(vocab)}")

    train, val, test = split(df)
    le = LabelEncoder().fit(df["role_family"])

    aug_x, aug_y = augment.drop_skills(train["skill_ids"].tolist(), train["role_family"].tolist())
    X_tr = features.to_matrix(aug_x, width)
    y_tr = le.transform(aug_y)
    X_val = features.to_matrix(val["skill_ids"], width)
    y_val = le.transform(val["role_family"])
    print(f"Train {len(train):,} (augmented to {X_tr.shape[0]:,}) | val {len(val):,} | test {len(test):,}")
    majority_val_acc = float(np.mean(y_val == np.bincount(y_val).argmax()))
    print(f"Majority baseline (val) acc={majority_val_acc:.4f}")

    results, fitted = {}, {}
    for name, model in _candidate_models(len(le.classes_)).items():
        s = time.time()
        model.fit(X_tr, y_tr)
        m = evaluate.score(model, X_val, y_val)
        results[name], fitted[name] = m, model
        print(f"  {name:9s} val macro-F1={m['macro_f1']:.3f} acc={m['accuracy']:.3f} "
              f"top3={m['top3_accuracy']:.3f}  ({time.time() - s:.1f}s)")

    best = "logreg"
    if "lightgbm" in results:
        diff = results["lightgbm"]["macro_f1"] - results["logreg"]["macro_f1"]
        if diff > 0.03:
            best = "lightgbm"
            
    clf = fitted[best]
    print(f"Selected model: {best}")

    report = evaluate.full_report(clf, test, le, width)
    report["model"] = best
    report["val"] = results
    
    # Compute test scores for both models
    X_test = features.to_matrix(test["skill_ids"], width)
    y_test = le.transform(test["role_family"])
    report["test_scores_both_models"] = {}
    for name, m_obj in fitted.items():
        report["test_scores_both_models"][name] = evaluate.score(m_obj, X_test, y_test)
        
    report["n_train_raw"], report["n_train_aug"] = len(train), int(X_tr.shape[0])
    report["n_dropped_no_skills"] = dropped_rows
    report["n_val"], report["n_test"] = len(val), len(test)
    report["built_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with open(os.path.join(ARTIFACTS_DIR, "classifier.pkl"), "wb") as f:
        pickle.dump(clf, f)
    with open(os.path.join(ARTIFACTS_DIR, "label_encoder.pkl"), "wb") as f:
        pickle.dump(le, f)
    with open(os.path.join(ARTIFACTS_DIR, "role_profiles.json"), "w") as f:
        json.dump(build_role_profiles(train, vocab), f, indent=2)
    metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(report, f, indent=2)

    evaluate.print_report(report)
    elapsed = time.time() - t0
    print(f"Artifacts written to {ARTIFACTS_DIR}/ in {elapsed:.1f}s")

    write_stage_stats(
        stage="train",
        rows_in=len(df) + dropped_rows,
        rows_out=len(df),
        drops_by_reason={"no_skill_ids": dropped_rows},
        elapsed_seconds=elapsed,
        output_files=[
            os.path.join(ARTIFACTS_DIR, "classifier.pkl"),
            os.path.join(ARTIFACTS_DIR, "label_encoder.pkl"),
            os.path.join(ARTIFACTS_DIR, "role_profiles.json"),
            os.path.join(ARTIFACTS_DIR, "metrics.json"),
        ],
    )


if __name__ == "__main__":
    main()
