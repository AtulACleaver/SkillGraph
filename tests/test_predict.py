import os

import pytest

from ml import augment, features

ARTIFACTS = "artifacts"
HAVE_MODEL = os.path.exists(os.path.join(ARTIFACTS, "classifier.pkl"))


def test_to_matrix_multi_hot():
    X = features.to_matrix([[1, 3, 3], [], [2, 999]], width=5)
    assert X.shape == (3, 5)
    assert X[0].toarray().tolist() == [[0, 1, 0, 1, 0]]
    assert X[1].nnz == 0
    assert X[2].toarray().tolist() == [[0, 0, 1, 0, 0]]  # out-of-range id ignored


def test_augment_keeps_originals_and_labels():
    x, y = augment.drop_skills([[1, 2, 3, 4, 5, 6]], ["A"], n_copies=2)
    assert len(x) == 3 and y == ["A", "A", "A"]
    assert all(set(c) <= {1, 2, 3, 4, 5, 6} and len(c) >= 2 for c in x[1:])


@pytest.mark.skipif(not HAVE_MODEL, reason="run `python -m ml.train` first")
def test_predictor_end_to_end():
    from ml.predict import Predictor
    p = Predictor(ARTIFACTS)
    out = p.match(["python", "machine learning", "deep learning", "nlp", "not-a-real-skill-xyz"])
    assert len(out["matches"]) == 3
    assert abs(sum(m["probability"] for m in out["matches"])) <= 1.0001
    assert out["matches"][0]["role"] == "Data Science / ML"
    assert "not-a-real-skill-xyz" in out["unrecognized"]

    r = p.readiness(["selenium", "manual testing", "test cases"], "QA / Test")
    assert r["band"] in {"High", "Medium", "Low"}
    assert 0 <= r["probability"] <= 1 and 0 <= r["coverage"] <= 1
