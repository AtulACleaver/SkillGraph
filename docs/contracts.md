# Contracts

- skill_vocab.json: ordered JSON list of canonical names. skill_id == list index, starting at 0. len(vocab) == classifier.n_features_in_. Frozen once data-v4 ships.
- skills_autocomplete.json: list of {id, name, display, aliases}, vocab skills only. This file feeds /api/skills, not skill_vocab.json.
- dataset.parquet: posting_id, skill_ids, role_family, experience_band, company, location_raw. Labelled rows only.
- role_profiles.json: {role: {n_postings, top_skills, skill_freq}} for every class. top_skills = the role's 20 most common skill names in the train split, before augmentation. skill_freq = [[name, share], ...] for the same 20, where share = fraction of that role's train postings listing the skill. Aryan's coverage_pct is that share.
- baskets.parquet: posting_id, skill_ids. Every tech row, labelled or not.
- model.json: {classes: list, coef: 2D list, intercept: list, n_features: int, vocab_sha256: str, source: str}.
- rules.json: {rules: [{antecedent: list, consequent: list, support: float, confidence: float, lift: float}], source: str}.
- Classes: the families in taxonomy/role_families.csv minus "Software Engineer (generic)", with Database / DBA merged into Data / BI Analyst and Mobile kept. Expect 10.
- Bands: "Ready", "Close", "Not yet". Never High/Medium/Low.
- Response shapes: api/schemas.py on main, unchanged. MatchResponse {matches: [{role, probability}], unrecognized}. ReadinessResponse {probability, band, coverage, covered, missing_count}. GapResponse {recommendations: [{skill, coverage_pct, readiness_gain, learn_with}]}.
- Health fields: `/api/health` includes `model` and `rules` metadata fields.
- Input caps: Maximum 30 skills per request. Maximum 60 characters per skill.
- Signatures, module-level:
  - etl/normalize.py: `skills_to_vector(raw: list[str]) -> tuple[np.ndarray, list[str]]`, returning (vector, unrecognized strings exactly as typed).
  - ml/predict.py: `predict_roles(vector) -> list[dict]` ([{role, probability}] for every class, sorted descending), `readiness(vector, desired_role) -> dict` (the ReadinessResponse fields), `delta_readiness(vector, desired_role, candidate_skill_id) -> float`.
  - mining/gap.py (Aryan): `rank_gap(vector, desired_role, top_n=5) -> list[dict]`.
- An unknown desired_role raises ValueError. An all-zero vector raises ValueError (never predict from it: that returns the class priors). Routes turn both into 400s and list the unrecognized skills.

## Personas

1. `["sql", "excel", "power bi", "tableau"]` for role `Data / BI Analyst`:
   - Match: top match Data / BI Analyst 0.9733
   - Readiness: probability 0.9733, band Close, coverage 0.1, covered sql and power bi.

2. `["java", "spring boot", "mysql", "docker"]` for role `Backend`:
   - Readiness: probability 0.7520, band Close, coverage 0.15.

3. `["react", "javascript", "html", "css"]` for role `Full Stack`:
   - Match: top match Frontend 0.7369
   - Readiness: probability 0.2395, band Not yet.

4. `["python", "sql", "pandas"]` for role `Data / BI Analyst` (known limitation):
   - Match: top match Backend 0.4906
   - Readiness: probability 0.1080, band Not yet, coverage 0.1, covered sql and python.

