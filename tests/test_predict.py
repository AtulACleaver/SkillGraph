import json
import os

import numpy as np
import pandas as pd
import pytest

from ml import augment, features, predict

ARTIFACTS = os.environ.get("ARTIFACTS_DIR", "artifacts")
HAVE_MODEL = os.path.exists(os.path.join(ARTIFACTS, "classifier.pkl"))

def test_to_matrix_multi_hot():
    X = features.to_matrix([[0, 2, 2], [], [1, 999]], width=5)
    assert X.shape == (3, 5)
    assert X[0].toarray().tolist() == [[1, 0, 1, 0, 0]]
    assert X[1].nnz == 0
    assert X[2].toarray().tolist() == [[0, 1, 0, 0, 0]]

def test_augment_keeps_originals_and_labels():
    x, y = augment.drop_skills([[1, 2, 3, 4, 5, 6]], ["A"], n_copies=2)
    assert len(x) == 3 and y == ["A", "A", "A"]
    assert all(set(c) <= {1, 2, 3, 4, 5, 6} and len(c) >= 2 for c in x[1:])

@pytest.mark.skipif(not HAVE_MODEL, reason="run `python -m ml.train` first")
def test_predictor_end_to_end():
    p = predict.get_predictor()
    
    name_to_id = {v.lower(): i for i, v in enumerate(p.vocab)}
    
    vec = features.to_matrix([[name_to_id.get(s, -1) for s in ["python", "machine learning", "deep learning", "nlp"]]], p.width)
    out = predict.predict_roles(vec.toarray()[0])
    
    assert len(out) == len(p.le.classes_)
    assert abs(sum(m["probability"] for m in out)) <= 1.0001
    assert out[0]["probability"] >= out[-1]["probability"]
    assert out[0]["role"] == "Data Science / ML"

    with pytest.raises(ValueError):
        predict.predict_roles(np.zeros(p.width))

    r = predict.readiness(vec.toarray()[0], "QA / Test")
    assert r["band"] in {"Ready", "Close", "Not yet"}
    assert 0 <= r["probability"] <= 1 and 0 <= r["coverage"] <= 1

    with pytest.raises(ValueError):
        predict.readiness(vec.toarray()[0], "Unknown Role")

@pytest.mark.skipif(not HAVE_MODEL, reason="run `python -m ml.train` first")
def test_predictor_load_time_checks(monkeypatch):
    # Mock json load for vocab length check
    original_n_features = features.n_features
    def mock_n_features(v): return original_n_features(v) + 1
    monkeypatch.setattr(features, "n_features", mock_n_features)
    with pytest.raises(ValueError, match="Vocab size"):
        predict.Predictor()
    monkeypatch.undo()

    # Mock json load for profiles
    original_json_load = json.load
    def mock_json_load(f):
        res = original_json_load(f)
        if isinstance(res, dict) and "Data Science / ML" in res:
            res["Fake Role"] = res["Data Science / ML"]
        return res
    monkeypatch.setattr(json, "load", mock_json_load)
    with pytest.raises(ValueError, match="Label classes do not match"):
        predict.Predictor()
    monkeypatch.undo()

@pytest.mark.skipif(not HAVE_MODEL, reason="run `python -m ml.train` first")
@pytest.mark.skipif(os.environ.get("CI") == "true", reason="Real-artifact tests skip in CI")
def test_matrix_round_trip():
    import etl.normalize as norm
    p = predict.get_predictor()
    
    dataset_df = pd.read_parquet("data/dataset.parquet")
    clean_df = pd.read_parquet("data/clean.parquet")
    
    dataset_df = dataset_df[dataset_df["skill_ids"].apply(lambda x: x is not None and len(x) > 0)]
    
    clean_df['posting_id'] = clean_df.apply(lambda r: str(r.get('jobId', r.name)), axis=1)
    
    merged = dataset_df.merge(clean_df, on='posting_id', how='left')
    if merged['tagsAndSkills'].isnull().any():
        pytest.fail("Join lost dataset rows")
        
    sample = merged.sample(n=500, random_state=42)
    
    mismatches = 0
    examples = []
    
    for _, row in sample.iterrows():
        skills_str = row['tagsAndSkills']
        raw_list = [t.strip() for t in str(skills_str).split(',') if t.strip()]
        
        vec, _ = norm.skills_to_vector(raw_list)
        serve_indices = set(np.where(vec > 0)[0])
        
        train_vec = features.to_matrix([row['skill_ids']], p.width).toarray()[0]
        train_indices = set(np.where(train_vec > 0)[0])
        
        if serve_indices != train_indices:
            mismatches += 1
            if len(examples) < 5:
                examples.append(f"Row {row['posting_id']}: serve {serve_indices} vs train {train_indices}")
                
    if mismatches > 0:
        pytest.fail(f"{mismatches} mismatches found. Examples:\n" + "\n".join(examples))
