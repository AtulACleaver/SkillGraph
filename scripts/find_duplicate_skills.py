#!/usr/bin/env python3
import json
import csv
import re
from rapidfuzz import fuzz

def normalize(skill):
    # normalising case, plurals, a trailing "development" or "developer", spaces and dots
    s = skill.lower()
    s = s.replace(".", "").replace(" ", "")
    s = re.sub(r'developers?$', '', s)
    s = re.sub(r'developments?$', '', s)
    s = re.sub(r'js$', '', s)
    s = re.sub(r's$', '', s)
    return s

def are_blocked(s1, s2):
    # never merge sas and sass, java and javascript, c, c++ and c#, r, go, .net
    blocked_groups = [
        {"sas", "sass"},
        {"java", "javascript"},
        {"c", "c++", "c#"},
        {"r", "go", ".net", "net"},
        {"genai", "gen"}, # to be safe
        {"cd", "cds"},
        {"io", "ios"},
        {"api integration", "sap integration"},
        {"data services", "odata services"},
        {"testing", "testng"},
        {"mysql", "sql"},
        {"nosql", "sql"},
    ]
    for g in blocked_groups:
        if s1 in g and s2 in g:
            return True
    
    # Also "anything a hiring manager would call different skills"
    # Block if they are short acronyms that differ
    if len(s1) <= 3 and len(s2) <= 3 and s1 != s2:
        return True

    
    return False

def main():
    with open("artifacts/skill_vocab.json", "r") as f:
        vocab = json.load(f)

    # find duplicates
    merges = []
    processed = set()
    
    for i, s1 in enumerate(vocab):
        if s1 in processed:
            continue
            
        group = []
        n1 = normalize(s1)
        
        for j in range(i + 1, len(vocab)):
            s2 = vocab[j]
            if s2 in processed:
                continue
                
            if are_blocked(s1, s2):
                continue
                
            n2 = normalize(s2)
            
            # normalisation check
            if n1 == n2 and n1 != "":
                group.append((s2, "normalisation"))
                continue
                
            # rapidfuzz check
            ratio = fuzz.ratio(s1, s2)
            if ratio >= 92:
                group.append((s2, f"rapidfuzz_{ratio}"))
                
        if group:
            # We must decide 'keep'. Shorter or more standard is better.
            all_skills = [s1] + [g[0] for g in group]
            # pick shortest by length, but prefer ones without spaces?
            keep = sorted(all_skills, key=lambda x: (len(x), x))[0]
            
            for s, reason in group:
                if s == keep: continue
                # if keep was not s1, we need to add s1 to merge_from
                merges.append({"keep": keep, "merge_from": s, "reason": reason})
                processed.add(s)
            
            if s1 != keep:
                merges.append({"keep": keep, "merge_from": s1, "reason": "normalisation"})
                processed.add(s1)
            processed.add(keep)

    with open("docs/taxonomy_v4_merges.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["keep", "merge_from", "reason"])
        writer.writeheader()
        writer.writerows(merges)
        
    print(f"Proposed {len(merges)} merges.")

if __name__ == "__main__":
    main()
