import json
import os
import pickle
import pandas as pd
import sys
from typing import Any, Dict

class FakePredictor:
    pass

class FakeLabelEncoder:
    pass

sys.modules["__main__"].FakePredictor = FakePredictor
sys.modules["__main__"].FakeLabelEncoder = FakeLabelEncoder

class ArtifactsManager:
    def __init__(self):
        self.vocab: Dict[str, Any] = {}
        self.role_profiles: Dict[str, Any] = {}
        self.rules: pd.DataFrame = None
        self.classifier: Any = None
        self.label_encoder: Any = None
        self.artifacts_loaded = False
        
        self.n_skills = 0
        self.n_postings = 0

    def load(self):
        artifacts_dir = os.getenv("ARTIFACTS_DIR", "fixtures")
        
        vocab_path = os.path.join(artifacts_dir, "skill_vocab.json")
        if os.path.exists(vocab_path):
            with open(vocab_path, "r") as f:
                self.vocab = json.load(f)
                self.n_skills = len(self.vocab)
        
        roles_path = os.path.join(artifacts_dir, "role_profiles.json")
        if os.path.exists(roles_path):
            with open(roles_path, "r") as f:
                self.role_profiles = json.load(f)
                self.n_postings = sum(d.get("n_postings", 0) for d in self.role_profiles.values())
        
        rules_path = os.path.join(artifacts_dir, "rules.parquet")
        if os.path.exists(rules_path):
            self.rules = pd.read_parquet(rules_path)
            
        clf_path = os.path.join(artifacts_dir, "classifier.pkl")
        if os.path.exists(clf_path):
            with open(clf_path, "rb") as f:
                self.classifier = pickle.load(f)
                
        le_path = os.path.join(artifacts_dir, "label_encoder.pkl")
        if os.path.exists(le_path):
            with open(le_path, "rb") as f:
                self.label_encoder = pickle.load(f)
                
        # Ensure all required artifacts were successfully loaded
        if self.vocab and self.role_profiles and self.rules is not None and self.classifier and self.label_encoder:
            self.artifacts_loaded = True
        else:
            raise FileNotFoundError(f"Missing one or more artifacts in {artifacts_dir}")

artifacts = ArtifactsManager()
