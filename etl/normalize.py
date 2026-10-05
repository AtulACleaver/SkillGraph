import csv
import json
import string

import numpy as np
from rapidfuzz import fuzz, process

from etl.paths import ARTIFACTS_DIR, TAXONOMY_DIR

_STRIP = str.maketrans('', '', string.punctuation.replace('+', '').replace('#', ''))

def _clean_token(t):
    if t is None: return ""
    t = str(t).lower().strip()
    if t == 'nan': return ""
    return ' '.join(t.translate(_STRIP).split())

_aliases = {}
def load_aliases():
    if _aliases: return
    alias_path = TAXONOMY_DIR / 'skill_aliases.csv'
    if not alias_path.exists():
        return
    with open(alias_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            alias = row.get('alias')
            canonical = row.get('canonical')
            if not alias or not canonical: continue
            cleaned_alias = _clean_token(alias)
            if cleaned_alias:
                _aliases[cleaned_alias] = _clean_token(canonical)

_vocab = []
_clean_map = {}
_exact_map = {}
_fuzzy_cache = {}

def load_vocab(vocab_list=None):
    global _vocab, _clean_map, _exact_map, _fuzzy_cache
    if vocab_list is None:
        vocab_path = ARTIFACTS_DIR / 'skill_vocab.json'
        if not vocab_path.exists():
            raise FileNotFoundError(f"Missing {vocab_path}")
        with open(vocab_path, 'r') as f:
            _vocab = json.load(f)
    else:
        _vocab = vocab_list
        
    _clean_map = {name: i for i, name in enumerate(_vocab)}
    _exact_map = {}
    _fuzzy_cache = {}
    load_aliases()

def skills_to_vector(raw: list[str]) -> tuple[np.ndarray, list[str]]:
    if isinstance(raw, str):
        raise TypeError("skills_to_vector expects a list of strings")
    if not _vocab:
        load_vocab()
    vec = np.zeros(len(_vocab), dtype=int)
    unmapped = []
    
    if not raw:
        return vec, unmapped
        
    seen_ids = set()
    for t in raw:
        i = normalize_skill(t)
        if i is not None:
            seen_ids.add(i)
        else:
            if str(t).strip():
                unmapped.append(str(t).strip())
                
    for i in seen_ids:
        vec[i] = 1
                
    return vec, unmapped

def normalize_skill(raw: str) -> int | None:
    if not _vocab:
        load_vocab()
    if raw is None: return None
    raw = str(raw).strip()
    if not raw or raw.lower() == 'nan': return None
    
    if raw in _exact_map:
        return _exact_map[raw]
        
    cleaned = _clean_token(raw)
    if not cleaned: return None
    
    if cleaned in _clean_map:
        _exact_map[raw] = _clean_map[cleaned]
        return _clean_map[cleaned]
        
    if cleaned in _aliases:
        target = _aliases[cleaned]
        if target in _clean_map:
            _exact_map[raw] = _clean_map[target]
            return _clean_map[target]
            
    if cleaned in _fuzzy_cache:
        return _fuzzy_cache[cleaned]
        
    if len(cleaned) < 4:
        _fuzzy_cache[cleaned] = None
        return None
        
    choices = [c for c in _vocab if len(c) >= 4]
    if not choices:
        return None
        
    match = process.extractOne(cleaned, choices, scorer=fuzz.ratio, score_cutoff=88)
    if match:
        matched_str = match[0]
        match_id = _clean_map[matched_str]
        _fuzzy_cache[cleaned] = match_id
        _exact_map[raw] = match_id
        return match_id
        
    _fuzzy_cache[cleaned] = None
    return None

def build_vocab(tech_series) -> list[str]:
    load_aliases()
    counts = {}
    
    for tags in tech_series.dropna():
        tokens = [t.strip() for t in str(tags).split(',') if t.strip()]
        for t in tokens:
            cleaned = _clean_token(t)
            if not cleaned: continue
            canonical = _aliases.get(cleaned, cleaned)
            counts[canonical] = counts.get(canonical, 0) + 1
            
    total_mass = sum(counts.values())
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    cumulative = 0
    vocab = []
    for name, count in sorted_counts:
        cumulative += count
        vocab.append(name)
        if len(vocab) >= 800 and (cumulative / total_mass) >= 0.75:
            break
        if len(vocab) == 1200:
            break
            
    print(f"Vocab size: {len(vocab)}")
    print(f"Mapped mass: {cumulative:,} / {total_mass:,} ({cumulative/total_mass:.1%})")
    return vocab

def build_baskets(clean_df):
    import pandas as pd
    baskets = []
    for idx, row in clean_df.iterrows():
        skills_str = row['tagsAndSkills']
        posting_id = str(row.get('jobId', idx))
        
        if pd.isna(skills_str):
            baskets.append({'posting_id': posting_id, 'skill_ids': []})
            continue
            
        tokens = [t.strip() for t in str(skills_str).split(',') if t.strip()]
        skill_ids = set()
        for t in tokens:
            i = normalize_skill(t)
            if i is not None:
                skill_ids.add(i)
        
        baskets.append({'posting_id': posting_id, 'skill_ids': list(skill_ids)})
        
    return pd.DataFrame(baskets)
