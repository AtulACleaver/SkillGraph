import json
import os
from typing import Any

import numpy as np
import pandas as pd

# Generic words that appear in top_skills but are not something you can learn.
NON_SKILLS = {
    "data",
    "development",
    "backend",
    "devops",
    "cloud",
    "front end",
    "frontend development",
    "ui development",
    "java development",
    "python development",
    "automation",
}


def _get_artifacts_dir() -> str:
    """Get artifacts directory with fallback to fixtures."""
    env_dir = os.getenv("ARTIFACTS_DIR", "artifacts")
    
    # If env_dir exists and contains role_profiles, use it
    if os.path.exists(env_dir) and os.path.exists(os.path.join(env_dir, "role_profiles.json")):
        return env_dir
        
    # Otherwise fallback to fixtures
    if os.path.exists("fixtures"):
        return "fixtures"
        
    return env_dir


_CACHE: dict[str, Any] | None = None


def get_gap_artifacts() -> dict[str, Any]:
    """Load artifacts once, reading ARTIFACTS_DIR at first call (not import)."""
    global _CACHE
    if _CACHE is None:
        _CACHE = load_gap_artifacts()
    return _CACHE


def load_gap_artifacts(artifacts_dir: str | None = None) -> dict[str, Any]:
    """Load role profiles, skill vocab, and association rules."""
    base_dir = artifacts_dir or _get_artifacts_dir()

    # 1. Role profiles
    role_profiles_path = os.path.join(base_dir, "role_profiles.json")
    if not os.path.exists(role_profiles_path):
        raise FileNotFoundError(f"Missing required artifact: {role_profiles_path}")
    with open(role_profiles_path, "r", encoding="utf-8") as f:
        role_profiles = json.load(f)

    # 2. Skill vocabulary
    vocab_path = os.path.join(base_dir, "skill_vocab.json")
    if not os.path.exists(vocab_path):
        raise FileNotFoundError(f"Missing required artifact: {vocab_path}")
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)
        if isinstance(vocab, dict):
            skill_to_id = {k.lower(): int(v) for k, v in vocab.items()}
            id_to_skill = {int(v): k for k, v in vocab.items()}
        else:
            skill_to_id = {name.lower(): i for i, name in enumerate(vocab)}
            id_to_skill = dict(enumerate(vocab))

    # 3. Association rules
    rules_path = os.path.join(base_dir, "rules.parquet")
    rules_df = None
    if os.path.exists(rules_path):
        try:
            rules_df = pd.read_parquet(rules_path)
        except (FileNotFoundError, ValueError, OSError):
            rules_df = None

    return {
        "role_profiles": role_profiles,
        "skill_to_id": skill_to_id,
        "id_to_skill": id_to_skill,
        "rules_df": rules_df,
    }


def _extract_user_skills(
    vector: np.ndarray | list[Any] | set[Any],
    skill_to_id: dict[str, int],
    id_to_skill: dict[int, str],
) -> set[str]:
    """Extract set of normalized lower-case skill names from input vector/list."""
    user_skills: set[str] = set()

    if isinstance(vector, (np.ndarray, list)):
        if len(vector) > 0 and isinstance(vector[0], (int, np.integer, float, np.floating)):
            # Binary one-hot or indexed vector
            if len(vector) == len(id_to_skill) or all(v in (0, 1, 0.0, 1.0) for v in vector):
                for idx, val in enumerate(vector):
                    if val > 0 and idx in id_to_skill:
                        user_skills.add(id_to_skill[idx].lower())
            else:
                # List of integer skill IDs
                for skill_id in vector:
                    skill_int = int(skill_id)
                    if skill_int in id_to_skill:
                        user_skills.add(id_to_skill[skill_int].lower())
        else:
            # List of string skill names
            for item in vector:
                if isinstance(item, str):
                    user_skills.add(item.strip().lower())
    elif isinstance(vector, set):
        for item in vector:
            if isinstance(item, str):
                user_skills.add(item.strip().lower())
            elif isinstance(item, int) and item in id_to_skill:
                user_skills.add(id_to_skill[item].lower())

    return user_skills


def _find_companions(
    candidate_id: int,
    candidate_ids: set[int],
    rules_df: pd.DataFrame | None,
    id_to_skill: dict[int, str],
    min_lift: float = 1.5,
) -> list[str]:
    """Other gap skills that co-occur with candidate_id at lift >= min_lift.

    rules.parquet stores antecedent/consequent as lists of skill IDs.
    """
    if rules_df is None or rules_df.empty:
        return []

    companion_ids: list[int] = []
    strong = rules_df[rules_df["lift"] >= min_lift]
    for ant, consq in zip(strong["antecedent"], strong["consequent"]):
        ant, consq = {int(x) for x in ant}, {int(x) for x in consq}
        if candidate_id in ant:
            others = consq
        elif candidate_id in consq:
            others = ant
        else:
            continue
        for other in sorted(others):
            if other != candidate_id and other in candidate_ids and other not in companion_ids:
                companion_ids.append(other)

    return [id_to_skill[i].title() for i in companion_ids[:2]]


def rank_gap(
    vector: np.ndarray | list[Any] | set[Any],
    desired_role: str,
    top_n: int = 5,
    artifacts: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Rank top skills to learn next for a desired role using counterfactual gain and association rules.
    
    Args:
        vector: User's current skills (binary numpy vector, skill ID list, or list of skill names).
        desired_role: Target role family name (e.g., 'Backend', 'Data Science / ML').
        top_n: Number of recommendations to return (default 5).
        artifacts: Preloaded artifacts dict. If None, loaded on-the-fly.
        
    Returns:
        List of dicts: [
            {
                "skill": str,
                "coverage_pct": float,
                "readiness_gain": float,
                "learn_with": List[str]
            }
        ]
    """
    if artifacts is None:
        artifacts = get_gap_artifacts()

    role_profiles = artifacts.get("role_profiles", {})
    skill_to_id = artifacts.get("skill_to_id", {})
    id_to_skill = artifacts.get("id_to_skill", {})
    rules_df = artifacts.get("rules_df")

    if not role_profiles:
        raise ValueError("System artifacts (role profiles) are missing or not loaded.")

    # Handle unknown or empty role
    if not desired_role or desired_role not in role_profiles:
        # Match case-insensitively
        matched_role = None
        for role_name in role_profiles:
            if role_name.lower() == str(desired_role).lower():
                matched_role = role_name
                break
        if not matched_role:
            raise ValueError(f"Role '{desired_role}' not found in role profiles.")
        desired_role = matched_role

    profile = role_profiles[desired_role]
    top_role_skills: list[str] = profile.get("top_skills", [])
    skill_freq = dict(profile.get("skill_freq", []))

    # Identify user's current skills
    user_skills = _extract_user_skills(vector, skill_to_id, id_to_skill)

    # Candidate set: Role's top skills minus what user already has
    candidates = [
        s for s in top_role_skills
        if s.lower() not in user_skills and s.lower() not in NON_SKILLS
    ]

    # Cold case: User already has all top skills
    if not candidates:
        return []

    candidate_ids = {skill_to_id[s.lower()] for s in candidates if s.lower() in skill_to_id}

    if isinstance(vector, np.ndarray):
        predict_vector = vector
    elif len(vector) > 0 and isinstance(next(iter(vector)), (int, np.integer)):
        predict_vector = [int(x) for x in vector]
    else:
        predict_vector = sorted({skill_to_id[s] for s in user_skills if s in skill_to_id})

    import ml.predict

    scored_recommendations: list[dict[str, Any]] = []

    for skill in candidates:
        skill_lower = skill.lower()
        skill_id = skill_to_id.get(skill_lower)

        # Coverage = share of the role's train postings listing this skill
        base_coverage = skill_freq.get(skill_lower, 0.0)

        # Calculate readiness gain
        if skill_id is None:
            raise KeyError(f"Skill '{skill}' from role_profiles is not in skill_vocab.json")
        gain = ml.predict.delta_readiness(predict_vector, desired_role, skill_id)

        # Score = readiness_gain * coverage
        score = gain * base_coverage

        # Companion skills with high lift (>1.5)
        learn_with = _find_companions(skill_id, candidate_ids, rules_df, id_to_skill, min_lift=1.5)

        scored_recommendations.append(
            {
                "skill": skill.title() if not skill.isupper() else skill,
                "coverage_pct": base_coverage,
                "readiness_gain": round(gain, 4),
                "learn_with": learn_with,
                "_score": score,
            }
        )

    # Sort by score descending
    scored_recommendations.sort(key=lambda x: x["_score"], reverse=True)

    # Clean up internal fields and truncate to top_n
    results = []
    for rec in scored_recommendations[:top_n]:
        results.append(
            {
                "skill": rec["skill"],
                "coverage_pct": rec["coverage_pct"],
                "readiness_gain": rec["readiness_gain"],
                "learn_with": rec["learn_with"],
            }
        )

    return results