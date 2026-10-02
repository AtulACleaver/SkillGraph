import pandas as pd
import re
import json
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
        except Exception as e:
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
    # Load data
    clean_df = pd.read_parquet('data/clean.parquet')
    baskets_df = pd.read_parquet('data/baskets.parquet')
    
    # Ensure posting_id matches type
    if 'jobId' in clean_df.columns:
        clean_df['posting_id'] = clean_df['jobId'].astype(str)
        
    baskets_df['posting_id'] = baskets_df['posting_id'].astype(str)
    
    # Apply role families
    patterns = load_families('taxonomy/role_families.csv')
    clean_df['role_family'] = clean_df['title'].apply(lambda x: label_title(x, patterns))
    
    # Print distribution
    dist = clean_df['role_family'].value_counts(dropna=False)
    print("\nRole family distribution (before dropping < 500):")
    print(dist)
    
    # Drop families under 500 rows
    valid_families = dist[dist >= 500].index.tolist()
    # Remove NaN from valid_families if present
    valid_families = [f for f in valid_families if pd.notna(f)]
    
    # Unmatched
    unmatched = clean_df[clean_df['role_family'].isna()]
    unmatched_pct = len(unmatched) / len(clean_df) * 100
    print(f"\nRows matching no family: {len(unmatched)} ({unmatched_pct:.1f}%)")
    
    # Join with baskets
    df = pd.merge(clean_df, baskets_df, on='posting_id', how='left')
    
    dataset_df = df[df['role_family'].isin(valid_families)].copy()
    
    print(f"\nFinal labelled rows for dataset.parquet: {len(dataset_df)}")
    print(f"Role families included: {len(valid_families)}")
    
    # Select columns for dataset.parquet
    cols = ['posting_id', 'skill_ids', 'role_family', 'experience_band', 'companyName', 'location']
    dataset_df = dataset_df[cols].rename(columns={'companyName': 'company', 'location': 'location_raw'})
    
    # Save dataset.parquet
    dataset_df.to_parquet('data/dataset.parquet', index=False)
    
    # Write artifacts/skill_vocab.json
    vocab = norm._canonical
    # _canonical is {id: string}. Sort by id to maintain deterministic order
    sorted_vocab = [vocab[k] for k in sorted(vocab.keys())]
    
    with open('artifacts/skill_vocab.json', 'w') as f:
        json.dump(sorted_vocab, f, indent=2)
    
    print(f"Wrote skill_vocab.json with {len(sorted_vocab)} skills.")

if __name__ == '__main__':
    main()
