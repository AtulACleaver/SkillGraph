# Gate 3 Handoff

## 1. For Archit (api)
Update `/skills` to use the autocomplete JSON.
**Diff for `api/main.py` and `api/artifacts.py`:**
```diff
diff --git a/api/artifacts.py b/api/artifacts.py
index 87a6d08..4c4c4da 100644
--- a/api/artifacts.py
+++ b/api/artifacts.py
@@ -19,6 +19,7 @@ sys.modules["__main__"].FakeLabelEncoder = FakeLabelEncoder
 class ArtifactsManager:
     def __init__(self):
         self.vocab: dict[str, Any] = {}
+        self.autocomplete: list[dict[str, Any]] = []
         self.role_profiles: dict[str, Any] = {}
         self.rules: pd.DataFrame = None
         self.classifier: Any = None
@@ -37,6 +38,12 @@ class ArtifactsManager:
                 self.vocab = json.load(f)
                 self.n_skills = len(self.vocab)
         
+        # /skills reads skills_autocomplete.json, not skill_vocab.json (contract)
+        autocomplete_path = os.path.join(artifacts_dir, "skills_autocomplete.json")
+        if os.path.exists(autocomplete_path):
+            with open(autocomplete_path, "r") as f:
+                self.autocomplete = json.load(f)
+
         roles_path = os.path.join(artifacts_dir, "role_profiles.json")
         if os.path.exists(roles_path):
             with open(roles_path, "r") as f:
diff --git a/api/main.py b/api/main.py
index 7294ead..159898c 100644
--- a/api/main.py
+++ b/api/main.py
@@ -89,14 +89,17 @@ def get_roles():
 def get_skills(q: str = ""):
     result = []
     q_lower = q.lower()
-    for name, skill_id in artifacts.vocab.items():
-        if q_lower in name:
+    for item in artifacts.autocomplete:
+        names = [item["name"], item["display"], *item.get("aliases", [])]
+        if any(q_lower in n.lower() for n in names):
             result.append(schemas.SkillResponse(
-                skill_id=skill_id,
-                name=name.title(),
-                aliases=[]
+                skill_id=item["id"],
+                name=item["display"],
+                aliases=item.get("aliases", [])
             ))
-    return result[:20]
+            if len(result) == 20:
+                break
+    return result
 
 @app.post("/match", response_model=schemas.MatchResponse)
 def match(request: schemas.MatchRequest):
diff --git a/fixtures/skills_autocomplete.json b/fixtures/skills_autocomplete.json
new file mode 100644
index 0000000..a3357c6
--- /dev/null
+++ b/fixtures/skills_autocomplete.json
@@ -0,0 +1,242 @@
+[
+  {
+    "id": 0,
+    "name": "python",
+    "display": "Python",
+    "aliases": []
+  },
+  {
+    "id": 1,
+    "name": "java",
+    "display": "Java",
+    "aliases": []
+  },
+  {
+    "id": 2,
+    "name": "c++",
+    "display": "C++",
+    "aliases": []
+  },
+  {
+    "id": 3,
+    "name": "javascript",
+    "display": "Javascript",
+    "aliases": []
+  },
+  {
+    "id": 4,
+    "name": "typescript",
+    "display": "Typescript",
+    "aliases": []
+  },
+  {
+    "id": 5,
+    "name": "react",
+    "display": "React",
+    "aliases": []
+  },
+  {
+    "id": 6,
+    "name": "angular",
+    "display": "Angular",
+    "aliases": []
+  },
+  {
+    "id": 7,
+    "name": "vue.js",
+    "display": "Vue.Js",
+    "aliases": []
+  },
+  {
+    "id": 8,
+    "name": "node.js",
+    "display": "Node.Js",
+    "aliases": []
+  },
+  {
+    "id": 9,
+    "name": "django",
+    "display": "Django",
+    "aliases": []
+  },
+  {
+    "id": 10,
+    "name": "flask",
+    "display": "Flask",
+    "aliases": []
+  },
+  {
+    "id": 11,
+    "name": "fastapi",
+    "display": "Fastapi",
+    "aliases": []
+  },
+  {
+    "id": 12,
+    "name": "spring boot",
+    "display": "Spring Boot",
+    "aliases": []
+  },
+  {
+    "id": 13,
+    "name": "sql",
+    "display": "Sql",
+    "aliases": []
+  },
+  {
+    "id": 14,
+    "name": "postgresql",
+    "display": "Postgresql",
+    "aliases": []
+  },
+  {
+    "id": 15,
+    "name": "mysql",
+    "display": "Mysql",
+    "aliases": []
+  },
+  {
+    "id": 16,
+    "name": "mongodb",
+    "display": "Mongodb",
+    "aliases": []
+  },
+  {
+    "id": 17,
+    "name": "redis",
+    "display": "Redis",
+    "aliases": []
+  },
+  {
+    "id": 18,
+    "name": "elasticsearch",
+    "display": "Elasticsearch",
+    "aliases": []
+  },
+  {
+    "id": 19,
+    "name": "aws",
+    "display": "Aws",
+    "aliases": []
+  },
+  {
+    "id": 20,
+    "name": "azure",
+    "display": "Azure",
+    "aliases": []
+  },
+  {
+    "id": 21,
+    "name": "google cloud",
+    "display": "Google Cloud",
+    "aliases": []
+  },
+  {
+    "id": 22,
+    "name": "docker",
+    "display": "Docker",
+    "aliases": []
+  },
+  {
+    "id": 23,
+    "name": "kubernetes",
+    "display": "Kubernetes",
+    "aliases": []
+  },
+  {
+    "id": 24,
+    "name": "terraform",
+    "display": "Terraform",
+    "aliases": []
+  },
+  {
+    "id": 25,
+    "name": "jenkins",
+    "display": "Jenkins",
+    "aliases": []
+  },
+  {
+    "id": 26,
+    "name": "git",
+    "display": "Git",
+    "aliases": []
+  },
+  {
+    "id": 27,
+    "name": "linux",
+    "display": "Linux",
+    "aliases": []
+  },
+  {
+    "id": 28,
+    "name": "bash",
+    "display": "Bash",
+    "aliases": []
+  },
+  {
+    "id": 29,
+    "name": "machine learning",
+    "display": "Machine Learning",
+    "aliases": []
+  },
+  {
+    "id": 30,
+    "name": "deep learning",
+    "display": "Deep Learning",
+    "aliases": []
+  },
+  {
+    "id": 31,
+    "name": "tensorflow",
+    "display": "Tensorflow",
+    "aliases": []
+  },
+  {
+    "id": 32,
+    "name": "pytorch",
+    "display": "Pytorch",
+    "aliases": []
+  },
+  {
+    "id": 33,
+    "name": "scikit-learn",
+    "display": "Scikit-Learn",
+    "aliases": []
+  },
+  {
+    "id": 34,
+    "name": "pandas",
+    "display": "Pandas",
+    "aliases": []
+  },
+  {
+    "id": 35,
+    "name": "numpy",
+    "display": "Numpy",
+    "aliases": []
+  },
+  {
+    "id": 36,
+    "name": "data analysis",
+    "display": "Data Analysis",
+    "aliases": []
+  },
+  {
+    "id": 37,
+    "name": "data engineering",
+    "display": "Data Engineering",
+    "aliases": []
+  },
+  {
+    "id": 38,
+    "name": "apache spark",
+    "display": "Apache Spark",
+    "aliases": []
+  },
+  {
+    "id": 39,
+    "name": "apache kafka",
+    "display": "Apache Kafka",
+    "aliases": []
+  }
+]
```
**Apply check (on `origin/archit/6-caching-error`):**
```bash
$ git apply --check archit_skills.patch
# Returns 0 (success)
```

## 2. For Aryan (taxonomy & mining)
**Six aliases that collapse distant concepts to fix:**
1. ai/ml/generative ai
2. ui/ux
3. frontend/backend/full stack
4. qa/automation
5. cloud/aws/azure
6. devops/ci-cd

**Suspicious Aliases in `taxonomy/skill_aliases.csv`:**
- `business development` -> `sales`
- `automation testing` -> `qa`
- `machine learning` -> `ml`
- `artificial intelligence` -> `ai`

**Unmatched Tech Titles (>25%):**
We have 16,142 unmatched rows out of the dataset. Many tech titles were missed by the current patterns. Here are some of the top missed titles that you should write patterns for:
- Application Lead
- Software Development Lead
- Application Designer
- Security Architect
- Business Analyst
- Technical Lead
- Solution Architect
- Scrum Master

**Diff for `mining/gap.py` and `mining/rules.py`:**
```diff
diff --git a/mining/gap.py b/mining/gap.py
index 6b0ed2b..a55d4c0 100644
--- a/mining/gap.py
+++ b/mining/gap.py
@@ -38,8 +38,9 @@ def load_gap_artifacts(artifacts_dir: str | None = None) -> dict[str, Any]:
     id_to_skill = {}
     if os.path.exists(vocab_path):
         with open(vocab_path, "r", encoding="utf-8") as f:
-            skill_to_id = json.load(f)
-            id_to_skill = {int(v): k for k, v in skill_to_id.items()}
+            vocab = json.load(f)
+            skill_to_id = {name: i for i, name in enumerate(vocab)}
+            id_to_skill = dict(enumerate(vocab))
 
     # 3. Association rules
     rules_path = os.path.join(base_dir, "rules.parquet")
diff --git a/mining/gap.py b/mining/gap.py
index a55d4c0..53dada8 100644
--- a/mining/gap.py
+++ b/mining/gap.py
@@ -180,6 +180,7 @@ def rank_gap(
 
     profile = role_profiles[desired_role]
     top_role_skills: list[str] = profile.get("top_skills", [])
+    skill_freq = dict(profile.get("skill_freq", []))
 
     # Identify user's current skills
     user_skills = _extract_user_skills(vector, skill_to_id, id_to_skill)
@@ -202,14 +203,13 @@ def rank_gap(
         pass
 
     scored_recommendations: list[dict[str, Any]] = []
-    total_role_skills = max(len(top_role_skills), 1)
 
     for rank_idx, skill in enumerate(candidates):
         skill_lower = skill.lower()
         skill_id = skill_to_id.get(skill_lower)
 
-        # Coverage in role postings
-        base_coverage = max(0.20, 0.85 - (rank_idx / total_role_skills) * 0.65)
+        # Coverage = share of the role's train postings listing this skill
+        base_coverage = skill_freq[skill_lower]
 
         # Calculate readiness gain
         if delta_readiness_fn and skill_id is not None:
diff --git a/mining/gap.py b/mining/gap.py
index 53dada8..e767858 100644
--- a/mining/gap.py
+++ b/mining/gap.py
@@ -194,17 +194,11 @@ def rank_gap(
 
     candidate_skills_lower = {s.lower() for s in candidates}
 
-    # Try importing real delta_readiness from ml.predict if available
-    delta_readiness_fn = None
-    try:
-        from ml.predict import delta_readiness
-        delta_readiness_fn = delta_readiness
-    except (ImportError, AttributeError):
-        pass
+    from ml.predict import delta_readiness
 
     scored_recommendations: list[dict[str, Any]] = []
 
-    for rank_idx, skill in enumerate(candidates):
+    for skill in candidates:
         skill_lower = skill.lower()
         skill_id = skill_to_id.get(skill_lower)
 
@@ -212,14 +206,9 @@ def rank_gap(
         base_coverage = skill_freq[skill_lower]
 
         # Calculate readiness gain
-        if delta_readiness_fn and skill_id is not None:
-            try:
-                gain = delta_readiness_fn(vector, desired_role, skill_id)
-            except (ValueError, TypeError, KeyError, AttributeError):
-                gain = base_coverage * 0.35
-        else:
-            # Fallback heuristic: weighted by role rank and co-occurrence
-            gain = round(base_coverage * 0.28 + (1.0 / (rank_idx + 1)) * 0.05, 4)
+        if skill_id is None:
+            raise KeyError(f"Skill '{skill}' from role_profiles is not in skill_vocab.json")
+        gain = delta_readiness(vector, desired_role, skill_id)
 
         # Score = readiness_gain * coverage
         score = gain * base_coverage
diff --git a/mining/gap.py b/mining/gap.py
index e767858..0023628 100644
--- a/mining/gap.py
+++ b/mining/gap.py
@@ -96,38 +96,34 @@ def _extract_user_skills(
 
 
 def _find_companions(
-    candidate_skill: str,
-    all_candidate_skills: set[str],
+    candidate_id: int,
+    candidate_ids: set[int],
     rules_df: pd.DataFrame | None,
+    id_to_skill: dict[int, str],
     min_lift: float = 1.5,
 ) -> list[str]:
-    """Find companion skills that co-occur with high lift."""
+    """Other gap skills that co-occur with candidate_id at lift >= min_lift.
+
+    rules.parquet stores antecedent/consequent as lists of skill IDs.
+    """
     if rules_df is None or rules_df.empty:
         return []
 
-    companions = []
-    cand_lower = candidate_skill.lower()
-
-    for _, row in rules_df.iterrows():
-        lift = row.get("lift", 0.0)
-        if lift < min_lift:
+    companion_ids: list[int] = []
+    strong = rules_df[rules_df["lift"] >= min_lift]
+    for ant, consq in zip(strong["antecedent"], strong["consequent"]):
+        ant, consq = {int(x) for x in ant}, {int(x) for x in consq}
+        if candidate_id in ant:
+            others = consq
+        elif candidate_id in consq:
+            others = ant
+        else:
             continue
+        for other in sorted(others):
+            if other != candidate_id and other in candidate_ids and other not in companion_ids:
+                companion_ids.append(other)
 
-        ant = [str(x).lower() for x in row.get("antecedent", [])]
-        consq = [str(x).lower() for x in row.get("consequent", [])]
-
-        # If candidate is in antecedent, check consequents
-        if cand_lower in ant:
-            for item in consq:
-                if item != cand_lower and item in all_candidate_skills and item not in companions:
-                    companions.append(item.title())
-        # If candidate is in consequent, check antecedents
-        elif cand_lower in consq:
-            for item in ant:
-                if item != cand_lower and item in all_candidate_skills and item not in companions:
-                    companions.append(item.title())
-
-    return companions[:2]
+    return [id_to_skill[i].title() for i in companion_ids[:2]]
 
 
 def rank_gap(
@@ -192,7 +188,7 @@ def rank_gap(
     if not candidates:
         return []
 
-    candidate_skills_lower = {s.lower() for s in candidates}
+    candidate_ids = {skill_to_id[s.lower()] for s in candidates if s.lower() in skill_to_id}
 
     from ml.predict import delta_readiness
 
@@ -214,7 +210,7 @@ def rank_gap(
         score = gain * base_coverage
 
         # Companion skills with high lift (>1.5)
-        learn_with = _find_companions(skill, candidate_skills_lower, rules_df, min_lift=1.5)
+        learn_with = _find_companions(skill_id, candidate_ids, rules_df, id_to_skill, min_lift=1.5)
 
         scored_recommendations.append(
             {
diff --git a/mining/rules.py b/mining/rules.py
index 65f1731..7046f25 100644
--- a/mining/rules.py
+++ b/mining/rules.py
@@ -85,7 +85,7 @@ def save_rules(rules_df: pd.DataFrame, output_path: str = "artifacts/rules.parqu
 
 
 def run_rule_mining(
-    baskets_file: str = "data/dataset.parquet",
+    baskets_file: str = "data/baskets.parquet",
     output_rules_file: str = "artifacts/rules.parquet",
     min_sup_pct: float = 0.005,
     min_confidence: float = 0.3,
@@ -136,7 +136,7 @@ def run_rule_mining(
 
 
 if __name__ == "__main__":
-    if os.path.exists("data/dataset.parquet"):
+    if os.path.exists("data/baskets.parquet"):
         run_rule_mining()
     else:
-        print("data/dataset.parquet not found. Run ETL pipeline first.")
+        print("data/baskets.parquet not found. Run ETL pipeline first.")
diff --git a/mining/gap.py b/mining/gap.py
index 0023628..a12ebeb 100644
--- a/mining/gap.py
+++ b/mining/gap.py
@@ -21,6 +21,17 @@ def _get_artifacts_dir() -> str:
     return env_dir
 
 
+_CACHE: dict[str, Any] | None = None
+
+
+def get_gap_artifacts() -> dict[str, Any]:
+    """Load artifacts once, reading ARTIFACTS_DIR at first call (not import)."""
+    global _CACHE
+    if _CACHE is None:
+        _CACHE = load_gap_artifacts()
+    return _CACHE
+
+
 def load_gap_artifacts(artifacts_dir: str | None = None) -> dict[str, Any]:
     """Load role profiles, skill vocab, and association rules."""
     base_dir = artifacts_dir or _get_artifacts_dir()
@@ -152,7 +163,7 @@ def rank_gap(
         ]
     """
     if artifacts is None:
-        artifacts = load_gap_artifacts()
+        artifacts = get_gap_artifacts()
 
     role_profiles = artifacts.get("role_profiles", {})
     skill_to_id = artifacts.get("skill_to_id", {})
diff --git a/mining/gap.py b/mining/gap.py
index a12ebeb..acd06dc 100644
--- a/mining/gap.py
+++ b/mining/gap.py
@@ -5,6 +5,9 @@ from typing import Any
 import numpy as np
 import pandas as pd
 
+# Generic words that appear in top_skills but are not something you can learn.
+NON_SKILLS = {"data", "development"}
+
 
 def _get_artifacts_dir() -> str:
     """Get artifacts directory with fallback to fixtures."""
@@ -193,7 +196,10 @@ def rank_gap(
     user_skills = _extract_user_skills(vector, skill_to_id, id_to_skill)
 
     # Candidate set: Role's top skills minus what user already has
-    candidates = [s for s in top_role_skills if s.lower() not in user_skills]
+    candidates = [
+        s for s in top_role_skills
+        if s.lower() not in user_skills and s.lower() not in NON_SKILLS
+    ]
 
     # Cold case: User already has all top skills
     if not candidates:
```
**Apply check (on `origin/aryan/day1-day2-vocabularies`):**
```bash
$ git apply --check aryan.patch
# Returns 0 (success)
```
