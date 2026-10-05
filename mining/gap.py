import json
from typing import Any

import numpy as np

from etl.paths import ARTIFACTS_DIR

from etl.paths import ARTIFACTS_DIR, REPO_ROOT

_CACHE: dict[str, Any] | None = None


def get_gap_artifacts() -> dict[str, Any]:
    """Load artifacts once."""
    global _CACHE
    if _CACHE is None:
        _CACHE = load_gap_artifacts()
    return _CACHE


def load_gap_artifacts() -> dict[str, Any]:
    """Load role profiles, skill vocab, and association rules."""
    
    # 1. Role profiles
    role_profiles_path = ARTIFACTS_DIR / "role_profiles.json"
    if not role_profiles_path.exists():
        raise FileNotFoundError(f"Missing required artifact: {role_profiles_path}")
    with open(role_profiles_path, "r", encoding="utf-8") as f:
        role_profiles = json.load(f)

    # 2. Skill vocabulary
    vocab_path = ARTIFACTS_DIR / "skill_vocab.json"
    if not vocab_path.exists():
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
    rules_path = ARTIFACTS_DIR / "rules.json"
    rules_list = []
    if rules_path.exists():
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                rules_data = json.load(f)
                rules_list = rules_data.get("rules", [])
        except (FileNotFoundError, ValueError, OSError):
            rules_list = []

    # 4. Non-learnable skills
    non_skills = set()
    non_skills_path = REPO_ROOT / "taxonomy" / "non_learnable.txt"
    if non_skills_path.exists():
        with open(non_skills_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    non_skills.add(line.strip().lower())

    return {
        "role_profiles": role_profiles,
        "skill_to_id": skill_to_id,
        "id_to_skill": id_to_skill,
        "rules_list": rules_list,
        "non_skills": non_skills,
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
    rules_list: list[dict[str, Any]],
    id_to_skill: dict[int, str],
    min_lift: float = 1.5,
) -> list[str]:
    """Other gap skills that co-occur with candidate_id at lift >= min_lift."""
    if not rules_list:
        return []

    companion_ids: list[int] = []
    for rule in rules_list:
        if rule.get("lift", 0) < min_lift:
            continue
            
        ant = set(rule["antecedent"])
        consq = set(rule["consequent"])
        
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
    """
    if artifacts is None:
        artifacts = get_gap_artifacts()

    role_profiles = artifacts.get("role_profiles", {})
    skill_to_id = artifacts.get("skill_to_id", {})
    id_to_skill = artifacts.get("id_to_skill", {})
    rules_list = artifacts.get("rules_list", [])
    non_skills = artifacts.get("non_skills", set())

    if not role_profiles:
        raise ValueError("System artifacts (role profiles) are missing or not loaded.")

    if not desired_role or desired_role not in role_profiles:
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

    user_skills = _extract_user_skills(vector, skill_to_id, id_to_skill)

    generic_words = ["development", "developer", "engineering", "engineer", "administration", "administrator"]
    
    candidates = []
    for s in top_role_skills:
        s_lower = s.lower()
        if s_lower in user_skills or s_lower in non_skills:
            continue
            
        # never recommends a skill that is a skill the user already has plus a generic word (java development when the user has java)
        is_user_skill_plus_generic = False
        for user_skill in user_skills:
            if s_lower.startswith(user_skill + " "):
                suffix = s_lower[len(user_skill) + 1:]
                if suffix in generic_words:
                    is_user_skill_plus_generic = True
                    break
        if is_user_skill_plus_generic:
            continue
            
        candidates.append(s)

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

        base_coverage = skill_freq.get(skill_lower, 0.0)

        if skill_id is None:
            raise KeyError(f"Skill '{skill}' from role_profiles is not in skill_vocab.json")
        gain = ml.predict.delta_readiness(predict_vector, desired_role, skill_id)

        score = gain * base_coverage

        learn_with = _find_companions(skill_id, candidate_ids, rules_list, id_to_skill, min_lift=1.5)

        scored_recommendations.append(
            {
                "skill": skill.title() if not skill.isupper() else skill,
                "coverage_pct": base_coverage,
                "readiness_gain": round(gain, 4),
                "learn_with": learn_with,
                "_score": score,
            }
        )

    scored_recommendations.sort(key=lambda x: x["_score"], reverse=True)

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