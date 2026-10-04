import json
import re

import pandas as pd

import etl.normalize as norm


def load_families(csv_path):
    df = pd.read_csv(csv_path)
    if 'priority' in df.columns:
        df = df.sort_values('priority')
    patterns = []
    for _, row in df.iterrows():
        if pd.isna(row['pattern']): continue
        try:
            pat = re.compile(row['pattern'], re.IGNORECASE)
            patterns.append((pat, row['role_family']))
        except Exception as e:  # noqa: BLE001
            print(f"Failed to compile pattern {row['pattern']}: {e}")
    return patterns

def label_title(title, patterns):
    if pd.isna(title):
        return None
    for pat, family in patterns:
        if pat.search(str(title)):
            return family
    return None

def main():
    print("Labeling dataset...")
    clean_df = pd.read_parquet('data/clean.parquet')
    
    if 'jobId' in clean_df.columns:
        clean_df['posting_id'] = clean_df['jobId'].astype(str)
    
    patterns = load_families('taxonomy/role_families.csv')
    
    clean_df['role_family_raw'] = clean_df['title'].apply(lambda x: label_title(x, patterns))
    clean_df['role_family'] = clean_df['role_family_raw'].replace({'Database / DBA': 'Data / BI Analyst'})
    
    dist = clean_df['role_family'].value_counts(dropna=False)
    print("\nRole family distribution (all rows):")
    print(dist)
    
    valid_families = [f for f in dist.index if pd.notna(f) and f != "Software Engineer (generic)"]
    
    for f in valid_families:
        if dist[f] < 400:
            raise ValueError(f"STOP: Family '{f}' has under 400 rows ({dist[f]}).")

    tech_df = clean_df[clean_df['role_family'].isin(valid_families)].copy()
    
    unmatched = clean_df[clean_df['role_family_raw'].isna()]
    if len(unmatched) > 0.25 * len(tech_df):
        print(f"WARNING: Unmatched rows ({len(unmatched)}) exceed 25% of tech rows ({len(tech_df)}).")
        
    print(f"\nExcluded rows: {len(unmatched)} (unmatched)")
    print(f"Excluded rows: {dist.get('Software Engineer (generic)', 0)} (Software Engineer (generic))")

    print("\nBuilding vocab...")
    vocab = norm.build_vocab(tech_df['tagsAndSkills'])
    with open('artifacts/skill_vocab.json', 'w') as f:
        json.dump(vocab, f, indent=2)
        
    norm.load_vocab(vocab)
    
    print("Building skills_autocomplete.json...")
    display_map = {
        'sql': 'SQL', 'aws': 'AWS', 'power bi': 'Power BI', 'node': 'Node.js',
        'qa': 'QA', 'ml': 'ML', 'css': 'CSS', 'javascript': 'JavaScript',
        'html': 'HTML', 'cicd': 'CI/CD'
    }
    
    reverse_aliases = {}
    for alias, canonical in norm._aliases.items():
        if canonical not in reverse_aliases:
            reverse_aliases[canonical] = []
        reverse_aliases[canonical].append(alias)
        
    autocomplete = []
    for i, name in enumerate(vocab):
        display = display_map.get(name, name.title())
        aliases = reverse_aliases.get(name, [])
        autocomplete.append({
            "id": i,
            "name": name,
            "display": display,
            "aliases": aliases
        })
        
    with open('artifacts/skills_autocomplete.json', 'w') as f:
        json.dump(autocomplete, f, indent=2)

    print("Building baskets...")
    baskets_df = norm.build_baskets(clean_df)
    
    assert clean_df['posting_id'].is_unique, "posting_id is not unique in clean_df"
    assert baskets_df['posting_id'].is_unique, "posting_id is not unique in baskets_df"
    assert set(clean_df['posting_id']) == set(baskets_df['posting_id']), "posting_ids differ"
    
    baskets_df.to_parquet('data/baskets.parquet', index=False)
    
    dataset_df = pd.merge(tech_df, baskets_df, on='posting_id', how='left')
    cols = ['posting_id', 'skill_ids', 'role_family', 'experience_band', 'companyName', 'location']
    dataset_df = dataset_df[cols].rename(columns={'companyName': 'company', 'location': 'location_raw'})
    
    print(f"\nFinal labelled rows for dataset.parquet: {len(dataset_df)}")
    dataset_df.to_parquet('data/dataset.parquet', index=False)

if __name__ == '__main__':
    main()
