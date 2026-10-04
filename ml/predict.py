import json
import os
import pickle

import numpy as np

from ml import features

_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = Predictor()
    return _predictor

class Predictor:
    def __init__(self):
        artifacts_dir = os.environ.get("ARTIFACTS_DIR", "artifacts")
        self.vocab = features.load_vocab(os.path.join(artifacts_dir, "skill_vocab.json"))
        self.width = features.n_features(self.vocab)
        
        with open(os.path.join(artifacts_dir, "classifier.pkl"), "rb") as f:
            self.clf = pickle.load(f)
        with open(os.path.join(artifacts_dir, "label_encoder.pkl"), "rb") as f:
            self.le = pickle.load(f)
        with open(os.path.join(artifacts_dir, "role_profiles.json")) as f:
            self.profiles = json.load(f)

        if self.width != self.clf.n_features_in_:
            raise ValueError(f"Vocab size {self.width} does not match model features {self.clf.n_features_in_}")
        
        # classes can be numpy array or list
        classes_set = set(self.le.classes_)
        profiles_set = set(self.profiles.keys())
        if classes_set != profiles_set:
            raise ValueError("Label classes do not match role_profiles keys")

    def proba(self, vector):
        if isinstance(vector, np.ndarray):
            vec = vector
            if len(vec.shape) == 1:
                vec = vec.reshape(1, -1)
        else:
            # Assuming it's a list of IDs or list of names? "vector" could be list of int.
            # "ml/predict.py takes vectors" - let's convert list of IDs to matrix
            vec = features.to_matrix([vector], self.width)

        if vec.sum() == 0:
            raise ValueError("All-zero vector")

        return self.clf.predict_proba(vec)[0]


def band_for(p: float, coverage: float = 1.0) -> str:
    # "Start at Ready >= 0.60, Close 0.30 to 0.60, Not yet below 0.30."
    # "Coverage = share of the role's top 20 skills the user has. Band = the lower of the two."
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
    roles = p.le.inverse_transform(p.clf.classes_[order])
    return [{"role": str(r), "probability": round(float(prob[j]), 4)} for r, j in zip(roles, order)]

def readiness(vector, desired_role: str) -> dict:
    p = get_predictor()
    if desired_role not in p.profiles:
        raise ValueError(f"Unknown role: {desired_role}")
    
    prob_array = p.proba(vector)
    cls = int(p.le.transform([desired_role])[0])
    prob = float(prob_array[list(p.clf.classes_).index(cls)])
    
    # "share of the role's top 20 skills the user has"
    top = list(dict.fromkeys(s.lower() for s in p.profiles[desired_role].get("top_skills", [])[:20]))
    
    # extract user skills from vector
    if isinstance(vector, np.ndarray):
        if len(vector.shape) == 2:
            indices = np.where(vector[0] > 0)[0]
        else:
            indices = np.where(vector > 0)[0]
    else:
        indices = vector
        
    have = {p.vocab[int(i)].lower() for i in indices if 0 <= int(i) < p.width}
    covered = [s for s in top if s in have]
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
        
    # Check if user already has it
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
