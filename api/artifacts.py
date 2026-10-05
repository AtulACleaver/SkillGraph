import json
from typing import Any

from etl.paths import ARTIFACTS_DIR


class ArtifactsManager:
    def __init__(self):
        self.vocab: dict[str, Any] = {}
        self.autocomplete: list[dict[str, Any]] = []
        self.role_profiles: dict[str, Any] = {}
        self.artifacts_loaded = False
        
        self.n_skills = 0
        self.n_postings = 0
        
        # New model metadata
        self.model_version: str | None = None
        self.rules_version: str | None = None

    def load(self):
        vocab_path = ARTIFACTS_DIR / "skill_vocab.json"
        if vocab_path.exists():
            with open(vocab_path, "r") as f:
                self.vocab = json.load(f)
                self.n_skills = len(self.vocab)
        
        autocomplete_path = ARTIFACTS_DIR / "skills_autocomplete.json"
        if autocomplete_path.exists():
            with open(autocomplete_path, "r") as f:
                self.autocomplete = json.load(f)
        
        roles_path = ARTIFACTS_DIR / "role_profiles.json"
        if roles_path.exists():
            with open(roles_path, "r") as f:
                self.role_profiles = json.load(f)
                self.n_postings = sum(d.get("n_postings", 0) for d in self.role_profiles.values())
                
        model_path = ARTIFACTS_DIR / "model.json"
        if model_path.exists():
            with open(model_path, "r") as f:
                model_data = json.load(f)
                self.model_version = model_data.get("source")
                
        rules_path = ARTIFACTS_DIR / "rules.json"
        if rules_path.exists():
            with open(rules_path, "r") as f:
                rules_data = json.load(f)
                self.rules_version = rules_data.get("source")
                
        # Ensure all required artifacts were successfully loaded
        if self.vocab and self.role_profiles and self.model_version and self.rules_version:
            self.artifacts_loaded = True
        else:
            raise FileNotFoundError(f"Missing one or more JSON artifacts in {ARTIFACTS_DIR}")

artifacts = ArtifactsManager()
