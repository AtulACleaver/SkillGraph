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
            "skills": ["python", "sql", "pandas"],
            "desired_role": "Data / BI Analyst"
        })
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert abs(data1["readiness"]["probability"] - 0.2560) < 1e-4
        assert data1["readiness"]["band"] == "Not yet"
        assert data1["match"]["matches"][0]["role"] == "Backend"
        assert abs(data1["match"]["matches"][0]["probability"] - 0.4018) < 1e-4

        # Persona 2
        resp2 = client.post("/api/analyze", json={
            "skills": ["java", "spring boot", "mysql", "docker"],
            "desired_role": "Backend"
        })
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert abs(data2["readiness"]["probability"] - 0.7202) < 1e-4
        assert data2["readiness"]["band"] == "Close"

        # Persona 3
        resp3 = client.post("/api/analyze", json={
            "skills": ["react", "javascript", "html", "css"],
            "desired_role": "Full Stack"
        })
        assert resp3.status_code == 200
        data3 = resp3.json()
        assert data3["match"]["matches"][0]["role"] == "Frontend"
        assert abs(data3["match"]["matches"][0]["probability"] - 0.7313) < 1e-4
        assert abs(data3["readiness"]["probability"] - 0.2459) < 1e-4
        assert data3["readiness"]["band"] == "Not yet"

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
