# Contracts

- skill_vocab.json: ordered JSON list of canonical names. skill_id == list index, starting at 0. len(vocab) == classifier.n_features_in_. Frozen once data-v3 ships.
- skills_autocomplete.json: list of {id, name, display, aliases}, vocab skills only. This file feeds /skills, not skill_vocab.json.
- dataset.parquet: posting_id, skill_ids, role_family, experience_band, company, location_raw. Labelled rows only.
- baskets.parquet: posting_id, skill_ids. Every tech row, labelled or not.
- Classes: the families in taxonomy/role_families.csv minus "Software Engineer (generic)", with Database / DBA merged into Data / BI Analyst and Mobile kept. Expect 10.
- Bands: "Ready", "Close", "Not yet". Never High/Medium/Low.
- Response shapes: api/schemas.py on main, unchanged. MatchResponse {matches: [{role, probability}], unrecognized}. ReadinessResponse {probability, band, coverage, covered, missing_count}. GapResponse {recommendations: [{skill, coverage_pct, readiness_gain, learn_with}]}.
- Signatures, module-level:
  - etl/normalize.py: `skills_to_vector(raw: list[str]) -> tuple[np.ndarray, list[str]]`, returning (vector, unrecognized strings exactly as typed).
  - ml/predict.py: `predict_roles(vector) -> list[dict]` ([{role, probability}] for every class, sorted descending), `readiness(vector, desired_role) -> dict` (the ReadinessResponse fields), `delta_readiness(vector, desired_role, candidate_skill_id) -> float`. Predictor can stay as the loader behind them.
  - mining/gap.py (Aryan): `rank_gap(vector, desired_role, top_n=5) -> list[dict]`.
- An unknown desired_role raises ValueError. An all-zero vector raises ValueError (never predict from it: that returns the class priors). Routes turn both into 400s and list the unrecognized skills.
