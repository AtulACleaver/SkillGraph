#!/usr/bin/env python3
import json
import os
import sys

from etl.normalize import skills_to_vector
from ml.predict import readiness
from mining.gap import rank_gap, get_gap_artifacts

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONAS_PATH = os.path.join(REPO_ROOT, "tests", "data", "personas.json")

def main():
    with open(PERSONAS_PATH, "r") as f:
        personas = json.load(f)

    artifacts = get_gap_artifacts()
    non_skills = artifacts.get("non_skills", set())
    
    total_junk = 0

    for p in personas:
        name = p["name"]
        skills = p["skills"]
        desired_role = p["desired_role"]

        vector, _ = skills_to_vector(skills)
        r = readiness(vector, desired_role)
        gaps = rank_gap(vector, desired_role, top_n=5)
        
        # calculate junk count
        junk = 0
        generic_words = ["development", "developer", "engineering", "engineer", "administration", "administrator"]
        user_skills_lower = [s.lower() for s in skills]
        
        for gap in gaps:
            gap_lower = gap["skill"].lower()
            if gap_lower in non_skills:
                junk += 1
                continue
                
            is_generic = False
            for u in user_skills_lower:
                if gap_lower.startswith(u + " "):
                    suffix = gap_lower[len(u)+1:]
                    if suffix in generic_words:
                        is_generic = True
                        break
            if is_generic:
                junk += 1

        top_5_skills = [g["skill"] for g in gaps]
        print(f"Persona: {name}")
        print(f"Role: {desired_role}")
        print(f"Readiness: {r['probability']:.4f}")
        print(f"Band: {r['band']}")
        print(f"Top 5 gaps: {top_5_skills}")
        print(f"Junk count: {junk}")
        print("-" * 40)
        
        total_junk += junk

    if total_junk > 0:
        print(f"FAILED: Found {total_junk} junk recommendations across all personas.")
        sys.exit(1)
    else:
        print("SUCCESS: 0 junk recommendations.")

if __name__ == "__main__":
    main()
