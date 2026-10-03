import json
import os

import numpy as np
import pandas as pd
import pytest

import etl.normalize as norm


def setup_module(module):
    # For CI tests, use the mock vocab
    norm._vocab = ["python", "java", "sql"]
    norm._clean_map = {"python": 0, "java": 1, "sql": 2}
    norm._exact_map = {}
    norm._fuzzy_cache = {}
    norm._aliases = {}

def test_skills_to_vector_empty():
    vec, unmapped = norm.skills_to_vector([])
    assert vec.sum() == 0
    assert not unmapped

def test_skills_to_vector_unknown():
    vec, unmapped = norm.skills_to_vector(["unknown_skill_xyz", ""])
    assert vec.sum() == 0
    assert "unknown_skill_xyz" in unmapped
    assert "" not in unmapped

def test_skills_to_vector_dedupe():
    vec, unmapped = norm.skills_to_vector(["python", "Python", "PYTHON "])
    assert vec.sum() == 1
    assert vec[0] == 1
    assert not unmapped

@pytest.mark.skipif(not os.path.exists('artifacts/skill_vocab.json') or not os.path.exists('data/clean.parquet'),
                    reason="Real artifacts not found")
def test_real_artifacts():
    # Load real vocab
    with open('artifacts/skill_vocab.json', 'r') as f:
        real_vocab = json.load(f)
    
    norm.load_vocab(real_vocab)
    
    # 1. Every vocab name maps to its own index
    for i, name in enumerate(real_vocab):
        idx = norm.normalize_skill(name)
        assert idx == i, f"Vocab name {name} maps to {idx}, expected {i}"
        
    # 2. for 500 real postings, skills_to_vector equals that posting's row in the training matrix (baskets)
    clean_df = pd.read_parquet('data/clean.parquet').head(500)
    baskets_df = pd.read_parquet('data/baskets.parquet')
    
    # We need to map posting_id to skill_ids from baskets
    baskets_map = dict(zip(baskets_df['posting_id'].astype(str), baskets_df['skill_ids']))
    
    for idx, row in clean_df.iterrows():
        posting_id = str(row.get('jobId', idx))
        skills_str = row['tagsAndSkills']
        if pd.isna(skills_str):
            raw = []
        else:
            raw = [t.strip() for t in str(skills_str).split(',') if t.strip()]
            
        vec, _unmapped = norm.skills_to_vector(raw)
        
        expected_ids = set(baskets_map.get(posting_id, []))
        actual_ids = set(np.where(vec == 1)[0])
        
        assert actual_ids == expected_ids, f"Mismatch for {posting_id}: {actual_ids} != {expected_ids}"
