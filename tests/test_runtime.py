import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", "artifacts")

@pytest.mark.skipif(not os.path.exists(os.path.join(ARTIFACTS_DIR, "classifier.pkl")), reason="Needs classifier.pkl")
def test_parity():
    # Parity is already asserted during export_runtime.py execution.
    # To test here, we could run the same logic or just rely on export_runtime.py.
    # The requirement says: "parity against classifier.pkl, skipped if the pkl is missing".
    import json
    import pickle

    import numpy as np
    
    with open(os.path.join(ARTIFACTS_DIR, "classifier.pkl"), "rb") as f:
        clf = pickle.load(f)
        
    with open(os.path.join(ARTIFACTS_DIR, "model.json"), "r") as f:
        model_json = json.load(f)
        
    np.random.seed(42)
    X = np.random.binomial(1, 0.1, size=(200, clf.n_features_in_)).astype(np.float32)
    
    original_proba = clf.predict_proba(X)
    
    coef = np.array(model_json["coef"], dtype=np.float32)
    intercept = np.array(model_json["intercept"], dtype=np.float32)
    logits = X @ coef.T + intercept
    e_x = np.exp(logits - np.max(logits, axis=1, keepdims=True))
    reconstructed_proba = e_x / e_x.sum(axis=1, keepdims=True)
    
    max_diff = np.max(np.abs(original_proba - reconstructed_proba))
    assert max_diff < 1e-9

def test_slim_imports():
    script = """
import sys
import api.main
banned = ['pandas', 'sklearn', 'scipy', 'pyarrow']
found = [m for m in banned if m in sys.modules]
if found:
    print("Found banned modules:", found)
    sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, f"Banned modules imported: {result.stdout}"

def test_analyze_personas():
    with TestClient(app) as client:
        # Persona 1
        resp1 = client.post("/api/analyze", json={
            "skills": ["sql", "excel", "power bi", "tableau"],
            "desired_role": "Data / BI Analyst"
        })
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["match"]["matches"][0]["role"] == "Data / BI Analyst"
        assert abs(data1["match"]["matches"][0]["probability"] - 0.9733) < 1e-4
        assert abs(data1["readiness"]["probability"] - 0.9733) < 1e-4
        assert data1["readiness"]["band"] == "Close"

        # Persona 2
        resp2 = client.post("/api/analyze", json={
            "skills": ["java", "spring boot", "mysql", "docker"],
            "desired_role": "Backend"
        })
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert abs(data2["readiness"]["probability"] - 0.7520) < 1e-4
        assert data2["readiness"]["band"] == "Close"

        # Persona 3
        resp3 = client.post("/api/analyze", json={
            "skills": ["react", "javascript", "html", "css"],
            "desired_role": "Full Stack"
        })
        assert resp3.status_code == 200
        data3 = resp3.json()
        assert data3["match"]["matches"][0]["role"] == "Frontend"
        assert abs(data3["match"]["matches"][0]["probability"] - 0.7369) < 1e-4
        assert abs(data3["readiness"]["probability"] - 0.2395) < 1e-4
        assert data3["readiness"]["band"] == "Not yet"

        # Persona 4 (known limitation: pandas sparse in training data)
        resp4 = client.post("/api/analyze", json={
            "skills": ["python", "sql", "pandas"],
            "desired_role": "Data / BI Analyst"
        })
        assert resp4.status_code == 200
        data4 = resp4.json()
        assert data4["match"]["matches"][0]["role"] == "Backend"
        assert abs(data4["match"]["matches"][0]["probability"] - 0.4906) < 1e-4
        assert abs(data4["readiness"]["probability"] - 0.1080) < 1e-4
        assert data4["readiness"]["band"] == "Not yet"

def test_400_validations():
    with TestClient(app) as client:
        resp_empty = client.post("/api/match", json={"skills": []})
        assert resp_empty.status_code == 400

        resp_unknown = client.post("/api/match", json={"skills": ["foo"]})
        assert resp_unknown.status_code == 400

        resp_role = client.post("/api/readiness", json={"skills": ["python"], "desired_role": "Fake Role"})
        assert resp_role.status_code == 400

        resp_too_many = client.post("/api/match", json={"skills": [f"skill{i}" for i in range(35)]})
        assert resp_too_many.status_code == 400
        
        resp_too_long = client.post("/api/match", json={"skills": ["a" * 65]})
        assert resp_too_long.status_code == 400


def test_personas_zero_junk():
    from scripts.persona_check import check_personas
    junk_count = check_personas()
    assert junk_count == 0


@pytest.mark.skipif(not os.path.exists("data/dataset.parquet"), reason="Needs data/dataset.parquet")
def test_serving_path_evaluation():
    import json
    import pickle

    import numpy as np
    from sklearn.metrics import accuracy_score, f1_score

    from etl.normalize import load_vocab, skills_to_vector
    from ml.predict import predict_roles
    from ml.train import load_dataset, split

    vocab_path = os.path.join(ARTIFACTS_DIR, "skill_vocab.json")
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    load_vocab(vocab)

    df, _ = load_dataset()
    _, _, test = split(df)

    with open(os.path.join(ARTIFACTS_DIR, "classifier.pkl"), "rb") as f:
        clf = pickle.load(f)
    with open(os.path.join(ARTIFACTS_DIR, "label_encoder.pkl"), "rb") as f:
        le = pickle.load(f)

    y_true = []
    y_pred_serving = []
    y_pred_clf = []

    for _, row in test.iterrows():
        skill_names = [vocab[int(i)] for i in row["skill_ids"]]
        vec, _ = skills_to_vector(skill_names)
        res = predict_roles(vec)
        y_pred_serving.append(res[0]["role"])

        vec_matrix = np.zeros((1, len(vocab)))
        for i in row["skill_ids"]:
            vec_matrix[0, i] = 1.0
        clf_pred = le.inverse_transform(clf.predict(vec_matrix))[0]
        y_pred_clf.append(clf_pred)
        y_true.append(row["role_family"])

    acc = accuracy_score(y_true, y_pred_serving)
    macro_f1 = f1_score(y_true, y_pred_serving, average="macro")

    with open(os.path.join(ARTIFACTS_DIR, "metrics.json"), "r", encoding="utf-8") as f:
        metrics = json.load(f)

    expected_acc = metrics["test"]["accuracy"]
    expected_f1 = metrics["test"]["macro_f1"]

    assert round(acc, 4) == round(expected_acc, 4)
    assert round(macro_f1, 4) == round(expected_f1, 4)

    np.random.seed(42)
    sample_indices = np.random.choice(len(test), size=50, replace=False)
    for idx in sample_indices:
        assert y_pred_serving[idx] == y_pred_clf[idx]

