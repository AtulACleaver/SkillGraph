import json
import sys
from pathlib import Path

# Add project root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from etl.normalize import skills_to_vector
from etl.paths import TAXONOMY_DIR
from mining.gap import _is_redundant_skill, rank_gap
from ml.predict import readiness


def load_non_learnable() -> set[str]:
    nl_path = TAXONOMY_DIR / "non_learnable.txt"
    if not nl_path.exists():
        return set()
    with open(nl_path, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip() and not line.startswith("#")}


def check_personas() -> int:
    personas_path = REPO_ROOT / "tests" / "data" / "personas.json"
    with open(personas_path, "r", encoding="utf-8") as f:
        personas = json.load(f)

    non_learnable = load_non_learnable()
    total_junk = 0

    print("=" * 80)
    print(f"{'PERSONA':<22} | {'ROLE':<18} | {'READINESS':<9} | {'BAND':<8} | {'JUNK':<4} | TOP 5 GAPS")
    print("-" * 80)

    for p in personas:
        name = p.get("name", p["role"])
        role = p["role"]
        user_skills = p["skills"]

        vector, _ = skills_to_vector(user_skills)
        read = readiness(vector, role)
        prob = read["probability"]
        band = read["band"]

        gaps = rank_gap(vector, role, top_n=5)
        gap_names = [g["skill"] for g in gaps]

        junk_skills = []
        for g in gaps:
            g_raw = g["skill"].lower()
            if g_raw in non_learnable or _is_redundant_skill(g_raw, set(user_skills)):
                junk_skills.append(g["skill"])

        junk_count = len(junk_skills)
        total_junk += junk_count

        gaps_str = ", ".join(gap_names)
        print(f"{name:<22} | {role:<18} | {prob:<9.4f} | {band:<8} | {junk_count:<4} | {gaps_str}")

    print("=" * 80)
    print(f"Total junk count across all {len(personas)} personas: {total_junk}")
    return total_junk


if __name__ == "__main__":
    junk = check_personas()
    if junk > 0:
        sys.exit(1)
