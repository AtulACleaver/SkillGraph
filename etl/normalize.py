import pandas as pd
import re
import string
from rapidfuzz import process, fuzz

# Canonical list and aliases
# We will build it on module load to keep the API clean.
_canonical = {}  # id -> string
_exact_map = {}  # string -> id
_clean_map = {}  # string -> id
_aliases = {
    # "Aryan's alias table" mock - you can add to this
    'reactjs': 'react',
    'react.js': 'react',
    'react js': 'react',
    'node.js': 'node',
    'nodejs': 'node'
}

def _clean_token(t):
    t = str(t).lower().strip()
    return t.translate(str.maketrans('', '', string.punctuation))

def init_registry():
    global _canonical, _exact_map, _clean_map
    if _canonical: return # already init
    
    try:
        df = pd.read_csv('data/top_tokens.csv')
    except Exception:
        return
        
    next_id = 1
    for token in df['tagsAndSkills'].dropna():
        cleaned = _clean_token(token)
        if cleaned not in _clean_map.values():
            # register new canonical
            _canonical[next_id] = cleaned
            _exact_map[token] = next_id
            _clean_map[cleaned] = next_id
            next_id += 1
        else:
            # map exact variant to existing cleaned ID
            _exact_map[token] = _clean_map[cleaned]

    # map aliases to ids if target exists
    for alias, target in _aliases.items():
        ct = _clean_token(target)
        if ct in _clean_map:
            _exact_map[alias] = _clean_map[ct]
            _clean_map[_clean_token(alias)] = _clean_map[ct]

init_registry()

# Cache for rapidfuzz to avoid re-searching
_fuzzy_cache = {}

def normalize_skill(raw: str) -> int | None:
    if pd.isna(raw):
        return None
    
    raw = str(raw).strip()
    
    # 1. Exact match
    if raw in _exact_map:
        return _exact_map[raw]
        
    # 2. Lowercase and strip punctuation
    cleaned = _clean_token(raw)
    if cleaned in _clean_map:
        return _clean_map[cleaned]
        
    # 3. Alias table (handled during init if exact/cleaned, but just in case)
    if cleaned in _aliases:
        target = _aliases[cleaned]
        tc = _clean_token(target)
        if tc in _clean_map:
            return _clean_map[tc]
            
    # 4. Fuzzy match with rapidfuzz
    if cleaned in _fuzzy_cache:
        return _fuzzy_cache[cleaned]
        
    choices = list(_canonical.values())
    if not choices:
        return None
        
    # Extract one best match above threshold 85
    match = process.extractOne(cleaned, choices, scorer=fuzz.WRatio, score_cutoff=85)
    if match:
        matched_str = match[0]
        match_id = _clean_map[matched_str]
        _fuzzy_cache[cleaned] = match_id
        return match_id
        
    # 5. Give up
    return None

def normalize_many(tokens: list[str]) -> list[int]:
    result = []
    for t in tokens:
        i = normalize_skill(t)
        if i is not None:
            result.append(i)
    return list(set(result)) # deduplicate

def _run_script():
    # Only run when executed as a script
    print("Normalizing tokens in dataset...")
    df = pd.read_parquet('data/clean.parquet')
    
    unmapped_counts = {}
    total_mass = 0
    mapped_mass = 0
    
    baskets = []
    
    # We will process each row
    for idx, row in df.iterrows():
        skills_str = row['tagsAndSkills']
        posting_id = row.get('jobId', idx) # use jobId or index
        
        if pd.isna(skills_str):
            baskets.append({'posting_id': posting_id, 'skill_ids': []})
            continue
            
        tokens = [t.strip() for t in str(skills_str).split(',') if t.strip()]
        skill_ids = set()
        
        for t in tokens:
            total_mass += 1
            i = normalize_skill(t)
            if i is not None:
                skill_ids.add(i)
                mapped_mass += 1
            else:
                unmapped_counts[t] = unmapped_counts.get(t, 0) + 1
                
        baskets.append({'posting_id': posting_id, 'skill_ids': list(skill_ids)})
        
    # 5. Write baskets.parquet
    out_df = pd.DataFrame(baskets)
    out_df.to_parquet('data/baskets.parquet', index=False)
    
    # 4. Write unmapped.csv
    unmapped_df = pd.DataFrame(list(unmapped_counts.items()), columns=['token', 'count'])
    unmapped_df = unmapped_df.sort_values('count', ascending=False)
    unmapped_df.to_csv('data/unmapped.csv', index=False)
    
    # 6. Measure and print token mass
    pct = (mapped_mass / total_mass) * 100 if total_mass > 0 else 0
    print(f"Total token mass: {total_mass:,}")
    print(f"Mapped token mass: {mapped_mass:,}")
    print(f"Coverage: {pct:.2f}% (Target: >70%)")

if __name__ == '__main__':
    _run_script()
