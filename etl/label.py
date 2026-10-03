"""
Role labelling module: maps job titles to canonical role families using taxonomy/role_families.csv.
"""
import os
import re

import pandas as pd


def load_role_family_patterns(taxonomy_file: str = "taxonomy/role_families.csv") -> list[dict]:
    """Load role family matching rules ordered by priority."""
    if not os.path.exists(taxonomy_file):
        return []
    df = pd.read_csv(taxonomy_file)
    # Sort by priority ascending (priority 1 first)
    if "priority" in df.columns:
        df = df.sort_values("priority")
    return df.to_dict("records")


def assign_role_family(title: str, patterns: list[dict]) -> str:
    """Match job title against role family patterns. First match wins."""
    if not title or pd.isna(title):
        return "Unmatched"
    
    title_str = str(title).lower().strip()
    for rule in patterns:
        pat = str(rule.get("pattern", "")).lower()
        role = rule.get("role_family", "Unmatched")
        if not pat:
            continue
        # Use regex search if valid, otherwise fallback to substring
        try:
            if re.search(pat, title_str, re.IGNORECASE):
                return role
        except re.error:
            if pat in title_str:
                return role
    return "Unmatched"


def label_dataset(
    clean_file: str = "data/clean.parquet",
    baskets_file: str = "data/baskets.parquet",
    output_file: str = "data/dataset.parquet",
    taxonomy_file: str = "taxonomy/role_families.csv",
) -> pd.DataFrame:
    """Create labelled dataset combining clean postings, baskets, and role family labels."""
    if not os.path.exists(clean_file) or not os.path.exists(baskets_file):
        print("Required input files (clean.parquet / baskets.parquet) not found.")
        return pd.DataFrame()

    df_clean = pd.read_parquet(clean_file)
    df_baskets = pd.read_parquet(baskets_file)
    patterns = load_role_family_patterns(taxonomy_file)

    # Merge on posting_id or index
    if "posting_id" in df_clean.columns and "posting_id" in df_baskets.columns:
        df = pd.merge(df_clean, df_baskets, on="posting_id", how="inner")
    else:
        df = df_clean.copy()
        df["skill_ids"] = df_baskets["skill_ids"]

    # Assign role family
    title_col = "title" if "title" in df.columns else "jobTitle"
    df["role_family"] = df[title_col].apply(lambda t: assign_role_family(t, patterns))

    # Save final dataset
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_parquet(output_file, index=False)
    print(f"Labelled {len(df):,} rows -> saved to {output_file}")
    return df


if __name__ == "__main__":
    if os.path.exists("data/clean.parquet") and os.path.exists("data/baskets.parquet"):
        label_dataset()