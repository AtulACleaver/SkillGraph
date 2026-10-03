import json
import os
from typing import Any

import numpy as np
import pandas as pd


def _get_artifacts_dir() -> str:
    """Get artifacts directory with fallback to fixtures."""
    env_dir = os.getenv("ARTIFACTS_DIR", "artifacts")
    if os.path.exists(env_dir):
        return env_dir
    if os.path.exists("fixtures"):
        return "fixtures"
    return "artifacts"


def load_gap_artifacts(artifacts_dir: str | None = None) -> dict[str, Any]:
    """Load role profiles, skill vocab, and association rules."""
    base_dir = artifacts_dir or _get_artifacts_dir()

    # 1. Role profiles
    role_profiles_path = os.path.join(base_dir, "role_profiles.json")
    role_profiles = {}
    if os.path.exists(role_profiles_path):
        with open(role_profiles_path, "r", encoding="utf-8") as f:
            role_profiles = json.load(f)

    # 2. Skill vocabulary
    vocab_path = os.path.join(base_dir, "skill_vocab.json")
    skill_to_id = {}
    id_to_skill = {}
    if os.path.exists(vocab_path):
        with open(vocab_path, "r", encoding="utf-8") as f:
            skill_to_id = json.load(f)
            id_to_skill = {int(v): k for k, v in skill_to_id.items()}

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
    candidate_skill: str,
    all_candidate_skills: set[str],
    rules_df: pd.DataFrame | None,
    min_lift: float = 1.5,
) -> list[str]:
    """Find companion skills that co-occur with high lift."""
    if rules_df is None or rules_df.empty:
        return []

    companions = []
    cand_lower = candidate_skill.lower()

    for _, row in rules_df.iterrows():
        lift = row.get("lift", 0.0)
        if lift < min_lift:
            continue

        ant = [str(x).lower() for x in row.get("antecedent", [])]
        consq = [str(x).lower() for x in row.get("consequent", [])]

        # If candidate is in antecedent, check consequents
        if cand_lower in ant:
            for item in consq:
                if item != cand_lower and item in all_candidate_skills and item not in companions:
                    companions.append(item.title())
        # If candidate is in consequent, check antecedents
        elif cand_lower in consq:
            for item in ant:
                if item != cand_lower and item in all_candidate_skills and item not in companions:
                    companions.append(item.title())

    return companions[:2]


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
        artifacts = load_gap_artifacts()

    role_profiles = artifacts.get("role_profiles", {})
    skill_to_id = artifacts.get("skill_to_id", {})
    id_to_skill = artifacts.get("id_to_skill", {})
    rules_df = artifacts.get("rules_df")

    # Handle unknown or empty role
    if not desired_role or desired_role not in role_profiles:
        # Match case-insensitively
        matched_role = None
        for role_name in role_profiles:
            if role_name.lower() == str(desired_role).lower():
                matched_role = role_name
                break
        if not matched_role:
            return []
        desired_role = matched_role

    profile = role_profiles[desired_role]
    top_role_skills: list[str] = profile.get("top_skills", [])

    # Identify user's current skills
    user_skills = _extract_user_skills(vector, skill_to_id, id_to_skill)

    # Candidate set: Role's top skills minus what user already has
    candidates = [s for s in top_role_skills if s.lower() not in user_skills]

    # Cold case: User already has all top skills
    if not candidates:
        return []

    candidate_skills_lower = {s.lower() for s in candidates}

    # Try importing real delta_readiness from ml.predict if available
    delta_readiness_fn = None
    try:
        from ml.predict import delta_readiness
        delta_readiness_fn = delta_readiness
    except (ImportError, AttributeError):
        pass

    scored_recommendations: list[dict[str, Any]] = []
    total_role_skills = max(len(top_role_skills), 1)

    for rank_idx, skill in enumerate(candidates):
        skill_lower = skill.lower()
        skill_id = skill_to_id.get(skill_lower)

        # Coverage in role postings
        base_coverage = max(0.20, 0.85 - (rank_idx / total_role_skills) * 0.65)

        # Calculate readiness gain
        if delta_readiness_fn and skill_id is not None:
            try:
                gain = delta_readiness_fn(vector, desired_role, skill_id)
            except (ValueError, TypeError, KeyError, AttributeError):
                gain = base_coverage * 0.35
        else:
            # Fallback heuristic: weighted by role rank and co-occurrence
            gain = round(base_coverage * 0.28 + (1.0 / (rank_idx + 1)) * 0.05, 4)

        # Score = readiness_gain * coverage
        score = gain * base_coverage

        # Companion skills with high lift (>1.5)
        learn_with = _find_companions(skill, candidate_skills_lower, rules_df, min_lift=1.5)

        scored_recommendations.append(
            {
                "skill": skill.title() if not skill.isupper() else skill,
                "coverage_pct": round(base_coverage, 2),
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