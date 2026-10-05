import hashlib
import json
import pickle
import time

import numpy as np
import pandas as pd

from etl.paths import ARTIFACTS_DIR
from etl.stats import write_stage_stats


def softmax(x):
    e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return e_x / e_x.sum(axis=1, keepdims=True)

def export_model():
    with open(ARTIFACTS_DIR / "classifier.pkl", "rb") as f:
        clf = pickle.load(f)
        
    with open(ARTIFACTS_DIR / "label_encoder.pkl", "rb") as f:
        le = pickle.load(f)

    with open(ARTIFACTS_DIR / "skill_vocab.json", "rb") as f:
        vocab_bytes = f.read()
    
    vocab_sha256 = hashlib.sha256(vocab_bytes).hexdigest()

    model_json = {
        "classes": le.classes_.tolist(),
        "coef": clf.coef_.tolist(),
        "intercept": clf.intercept_.tolist(),
        "n_features": clf.n_features_in_,
        "vocab_sha256": vocab_sha256,
        "source": "model-v3",
    }
    
    with open(ARTIFACTS_DIR / "model.json", "w") as f:
        json.dump(model_json, f, indent=2)
        
    # Assert parity
    np.random.seed(42)
    # Generate 200 random binary vectors
    X = np.random.binomial(1, 0.1, size=(200, clf.n_features_in_)).astype(np.float32)
    
    # Original predict_proba
    original_proba = clf.predict_proba(X)
    
    # Reconstructed predict_proba
    coef = np.array(model_json["coef"], dtype=np.float32)
    intercept = np.array(model_json["intercept"], dtype=np.float32)
    logits = X @ coef.T + intercept
    reconstructed_proba = softmax(logits)
    
    max_diff = np.max(np.abs(original_proba - reconstructed_proba))
    print(f"Model parity max diff: {max_diff}")
    assert max_diff < 1e-9, f"Max diff too high: {max_diff}"

def export_rules():
    rules_df = pd.read_parquet(ARTIFACTS_DIR / "rules.parquet")
    
    rules_list = []
    for _, row in rules_df.iterrows():
        rules_list.append({
            "antecedent": [int(x) for x in row["antecedent"]],
            "consequent": [int(x) for x in row["consequent"]],
            "support": float(row["support"]),
            "confidence": float(row["confidence"]),
            "lift": float(row["lift"]),
        })
        
    rules_json = {
        "rules": rules_list,
        "source": "rules-v1"
    }
    
    with open(ARTIFACTS_DIR / "rules.json", "w") as f:
        json.dump(rules_json, f, indent=2)

def main():
    t0 = time.time()
    export_model()
    export_rules()
    elapsed = time.time() - t0
    write_stage_stats(
        stage="export",
        rows_in=2,
        rows_out=2,
        drops_by_reason={},
        elapsed_seconds=elapsed,
        output_files=[ARTIFACTS_DIR / "model.json", ARTIFACTS_DIR / "rules.json"],
    )

if __name__ == "__main__":
    main()
