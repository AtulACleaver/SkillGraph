"""Feature building for the role classifier.

Each posting (or user) is a bag of canonical skill IDs. We encode it as a
sparse multi-hot vector. Skill IDs are 0-based, and
artifacts/skill_vocab.json is a list where vocab[i] is the name of ID i.
The feature width is len(vocab).
"""
import json
import os

import numpy as np
from scipy import sparse


def load_vocab(path: str | None = None) -> list[str]:
    if path is None:
        path = os.path.join(os.environ.get("ARTIFACTS_DIR", "artifacts"), "skill_vocab.json")
    with open(path) as f:
        vocab = json.load(f)
    return vocab


def n_features(vocab: list[str]) -> int:
    return len(vocab)


def to_matrix(skill_id_lists, width: int) -> sparse.csr_matrix:
    """Multi-hot encode an iterable of skill-id lists into a CSR matrix."""
    skill_id_lists = list(skill_id_lists)
    rows, cols = [], []
    for r, ids in enumerate(skill_id_lists):
        for i in {int(x) for x in ids}:
            if 0 <= i < width:
                rows.append(r)
                cols.append(i)
    data = np.ones(len(rows), dtype=np.float32)
    shape = (len(skill_id_lists), width)
    return sparse.csr_matrix((data, (rows, cols)), shape=shape, dtype=np.float32)
