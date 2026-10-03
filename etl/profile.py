import os

import matplotlib.pyplot as plt
import pandas as pd

os.makedirs('data', exist_ok=True)
os.makedirs('docs', exist_ok=True)

print("Loading excel file...")
df = pd.read_excel('indian-job-market-dataset-2025.xlsx')

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
        
    skills_col = 'tagsAndSkills' # assuming this from the prompt
    if skills_col not in df.columns:
        # try to find a skill col
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
    # Handle empty strings after strip
    all_tokens = all_tokens[all_tokens != '']
    token_counts = all_tokens.value_counts()
    
    f.write(f"- Distinct raw tokens: {len(token_counts):,}\n")
    
    # Export every token seen at least MIN_TOKEN_COUNT times.
    # (A fixed top-1500 cut covered only ~58% of skill mentions.)
    MIN_TOKEN_COUNT = 5
    top_tokens = token_counts[token_counts >= MIN_TOKEN_COUNT]
    top_tokens.to_csv('data/top_tokens.csv', header=['count'])
    f.write(f"- Tokens exported (count >= {MIN_TOKEN_COUNT}): {len(top_tokens):,} "
            f"covering {top_tokens.sum() / token_counts.sum():.1%} of mentions\n")
    
    # Plot frequency curve
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(token_counts)), token_counts.values)
    plt.yscale('log')
    plt.title('Skill Token Frequency Curve')
    plt.xlabel('Token Rank')
    plt.ylabel('Frequency (log scale)')
    plt.savefig('docs/token_frequency.png')
    
print("Done!")
