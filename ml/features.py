"""Feature building for the role classifier.

Each posting (or user) is a bag of canonical skill IDs. We encode it as a
sparse multi-hot vector. Skill IDs are 1-based (see etl/normalize.py), and
artifacts/skill_vocab.json is a list where vocab[i] is the name of ID i+1.
Column 0 is therefore unused, and the feature width is len(vocab) + 1.
"""
import json
import os

import numpy as np
from scipy import sparse

VOCAB_PATH = os.path.join("artifacts", "skill_vocab.json")


def load_vocab(path: str = VOCAB_PATH) -> list[str]:
    with open(path) as f:
        vocab = json.load(f)
    if isinstance(vocab, dict):  # fixture format {name: id}
        out = [""] * (max(vocab.values()) + 1)
        for name, i in vocab.items():
            out[i] = name
        return out[1:]
    return vocab


def n_features(vocab: list[str]) -> int:
    return len(vocab) + 1


def to_matrix(skill_id_lists, width: int) -> sparse.csr_matrix:
    """Multi-hot encode an iterable of skill-id lists into a CSR matrix."""
    skill_id_lists = list(skill_id_lists)
    rows, cols = [], []
    for r, ids in enumerate(skill_id_lists):
        for i in set(int(x) for x in ids):
            if 0 < i < width:
                rows.append(r)
                cols.append(i)
    data = np.ones(len(rows), dtype=np.float32)
    shape = (len(skill_id_lists), width)
    return sparse.csr_matrix((data, (rows, cols)), shape=shape, dtype=np.float32)
