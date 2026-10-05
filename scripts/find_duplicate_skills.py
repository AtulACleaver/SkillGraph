import csv
import json
import re
from pathlib import Path

from rapidfuzz import fuzz

REPO_ROOT = Path(__file__).resolve().parent.parent
VOCAB_PATH = REPO_ROOT / "artifacts" / "skill_vocab.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "taxonomy_v4_merges.csv"

# Protected skills and pairs that must NEVER be merged
NEVER_MERGE = {
    ("sas", "sass"),
    ("sass", "sas"),
    ("java", "javascript"),
    ("javascript", "java"),
    ("c", "c++"),
    ("c++", "c"),
    ("c", "c#"),
    ("c#", "c"),
    ("c++", "c#"),
    ("c#", "c++"),
    ("c", "cs"),
    ("cs", "c"),
    ("cd", "cds"),
    ("cds", "cd"),
    ("io", "ios"),
    ("ios", "io"),
    ("r", "go"),
    ("go", "r"),
    ("net", "net core"),
    ("asp", "aspnet"),
    ("aspnet", "aspnet core"),
    ("data services", "odata services"),
    ("odata services", "data services"),
    ("api integration", "sap integration"),
    ("sap integration", "api integration"),
    ("testing", "testng"),
    ("testng", "testing"),
    ("react", "react native"),
    ("react native", "react"),
    ("css", "cs"),
    ("cs", "css"),
}

PROTECTED_EXACT = {
    "sas", "sass", "java", "javascript", "c", "c++", "c#", "r", "go",
    "net", "net core", "asp", "aspnet", "aspnet core", "cd", "cds", "io", "ip", "s", "cs", "css",
}


def find_merges() -> list[dict[str, str]]:
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    vocab_set = set(vocab)

    merges: list[dict[str, str]] = []
    merged_from: set[str] = set()

    # 1. Explicit domain merges approved/requested in specification
    explicit_specs = [
        # React variants
        ("react", "react js", "suffix js"),
        ("react", "reacts js", "plural typo with suffix js"),
        # Spring Boot variants
        ("spring boot", "springboot", "spacing normalisation"),
        ("spring boot", "boot", "framework fragment"),
        # Angular variants
        ("angular", "angularjs", "variant with js suffix"),
        ("angular", "angular development", "trailing development"),
        # Databricks
        ("databricks", "data bricks", "spacing normalisation"),
        # Generative AI
        ("generative ai", "gen ai", "acronym expansion"),
        ("generative ai", "genai", "spacing normalisation"),
        # REST API variants
        ("rest api", "rest apis", "plural normalisation"),
        ("rest api", "rest api development", "trailing development"),
        ("rest api", "restful api", "spelling variant"),
        ("rest api", "restfull api", "spelling typo"),
        # Java variants
        ("java", "java development", "trailing development"),
        ("java", "javas", "plural typo"),
        # SAP variants
        ("sap", "sap development", "trailing development"),
        ("sap", "saps", "plural typo"),
        # SAP ABAP variants
        ("sap abap", "sap abap development", "trailing development"),
        ("sap abap", "abap development", "trailing development"),
        ("sap abap", "abap programming", "trailing programming"),
        # Mobile / UI / Web frameworks
        ("flutter", "flutter development", "trailing development"),
        ("ios", "ios development", "trailing development"),
        ("android", "android application development", "trailing development"),
        ("python", "python development", "trailing development"),
        ("sql", "sql development", "trailing development"),
        ("servicenow", "servicenow development", "trailing development"),
        ("salesforce", "sales force development", "trailing development"),
        # Cloud platform
        ("cloud platform", "cloud platforms", "plural normalisation"),
        # Role/domain development fragments in vocab
        ("full stack", "fullstack development", "trailing development"),
        ("backend", "backend development", "trailing development"),
        ("front end", "frontend development", "trailing development"),
        ("ui", "ui development", "trailing development"),
        ("software", "software development", "trailing development"),
        ("application", "application development", "trailing development"),
        # Additional approved merges
        ("azure", "microsoft azure", "vendor prefix"),
        ("nlp", "natural language processing", "acronym expansion"),
        ("selenium", "selenium webdriver", "tool component"),
        ("itil", "itil framework", "trailing framework"),
        ("java", "core java", "core prefix"),
        ("excel", "advanced excel", "advanced prefix"),
        ("web application", "web application development", "trailing development"),
    ]

    for keep, m_from, reason in explicit_specs:
        if keep in vocab_set and m_from in vocab_set and m_from not in merged_from:
            merges.append({"keep": keep, "merge_from": m_from, "reason": reason})
            merged_from.add(m_from)

    # 2. Automated scan for remaining trailing development/developer
    for s in vocab:
        if s in merged_from:
            continue
        dev_match = re.match(r"^(.*?)\s+(development|developer)$", s)
        if dev_match:
            base = dev_match.group(1).strip()
            if base in vocab_set and (base, s) not in NEVER_MERGE and base != s:
                merges.append({"keep": base, "merge_from": s, "reason": f"trailing {dev_match.group(2)}"})
                merged_from.add(s)

    # 3. Automated scan for plurals (e.g. trailing 's' where singular exists)
    for s in vocab:
        if s in merged_from or s in PROTECTED_EXACT:
            continue
        if s.endswith("s") and not s.endswith("ss") and len(s) > 3:
            sing = s[:-1]
            if sing in vocab_set and (sing, s) not in NEVER_MERGE and sing not in PROTECTED_EXACT:
                merges.append({"keep": sing, "merge_from": s, "reason": "plural normalisation"})
                merged_from.add(s)

    # 4. Automated scan for spaces and dots normalisation
    clean_map: dict[str, str] = {}
    for s in vocab:
        if s in merged_from or s in PROTECTED_EXACT:
            continue
        c = s.replace(" ", "").replace(".", "").replace("-", "")
        if c in clean_map:
            orig = clean_map[c]
            if (orig, s) not in NEVER_MERGE and orig != s:
                # keep canonical
                keep, m_from = (orig, s) if len(orig) <= len(s) else (s, orig)
                if m_from not in merged_from:
                    merges.append({"keep": keep, "merge_from": m_from, "reason": "spaces and dots normalisation"})
                    merged_from.add(m_from)
        else:
            clean_map[c] = s

    # 5. Automated rapidfuzz ratio >= 92
    for i in range(len(vocab)):
        s1 = vocab[i]
        if s1 in merged_from or s1 in PROTECTED_EXACT:
            continue
        for j in range(i + 1, len(vocab)):
            s2 = vocab[j]
            if s2 in merged_from or s2 in PROTECTED_EXACT:
                continue
            if (s1, s2) in NEVER_MERGE or (s2, s1) in NEVER_MERGE:
                continue
            ratio = fuzz.ratio(s1, s2)
            if ratio >= 92:
                keep, m_from = (s1, s2) if len(s1) <= len(s2) else (s2, s1)
                if m_from not in merged_from:
                    merges.append({"keep": keep, "merge_from": m_from, "reason": f"rapidfuzz ratio {ratio:.1f}"})
                    merged_from.add(m_from)

    return merges


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    merges = find_merges()

    if merges or not OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["keep", "merge_from", "reason"])
            writer.writeheader()
            writer.writerows(merges)
        print(f"Generated {OUTPUT_PATH} with {len(merges)} proposed merges.")
    # Group by keep target
    from collections import defaultdict
    groups = defaultdict(list)
    for m in merges:
        groups[m["keep"]].append(m["merge_from"])

    print(f"Total duplicate groups: {len(groups)}")
    for k, v in sorted(groups.items()):
        print(f"  {k} <- {', '.join(v)}")


if __name__ == "__main__":
    main()
