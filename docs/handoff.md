# Gate 3 Handoff

## 1. For Archit (api)
Update `/skills` to use the autocomplete JSON.
**Diff for `api/main.py`:**
```diff
--- a/api/main.py
+++ b/api/main.py
@@ -106,12 +106,17 @@
 
 @app.get("/skills", response_model=list[schemas.SkillResponse])
 def get_skills(q: str = ""):
+    import json
+    import os
+    with open(os.path.join(os.environ.get("ARTIFACTS_DIR", "artifacts"), "skills_autocomplete.json")) as f:
+        autocomplete = json.load(f)
     result = []
     q_lower = q.lower()
-    for name, skill_id in artifacts.vocab.items():
-        if q_lower in name:
+    for item in autocomplete:
+        if not q or q_lower in item["name"].lower() or any(q_lower in a.lower() for a in item.get("aliases", [])):
             result.append(schemas.SkillResponse(
-                skill_id=skill_id,
-                name=name.title(),
-                aliases=[]
+                skill_id=item["id"],
+                name=item["display"],
+                aliases=item.get("aliases", [])
             ))
+            if len(result) == 20: break
-    return result[:20]
+    return result
```
**Apply check (on `origin/archit/6-caching-error`):**
```bash
$ git apply --check archit.patch
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

**Diff for `mining/gap.py` (Vocab loading fix):**
```diff
--- a/mining/gap.py
+++ b/mining/gap.py
@@ -37,12 +37,11 @@
 def load_gap_artifacts(artifacts_dir: str | None = None) -> dict[str, Any]:
     if artifacts_dir is None:
         artifacts_dir = _get_artifacts_dir()
 
     vocab_path = os.path.join(artifacts_dir, "skill_vocab.json")
     skill_to_id = {}
     id_to_skill = {}
     if os.path.exists(vocab_path):
         with open(vocab_path, "r", encoding="utf-8") as f:
-            skill_to_id = json.load(f)
-            id_to_skill = {int(v): k for k, v in skill_to_id.items()}
+            vocab = json.load(f)
+            skill_to_id = {name: i for i, name in enumerate(vocab)}
+            id_to_skill = dict(enumerate(vocab))
```
**Apply check (on `origin/aryan/day1-day2-vocabularies`):**
```bash
$ git apply --check aryan.patch
# Returns 0 (success)
```
