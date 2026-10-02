import re

import pandas as pd

DROP_REASONS = {}

def drop(df, mask, reason):
    n = int(mask.sum())
    if n > 0:
        DROP_REASONS[reason] = DROP_REASONS.get(reason, 0) + n
    return df[~mask]

def main():
    df = pd.read_parquet('data/raw.parquet')
    
    # 1. Filter to tech subset
    with open('etl/tech_terms.txt', 'r') as f:
        raw_terms = [line.strip().lower() for line in f if line.strip()]
        
    def make_pattern(term):
        term = re.escape(term.strip())
        pat = term
        if re.match(r'^\w', term): pat = r'\b' + pat
        if re.search(r'\w$', term): pat = pat + r'\b'
        return pat

    patterns = [make_pattern(t) for t in raw_terms]
    pattern = re.compile('|'.join(patterns), re.IGNORECASE)
    
    def is_tech(row):
        title = str(row.get('title', ''))
        skills = str(row.get('tagsAndSkills', ''))
        return bool(pattern.search(title) or pattern.search(skills))
        
    mask = ~df.apply(is_tech, axis=1)
    df = drop(df, mask, "Not in tech subset")

    # 2. Exact duplicates
    mask = df.duplicated()
    df = drop(df, mask, "Exact duplicates")

    # 3. No skills after splitting
    def has_no_skills(val):
        if pd.isna(val): return True
        tokens = [t.strip() for t in str(val).split(',')]
        return len([t for t in tokens if t]) == 0
        
    mask = df['tagsAndSkills'].apply(has_no_skills)
    df = drop(df, mask, "No skills after splitting")

    # 4. Reposts (same title, companyName, tagsAndSkills)
    def parse_days_ago(text):
        text = str(text).lower()
        if 'just now' in text or 'few hours' in text or 'today' in text: return 0
        match = re.search(r'(\d+)\s+day', text)
        if match: return int(match.group(1))
        match = re.search(r'(\d+)\s+month', text)
        if match: return int(match.group(1)) * 30
        return 999
        
    if 'jobUploaded' in df.columns:
        df['_days_ago'] = df['jobUploaded'].apply(parse_days_ago)
        df = df.sort_values('_days_ago', ascending=False)
        
    mask = df.duplicated(subset=['title', 'companyName', 'tagsAndSkills'], keep='first')
    df = drop(df, mask, "Reposts")
    
    if '_days_ago' in df.columns:
        df = df.drop(columns=['_days_ago'])

    # 5. Experience
    def parse_exp(val):
        val = str(val).lower()
        match = re.search(r'(\d+)\s*-\s*(\d+)', val)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None, None
        
    parsed = df['experience'].apply(parse_exp)
    df['min_years'] = parsed.apply(lambda x: x[0] if x else None)
    df['max_years'] = parsed.apply(lambda x: x[1] if x else None)
    
    mask = (df['min_years'] > 40) | (df['max_years'] > 40)
    bad_exp = df[mask]
    if len(bad_exp) > 0:
        print(f"Logged {len(bad_exp)} rows with experience > 40 years as parse failure")
    df = drop(df, mask, "Experience parse failure")

    # 6. Experience band
    def get_band(min_y):
        if pd.isna(min_y): return None
        if min_y <= 1: return 'fresher'
        if min_y <= 4: return 'junior'
        if min_y <= 8: return 'mid'
        return 'senior'
        
    df['experience_band'] = df['min_years'].apply(get_band)

    # 7. Normalize company names
    def norm_company(name):
        if pd.isna(name): return name
        name = str(name).lower().strip()
        name = re.sub(r'\s+', ' ', name)
        name = re.sub(r'\s+pvt\s+ltd\.?$', '', name)
        name = re.sub(r'\s+private\s+limited\.?$', '', name)
        name = re.sub(r'\s+ltd\.?$', '', name)
        name = re.sub(r'\s+limited\.?$', '', name)
        return name.strip()
        
    df['companyName'] = df['companyName'].apply(norm_company)

    # 8. Save
    df.to_parquet('data/clean.parquet', index=False)

    # 9. Print
    for reason, n in DROP_REASONS.items():
        print(f"{n:>7,}  {reason}")
    print(f"{len(df):>7,}  rows surviving")

if __name__ == '__main__':
    main()
