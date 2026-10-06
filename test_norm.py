import time
from collections import Counter

import pandas as pd

from etl.normalize import (
    _aliases,
    _clean_map,
    _clean_token,
    load_vocab,
    normalize_skill,
)

t0 = time.time()
raw = pd.read_parquet('data/clean.parquet')
all_tokens = []
for s in raw['tagsAndSkills'].dropna():
    all_tokens.extend([t.strip().lower() for t in s.split(',') if t.strip()])

token_counts = Counter(all_tokens)
print(f"Total tokens: {len(all_tokens)}, Unique tokens: {len(token_counts)}, Time so far: {time.time() - t0:.2f}s")

load_vocab()
unmapped = []
mapped_mass = 0
fuzzy_count = 0
for i, (t, count) in enumerate(token_counts.items()):
    cleaned = _clean_token(t)
    if not cleaned: continue
    if cleaned in _clean_map or cleaned in _aliases:
        mapped_mass += count
    else:
        if normalize_skill(t) is not None:
            fuzzy_count += count
            mapped_mass += count
    if i % 5000 == 0:
        print(f"Processed {i} items...")

print(f"Mapped mass: {mapped_mass}, fuzzy: {fuzzy_count}, Total time: {time.time() - t0:.2f}s")
