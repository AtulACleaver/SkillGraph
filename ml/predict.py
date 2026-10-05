import csv
import json

import numpy as np

from etl.paths import ARTIFACTS_DIR, TAXONOMY_DIR
from ml import features

_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = Predictor()
    return _predictor

class Predictor:
    def __init__(self):
        self.vocab = features.load_vocab(str(ARTIFACTS_DIR / "skill_vocab.json"))
        self.width = features.n_features(self.vocab)
        
        with open(ARTIFACTS_DIR / "model.json", "r") as f:
            model_data = json.load(f)
            
        self.classes = model_data["classes"]
        self.coef = np.array(model_data["coef"], dtype=np.float32)
        self.intercept = np.array(model_data["intercept"], dtype=np.float32)
        self.n_features_in = model_data["n_features"]
        
        with open(ARTIFACTS_DIR / "role_profiles.json", "r") as f:
            self.profiles = json.load(f)

        if self.width != self.n_features_in:
            raise ValueError(f"Vocab size {self.width} does not match model features {self.n_features_in}")
        
        classes_set = set(self.classes)
        profiles_set = set(self.profiles.keys())
        if classes_set != profiles_set:
            raise ValueError("Label classes do not match role_profiles keys")

        self.display_names: dict[str, str] = {}
        ac_path = ARTIFACTS_DIR / "skills_autocomplete.json"
        if ac_path.exists():
            try:
                with open(ac_path, "r", encoding="utf-8") as f:
                    for item in json.load(f):
                        self.display_names[item["name"].lower()] = item.get("display", item["name"].title())
            except (json.JSONDecodeError, OSError):
                pass
        overrides_path = TAXONOMY_DIR / "display_overrides.csv"
        if overrides_path.exists():
            try:
                with open(overrides_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    for row in reader:
                        if len(row) >= 2:
                            k, v = row[0].strip().lower(), row[1].strip()
                            if k and v:
                                self.display_names[k] = v
            except OSError:
                pass

    def get_display_name(self, name: str) -> str:
        s = name.lower().strip()
        return self.display_names.get(s, name.title() if not name.isupper() else name)

    def proba(self, vector):
        if isinstance(vector, np.ndarray):
            vec = vector
            if len(vec.shape) == 1:
                vec = vec.reshape(1, -1)
        else:
            # Assuming it's a list of IDs or list of names? "vector" could be list of int.
            # Convert to dense since we are only doing inference
            vec = np.zeros((1, self.width), dtype=np.float32)
            for i in set(vector):
                if 0 <= int(i) < self.width:
                    vec[0, int(i)] = 1.0

        if vec.sum() == 0:
            raise ValueError("All-zero vector")

        # Stable softmax
        logits = vec @ self.coef.T + self.intercept
        e_x = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = e_x / e_x.sum(axis=1, keepdims=True)
        return probs[0]


def band_for(p: float, coverage: float = 1.0) -> str:
    if p >= 0.60:
        p_band = 2 # Ready
    elif p >= 0.30:
        p_band = 1 # Close
    else:
        p_band = 0 # Not yet
        
    if coverage >= 0.20:
        c_band = 2
    elif coverage >= 0.10:
        c_band = 1
    else:
        c_band = 0
        
    final_band = min(p_band, c_band)
    if final_band == 2: return "Ready"
    elif final_band == 1: return "Close"
    return "Not yet"

def predict_roles(vector) -> list[dict]:
    p = get_predictor()
    prob = p.proba(vector)
    order = np.argsort(-prob)
    roles = [p.classes[i] for i in order]
    return [{"role": str(r), "probability": round(float(prob[j]), 4)} for r, j in zip(roles, order)]

def readiness(vector, desired_role: str) -> dict:
    p = get_predictor()
    if desired_role not in p.profiles:
        raise ValueError(f"Unknown role: {desired_role}")
    
    prob_array = p.proba(vector)
    cls_idx = p.classes.index(desired_role)
    prob = float(prob_array[cls_idx])
    
    top = list(dict.fromkeys(s.lower() for s in p.profiles[desired_role].get("top_skills", [])[:20]))
    
    if isinstance(vector, np.ndarray):
        if len(vector.shape) == 2:
            indices = np.where(vector[0] > 0)[0]
        else:
            indices = np.where(vector > 0)[0]
    else:
        indices = vector
        
    have = {p.vocab[int(i)].lower() for i in indices if 0 <= int(i) < p.width}
    covered = [p.get_display_name(s) for s in top if s in have]
    coverage = len(covered) / len(top) if top else 0.0
    
    return {
        "probability": round(prob, 4),
        "band": band_for(prob, coverage),
        "coverage": round(coverage, 4),
        "covered": covered,
        "missing_count": len(top) - len(covered),
    }

def delta_readiness(vector, desired_role: str, candidate_skill_id: int) -> float:
    p = get_predictor()
    if desired_role not in p.profiles:
        raise ValueError(f"Unknown role: {desired_role}")
        
    if isinstance(vector, np.ndarray):
        if len(vector.shape) == 2:
            if vector[0, candidate_skill_id] > 0: return 0.0
        else:
            if vector[candidate_skill_id] > 0: return 0.0
    else:
        if candidate_skill_id in vector: return 0.0
        
    base_prob = readiness(vector, desired_role)["probability"]
    
    if isinstance(vector, np.ndarray):
        new_vec = vector.copy()
        if len(new_vec.shape) == 2:
            new_vec[0, candidate_skill_id] = 1
        else:
            new_vec[candidate_skill_id] = 1
    else:
        new_vec = list(vector) + [candidate_skill_id]
        
    new_prob = readiness(new_vec, desired_role)["probability"]
    return max(0.0, new_prob - base_prob)
