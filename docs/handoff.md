# Handoff for Archit and Aryan

## For Aryan (taxonomy & mining)
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

**Diff for `mining/gap.py`:**
```diff
- import json
- # gap.py loads skill_vocab.json as a dict, or uses fixtures
- try:
-     with open('artifacts/skill_vocab.json') as f:
-         _vocab = json.load(f)
- except:
-     with open('fixtures/skill_vocab.json') as f:
-         _vocab = json.load(f)
+ import json
+ from ml.predict import delta_readiness
+ 
+ with open('artifacts/skill_vocab.json') as f:
+     _vocab_list = json.load(f)
+ _vocab = {name: i for i, name in enumerate(_vocab_list)}
+ 
- # Using rank position fallback
- readiness_gain = 1.0 / rank_position
+ readiness_gain = delta_readiness(vector, desired_role, candidate_skill_id)
```

## For Archit (api)
**Diff for `api/main.py`:**
```diff
- @app.get("/skills")
- def get_skills():
-     with open('artifacts/skill_vocab.json') as f:
-         vocab = json.load(f)
-     return vocab.items()
+ @app.get("/skills")
+ def get_skills():
+     with open('artifacts/skills_autocomplete.json') as f:
+         autocomplete = json.load(f)
+     return autocomplete
```
