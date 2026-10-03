"""Inference helpers used by the API.

    from ml.predict import Predictor
    p = Predictor("artifacts")
    p.match(["python", "sql", "power bi"])            # top-3 roles
    p.readiness(["python", "sql"], "Data / BI Analyst")
"""
import json
import os
import pickle

import numpy as np

from ml import features

BANDS = ((0.60, "High"), (0.30, "Medium"), (0.0, "Low"))


def band_for(p: float) -> str:
    return next(name for cut, name in BANDS if p >= cut)


class Predictor:
    def __init__(self, artifacts_dir: str = "artifacts"):
        self.vocab = features.load_vocab(os.path.join(artifacts_dir, "skill_vocab.json"))
        self.width = features.n_features(self.vocab)
        self.name_to_id = {name.lower(): i + 1 for i, name in enumerate(self.vocab)}
        with open(os.path.join(artifacts_dir, "classifier.pkl"), "rb") as f:
            self.clf = pickle.load(f)
        with open(os.path.join(artifacts_dir, "label_encoder.pkl"), "rb") as f:
            self.le = pickle.load(f)
        with open(os.path.join(artifacts_dir, "role_profiles.json")) as f:
            self.profiles = json.load(f)

    # -- skill resolution -------------------------------------------------
    def resolve(self, skills: list[str]) -> tuple[list[int], list[str]]:
        """Map user-typed names to skill IDs. Returns (ids, unrecognized)."""
        ids, unknown = [], []
        for s in skills:
            i = self.name_to_id.get(str(s).strip().lower())
            if i is None:
                try:  # alias + fuzzy matching from the ETL module
                    from etl.normalize import normalize_skill
                    i = normalize_skill(s)
                except Exception:
                    i = None
            if i is not None and 0 < i < self.width:
                ids.append(i)
            else:
                unknown.append(s)
        return sorted(set(ids)), unknown

    def _proba(self, ids: list[int]) -> np.ndarray:
        return self.clf.predict_proba(features.to_matrix([ids], self.width))[0]

    # -- public API -------------------------------------------------------
    def match(self, skills: list[str], top_k: int = 3) -> dict:
        ids, unknown = self.resolve(skills)
        if not ids:
            return {"matches": [], "unrecognized": unknown}
        p = self._proba(ids)
        order = np.argsort(-p)[:top_k]
        roles = self.le.inverse_transform(self.clf.classes_[order])
        return {
            "matches": [{"role": str(r), "probability": round(float(p[j]), 4)} for r, j in zip(roles, order)],
            "unrecognized": unknown,
        }

    def readiness(self, skills: list[str], desired_role: str) -> dict:
        ids, _ = self.resolve(skills)
        prob = 0.0
        if ids:
            p = self._proba(ids)
            cls = int(self.le.transform([desired_role])[0])
            prob = float(p[list(self.clf.classes_).index(cls)])
        top = list(dict.fromkeys(s.lower() for s in self.profiles.get(desired_role, {}).get("top_skills", [])))
        have = {self.vocab[i - 1].lower() for i in ids}
        covered = [s for s in top if s in have]
        return {
            "probability": round(prob, 4),
            "band": band_for(prob),
            "coverage": round(len(covered) / len(top), 4) if top else 0.0,
            "covered": covered,
            "missing_count": len(top) - len(covered),
        }
