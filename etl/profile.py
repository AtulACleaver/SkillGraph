import os
import time

import matplotlib.pyplot as plt
import pandas as pd

from etl.paths import RAW_XLSX
from etl.stats import write_stage_stats


def main():
    t0 = time.time()
    os.makedirs('data', exist_ok=True)
    os.makedirs('docs', exist_ok=True)

    print(f"Loading excel file from {RAW_XLSX}...")
    df = pd.read_excel(RAW_XLSX)

    print("Saving to parquet...")
    df.to_parquet('data/raw.parquet', index=False)

    print("Writing audit doc...")
    with open('docs/data_audit.md', 'w') as f:
        f.write("# Data Audit\n\n")
        f.write(f"Total Rows: {len(df):,}\n\n")

        f.write("## Columns\n")
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            distinct_count = df[col].nunique()
            examples = df[col].dropna().unique()[:5].tolist()

            f.write(f"### {col}\n")
            f.write(f"- Dtype: {dtype}\n")
            f.write(f"- Null Count: {null_count:,} ({null_pct:.2f}%)\n")
            f.write(f"- Distinct Count: {distinct_count:,}\n")
            f.write(f"- Examples: {examples}\n\n")

        skills_col = 'tagsAndSkills'
        if skills_col not in df.columns:
            for col in df.columns:
                if 'skill' in col.lower() or 'tag' in col.lower():
                    skills_col = col
                    break

        empty_skills = df[df[skills_col].isnull() | (df[skills_col].astype(str).str.strip() == '')]
        f.write("## Skills\n")
        f.write(f"- Rows with empty/null skills: {len(empty_skills):,}\n")

        # Split skills
        skills_series = df[skills_col].dropna().astype(str)
        all_tokens = skills_series.str.split(',').explode().str.strip()
        all_tokens = all_tokens[all_tokens != '']
        token_counts = all_tokens.value_counts()

        f.write(f"- Distinct raw tokens: {len(token_counts):,}\n")

        MIN_TOKEN_COUNT = 5
        top_tokens = token_counts[token_counts >= MIN_TOKEN_COUNT]
        top_tokens.to_csv('data/top_tokens.csv', header=['count'])
        f.write(f"- Tokens exported (count >= {MIN_TOKEN_COUNT}): {len(top_tokens):,} "
                f"covering {top_tokens.sum() / token_counts.sum():.1%} of mentions\n\n")

        f.write("## Baskets Audit: 34,569 vs 30,134\n\n")
        f.write(
            "The original project plan stated 30,134 baskets, whereas data-v3 produced 34,569 baskets. "
            "The difference arose from how tech postings were filtered and cleaned across project stages.\n\n"
            "In the initial exploratory plan, a draft filter selected 33,724 postings based on skill tags. "
            "After dropping exact duplicates and empty skill lists, 30,134 rows survived. The plan assumed "
            "mining baskets would match that preliminary count of 30,134 postings (comprising 13,185 generic "
            "software engineer rows, 4,086 unmatched rows, and 12,863 role-labelled rows).\n\n"
            "In the pipeline implementation in `etl/clean.py`, the tech filter checked 32 keywords from "
            "`etl/tech_terms.txt` across both `title` and `tagsAndSkills` columns of "
            "`data/raw/indian-job-market-dataset-2025.xlsx`. This broader check identified 38,271 candidate "
            "tech postings. Cleaning dropped 100 exact duplicates, 80 rows with no skills after splitting, "
            "and 3,522 reposts, leaving 34,569 rows saved to `data/clean.parquet`.\n\n"
            "In `etl/label.py`, the `build_baskets` function created one basket per row of `data/clean.parquet`, "
            "saving 34,569 records to `data/baskets.parquet`. In that file, 32,949 baskets contain one or more "
            "canonical skill IDs and 1,620 contain empty lists after mapping against `artifacts/skill_vocab.json`.\n"
        )

        # Plot frequency curve
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(token_counts)), token_counts.values)
        plt.yscale('log')
        plt.title('Skill Token Frequency Curve')
        plt.xlabel('Token Rank')
        plt.ylabel('Frequency (log scale)')
        plt.savefig('docs/token_frequency.png')

    elapsed = time.time() - t0
    write_stage_stats(
        stage="profile",
        rows_in=len(df),
        rows_out=len(df),
        drops_by_reason={},
        elapsed_seconds=elapsed,
        output_files=['data/raw.parquet', 'data/top_tokens.csv'],
    )
    print("Done!")


if __name__ == '__main__':
    main()
