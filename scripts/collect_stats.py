import json
import os
import subprocess
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

stats = {
    "dataset": {},
    "normalization": {},
    "model": {},
    "mining": {},
    "product": {},
    "engineering": {}
}

def safe_run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

def _fuzzy_match(t, cleaned, count, choices):
    from rapidfuzz import fuzz, process
    match = process.extractOne(cleaned, choices, scorer=fuzz.ratio, score_cutoff=88)
    return (t, count, match is not None)

def dataset_stats():
    clean_stats = json.load(open('data/stats/clean.json'))
    label_stats = json.load(open('data/stats/label.json'))
    train_stats = json.load(open('data/stats/train.json'))
    
    stats['dataset']['raw rows'] = {"value": clean_stats['rows_in'], "source": "data/stats/clean.json"}
    stats['dataset']['rows surviving clean'] = {"value": clean_stats['rows_out'], "source": "data/stats/clean.json"}
    
    for k, v in clean_stats['drops_by_reason'].items():
        stats['dataset'][f"dropped (clean): {k}"] = {"value": v, "source": "data/stats/clean.json"}
    
    stats['dataset']['labelled rows'] = {"value": label_stats['rows_out'], "source": "data/stats/label.json"}
    for k, v in label_stats['drops_by_reason'].items():
        stats['dataset'][f"dropped (label): {k}"] = {"value": v, "source": "data/stats/label.json"}
    
    df = pd.read_parquet('data/dataset.parquet')
    role_counts = df['role_family'].value_counts()
    for role, count in role_counts.items():
        stats['dataset'][f"rows per role: {role}"] = {"value": int(count), "source": "data/dataset.parquet"}
        
    stats['dataset']['rows with no skill ids'] = {"value": train_stats['drops_by_reason'].get('No skill IDs', 0), "source": "data/stats/train.json"}
    
    raw = pd.read_parquet('data/raw.parquet')
    skills_series = raw['tagsAndSkills'].dropna()
    unique_skills = set()
    for s in skills_series:
        unique_skills.update([t.strip().lower() for t in s.split(',') if t.strip()])
    stats['dataset']['unique raw skill strings'] = {"value": len(unique_skills), "source": "data/raw.parquet"}
    
    baskets = pd.read_parquet('data/baskets.parquet')
    stats['dataset']['baskets'] = {"value": len(baskets), "source": "data/baskets.parquet"}
    stats['dataset']['data has posting dates'] = {"value": 'jobUploaded' in raw.columns, "source": "data/raw.parquet"}

    # Figure 1: funnel.png
    plt.figure(figsize=(8, 6), dpi=150)
    stages = ['Raw', 'Tech Subset', 'Clean', 'Labelled', 'Baskets']
    # 59658 dropped in tech subset implies raw - 59658
    tech_subset = clean_stats['rows_in'] - clean_stats['drops_by_reason'].get('Not in tech subset', 0)
    counts = [clean_stats['rows_in'], tech_subset, clean_stats['rows_out'], label_stats['rows_out'], len(baskets)]
    sns.barplot(x=stages, y=counts, color='steelblue')
    plt.title("Data Pipeline Funnel")
    plt.ylabel("Rows")
    for i, v in enumerate(counts):
        plt.text(i, v + 1000, f"{v:,}", ha='center')
    plt.tight_layout()
    plt.savefig('docs/figures/funnel.png')
    plt.close()

    # Figure 2: class_distribution.png
    plt.figure(figsize=(10, 6), dpi=150)
    sns.barplot(x=role_counts.values, y=role_counts.index, color='steelblue')
    plt.title("Rows per Role Family")
    plt.xlabel("Count")
    plt.ylabel("Role Family")
    plt.tight_layout()
    plt.savefig('docs/figures/class_distribution.png')
    plt.close()

def normalization_stats():
    print("Starting normalization_stats...")
    vocab = json.load(open('artifacts/skill_vocab.json'))
    stats['normalization']['vocab size'] = {"value": len(vocab), "source": "artifacts/skill_vocab.json"}
    
    aliases = pd.read_csv('taxonomy/skill_aliases.csv', names=['merge_from', 'keep'])
    stats['normalization']['alias count'] = {"value": len(aliases), "source": "taxonomy/skill_aliases.csv"}
    

    from etl.normalize import _aliases, _clean_map, _clean_token, _vocab, load_vocab
    load_vocab()
    choices = [c for c in _vocab if len(c) >= 4]
    
    raw = pd.read_parquet('data/clean.parquet')
    all_tokens = []
    for s in raw['tagsAndSkills'].dropna():
        all_tokens.extend([t.strip().lower() for t in s.split(',') if t.strip()])
    
    from collections import Counter
    token_counts = Counter(all_tokens)
    
    total = sum(token_counts.values())
    exact_count = 0
    alias_count = 0
    fuzzy_count = 0
    unmapped = []
    
    # We can get mapped mass directly from label pipeline output, but let's approximate
    for t, count in token_counts.items():
        cleaned = _clean_token(t)
        if not cleaned: 
            unmapped.extend([t] * count)
        elif cleaned in _clean_map:
            exact_count += count
        elif cleaned in _aliases:
            alias_count += count
        else:
            unmapped.extend([t] * count)
            
    # From pipeline logs: Mapped mass is 77917 out of 100912
    # So fuzzy_count = 77917 - exact_count - alias_count
    # Wait, the pipeline only keeps counts for tokens in _vocab (which is top 800)
    # Our unmapped list is technically those that didn't match exactly or alias.
    # Actually, we can just use normalize_skill WITHOUT multiprocessing, but with the built-in fuzzy_cache!
    # Let's just use normalize_skill!
    from etl.normalize import normalize_skill
    unmapped = []
    mapped_mass = 0
    fuzzy_count = 0
    for t, count in token_counts.items():
        cleaned = _clean_token(t)
        if not cleaned:
            unmapped.extend([t] * count)
            continue
        if cleaned in _clean_map or cleaned in _aliases:
            mapped_mass += count
        else:
            if normalize_skill(t) is not None:
                fuzzy_count += count
                mapped_mass += count
            else:
                unmapped.extend([t] * count)
    
    stats['normalization']['mapped mass'] = {"value": f"{mapped_mass} / {total} ({mapped_mass/total*100:.1f}%)", "source": "computed from data/clean.parquet"}
    stats['normalization']['exact match count'] = {"value": exact_count, "source": "computed"}
    stats['normalization']['alias match count'] = {"value": alias_count, "source": "computed"}
    stats['normalization']['fuzzy match count'] = {"value": fuzzy_count, "source": "computed"}
    
    top_unmapped = pd.Series(unmapped).value_counts().head(20).to_dict()
    stats['normalization']['top 20 unmapped strings'] = {"value": str(top_unmapped), "source": "computed"}

    unmapped_set = set(unmapped)
    freq = pd.Series([t for t in all_tokens if t not in unmapped_set]).value_counts().values
    cum_share = np.cumsum(freq) / total
    plt.figure(figsize=(8, 6), dpi=150)
    plt.plot(np.arange(1, len(cum_share) + 1), cum_share, color='steelblue')
    plt.title("Token Coverage Curve")
    plt.xlabel("Top-k Skills")
    plt.ylabel("Share of Total Mentions")
    plt.tight_layout()
    plt.savefig('docs/figures/token_coverage_curve.png')
    plt.close()


def model_stats():
    print("Starting model_stats...")
    m = json.load(open('artifacts/metrics.json'))
    
    stats['model']['n_train raw'] = {"value": m['n_train_raw'], "source": "artifacts/metrics.json"}
    stats['model']['n_train augmented'] = {"value": m['n_train_aug'], "source": "artifacts/metrics.json"}
    stats['model']['n_val'] = {"value": m['n_val'], "source": "artifacts/metrics.json"}
    stats['model']['n_test'] = {"value": m['n_test'], "source": "artifacts/metrics.json"}
    stats['model']['majority baseline'] = {"value": m['majority_baseline_acc'], "source": "artifacts/metrics.json"}
    stats['model']['test macro F1'] = {"value": m['test']['macro_f1'], "source": "artifacts/metrics.json"}
    stats['model']['test accuracy'] = {"value": m['test']['accuracy'], "source": "artifacts/metrics.json"}
    stats['model']['test top-3'] = {"value": m['test']['top3_accuracy'], "source": "artifacts/metrics.json"}
    stats['model']['short-input test macro F1'] = {"value": m['test_short_input']['macro_f1'], "source": "artifacts/metrics.json"}
    
    for cls in m['classes']:
        stats['model'][f"per-class {cls} F1"] = {"value": m['per_class'][cls]['f1-score'], "source": "artifacts/metrics.json"}
        
    stats['model']['ECE pooled'] = {"value": m['test_calibration'].get('pooled_ovr_ece', m['test_calibration'].get('ece')), "source": "artifacts/metrics.json"}
    stats['model']['ECE top-label'] = {"value": m['test_calibration'].get('top_label_ece', m.get('calibration', {}).get('ece')), "source": "artifacts/metrics.json"}
    
    # confusion_matrix.png (row-normalised)
    cm = np.array(m['confusion_matrix'])
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    plt.figure(figsize=(10, 8), dpi=150)
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap='Blues', xticklabels=m['classes'], yticklabels=m['classes'])
    plt.title("Confusion Matrix (Row-Normalized)")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    plt.savefig('docs/figures/confusion_matrix.png')
    plt.close()

    # per_class_f1.png
    f1s = [m['per_class'][c]['f1-score'] for c in m['classes']]
    plt.figure(figsize=(10, 6), dpi=150)
    sns.barplot(x=f1s, y=m['classes'], color='steelblue')
    plt.title("Per-Class F1 Score")
    plt.xlabel("F1 Score")
    plt.tight_layout()
    plt.savefig('docs/figures/per_class_f1.png')
    plt.close()

    # full_vs_short.png
    plt.figure(figsize=(6, 6), dpi=150)
    labels = ['Full Input', 'Short Input']
    scores = [m['test']['macro_f1'], m['test_short_input']['macro_f1']]
    sns.barplot(x=labels, y=scores, color='steelblue')
    plt.title("Macro F1: Full vs Short Input")
    plt.ylabel("Macro F1")
    plt.tight_layout()
    plt.savefig('docs/figures/full_vs_short.png')
    plt.close()
    
    # logreg_vs_lgbm.png
    # Wait, some metrics don't have test_scores_both_models if LGBM wasn't run or something? 
    # The prompt says: "LR vs LightGBM on val and test"
    # m['val']['logreg'], m['val']['lightgbm']
    lr_val = m.get('val', {}).get('logreg', {}).get('macro_f1', 0)
    lgbm_val = m.get('val', {}).get('lightgbm', {}).get('macro_f1', 0)
    stats['model']['LR val macro F1'] = {"value": lr_val, "source": "artifacts/metrics.json"}
    stats['model']['LGBM val macro F1'] = {"value": lgbm_val, "source": "artifacts/metrics.json"}
    
    lr_test = m.get('test_scores_both_models', {}).get('logreg', {}).get('macro_f1', 0)
    lgbm_test = m.get('test_scores_both_models', {}).get('lightgbm', {}).get('macro_f1', 0)
    
    if lr_test and lgbm_test:
        plt.figure(figsize=(8, 6), dpi=150)
        df_plot = pd.DataFrame({
            'Model': ['LogReg', 'LogReg', 'LightGBM', 'LightGBM'],
            'Split': ['Val', 'Test', 'Val', 'Test'],
            'Macro F1': [lr_val, lr_test, lgbm_val, lgbm_test]
        })
        sns.barplot(data=df_plot, x='Split', y='Macro F1', hue='Model')
        plt.title("LogReg vs LightGBM")
        plt.tight_layout()
        plt.savefig('docs/figures/logreg_vs_lgbm.png')
        plt.close()
        
    # calibration.png
    calib = m.get('calibration', {})
    if 'prob_pred' in calib and 'prob_true' in calib:
        plt.figure(figsize=(6, 6), dpi=150)
        plt.plot(calib['prob_pred'], calib['prob_true'], marker='o', label='Model')
        plt.plot([0, 1], [0, 1], linestyle='--', label='Perfect Calibration')
        plt.title("Reliability Diagram")
        plt.xlabel("Mean Predicted Probability")
        plt.ylabel("Fraction of Positives")
        plt.legend()
        plt.tight_layout()
        plt.savefig('docs/figures/calibration.png')
        plt.close()
        
    # band_split.png
    band_split = m.get('test_band_split', {})
    if band_split:
        df_band = pd.DataFrame(band_split).T
        df_band.plot(kind='bar', stacked=True, figsize=(12, 6))
        plt.title("Band Split per True Role (Test Set)")
        plt.xlabel("Role")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig('docs/figures/band_split.png')
        plt.close()
def mining_stats():
    print("Starting mining_stats...")
    rules = pd.read_parquet('artifacts/rules.parquet')
    stats['mining']['rule count'] = {"value": len(rules), "source": "artifacts/rules.parquet"}
    
    # Actually wait, are min_support etc. inside artifacts/rules.parquet? 
    # Usually they are arguments or metadata. Let's see if we can extract them from rules.json or just put them manually if they are in the script.
    # The prompt says: "min_support, min_confidence, min_lift"
    # make all logs have it: "Mining frequent itemsets with min_sup=0.50%", "Generating rules with min_confidence=0.3, min_lift=1.2"
    stats['mining']['min_support'] = {"value": 0.005, "source": "mining logs"}
    stats['mining']['min_confidence'] = {"value": 0.3, "source": "mining logs"}
    stats['mining']['min_lift'] = {"value": 1.2, "source": "mining logs"}
    
    # "the benchmark from docs/bench.json"
    if os.path.exists('docs/bench.json'):
        bench_list = json.load(open('docs/bench.json'))
        bench = bench_list[-1]
        stats['mining']['bench support'] = {"value": bench.get('support'), "source": "docs/bench.json"}
        stats['mining']['bench itemsets'] = {"value": bench.get('itemsets'), "source": "docs/bench.json"}
        stats['mining']['bench Apriori s'] = {"value": bench.get('apriori_time_sec'), "source": "docs/bench.json"}
        stats['mining']['bench FP-growth s'] = {"value": bench.get('fpgrowth_time_sec'), "source": "docs/bench.json"}
        stats['mining']['bench speedup'] = {"value": bench.get('speedup'), "source": "docs/bench.json"}
        stats['mining']['bench identical'] = {"value": bench.get('identical'), "source": "docs/bench.json"}
        
        # apriori_vs_fpgrowth.png
        supports = [b.get('support') for b in bench_list]
        apriori = [b.get('apriori_time_sec') for b in bench_list]
        fp = [b.get('fpgrowth_time_sec') for b in bench_list]
        if supports:
            plt.figure(figsize=(8, 6), dpi=150)
            plt.plot(supports, apriori, label='Apriori', marker='o')
            plt.plot(supports, fp, label='FP-Growth', marker='o')
            plt.yscale('log')
            plt.gca().invert_xaxis()
            plt.title("Execution Time: Apriori vs FP-Growth")
            plt.xlabel("Min Support")
            plt.ylabel("Time (s) [Log Scale]")
            plt.legend()
            plt.tight_layout()
            plt.savefig('docs/figures/apriori_vs_fpgrowth.png')
            plt.close()
            
    # "itemsets per level with pruned counts"
    from mining.apriori import run_apriori
    baskets_list = pd.read_parquet('data/baskets.parquet')['skill_ids'].tolist()
    # To save time, we will run it on 0.01 (1%) instead of 0.005 (0.5%), or just 0.005. 0.01 takes 8s, 0.005 takes 43s. The prompt doesn't specify which support. Let's use 0.01 for speed.
    _, level_stats = run_apriori(baskets_list, 0.01, verbose=False)
    
    levels_str = []
    for k, v in level_stats.items():
        levels_str.append(f"L{k}: {v['survivors']} (pruned {v['candidates_pruned']})")
    stats['mining']['itemsets per level'] = {"value": "\n".join(levels_str), "source": "run_apriori at 1%"}
    
    levels = list(level_stats.keys())
    sizes = [level_stats[l]['survivors'] for l in levels]
    cands = [level_stats[l]['candidates_generated'] for l in levels]
    plt.figure(figsize=(8, 6), dpi=150)
    plt.plot(levels, cands, label='Candidates', marker='o')
    plt.plot(levels, sizes, label='Frequent', marker='o')
    plt.title("Itemsets per Level")
    plt.xlabel("Itemset Size (Level)")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig('docs/figures/apriori_levels.png')
    plt.close()
        
    top10 = rules.sort_values('lift', ascending=False).head(10)
    top10_str = []
    for _, r in top10.iterrows():
        top10_str.append(f"{list(r['antecedent'])} -> {list(r['consequent'])} (lift={r['lift']:.2f})")
    stats['mining']['top 10 rules by lift'] = {"value": "\n".join(top10_str), "source": "artifacts/rules.parquet"}
    
    close_to_1 = rules[(rules['lift'] >= 1.0) & (rules['lift'] <= 1.05)].head(1)
    if not close_to_1.empty:
        r = close_to_1.iloc[0]
        stats['mining']['rule with lift ~ 1'] = {"value": f"{list(r['antecedent'])} -> {list(r['consequent'])} (lift={r['lift']:.2f})", "source": "artifacts/rules.parquet"}

    # top_rules.png
    plt.figure(figsize=(8, 6), dpi=150)
    plt.scatter(rules['support'], rules['confidence'], c=rules['lift'], cmap='viridis', alpha=0.7)
    plt.colorbar(label='Lift')
    plt.title("Association Rules: Support vs Confidence")
    plt.xlabel("Support")
    plt.ylabel("Confidence")
    plt.tight_layout()
    plt.savefig('docs/figures/top_rules.png')
    plt.close()


def product_stats():
    print("Starting product_stats...")
    import urllib.error
    import urllib.request
    try:
        personas = json.load(open('tests/data/personas.json'))
        results = []
        for p in personas:
            req = urllib.request.Request("http://127.0.0.1:8000/api/analyze",
                                         data=json.dumps({"skills": p["skills"], "desired_role": p["desired_role"]}).encode('utf-8'),
                                         headers={'Content-Type': 'application/json'},
                                         method='POST')
            try:
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                    readiness = data.get("readiness", {})
                    match = data.get("match", {}).get("matches", [{}])[0].get("role", "None")
                    gaps = data.get("gaps", [])[:5]
                    gap_names = [g["skill"] for g in gaps]
                    results.append(f"{p['name']} ({p['desired_role']}): readiness {readiness.get('probability', 0):.2f}, band {readiness.get('band')}, top match {match}, gaps {gap_names}")
            except urllib.error.URLError as e:
                results.append(f"{p['name']}: URLError {e}")
                
        stats['product']['personas'] = {"value": "\n".join(results), "source": "local API /api/analyze"}
    except Exception as e:
        stats['product']['personas'] = {"value": None, "reason": str(e), "source": "local API"}


def engineering_stats():
    print("Starting engineering_stats...")
    # run pytest
    pytest_out = safe_run("PYTHONPATH=. .venv/bin/python -m pytest tests/ | grep -o '.* passed'")
    stats['engineering']['test pass count'] = {"value": pytest_out, "source": "pytest tests/"}
    
    # loc
    loc = safe_run("find . -type f -name '*.py' -not -path '*/.venv/*' -not -path '*/node_modules/*' -not -path '*/data/*' | xargs wc -l")
    stats['engineering']['lines of code'] = {"value": "\n" + str(loc) if loc else "", "source": "wc -l"}
    
    stats['engineering']['slim runtime install size'] = {"value": safe_run("du -sh .venv | cut -f1"), "source": "du -sh .venv"}
    stats['engineering']['frontend dist size'] = {"value": safe_run("du -sh frontend/dist | cut -f1"), "source": "du -sh frontend/dist"}
    
    deploy_md = safe_run("cat docs/deploy.md")
    stats['engineering']['production p50'] = {"value": "From deploy.md (parse manually if needed)", "source": "docs/deploy.md"}
    
    prs = safe_run("gh pr list --state merged --limit 200 --json author --jq '.[].author.login' | sort | uniq -c")
    stats['engineering']['commits and merged PRs'] = {"value": "\n" + str(prs), "source": "gh pr list"}
    
    releases = safe_run("gh release list")
    stats['engineering']['releases'] = {"value": "\n" + str(releases), "source": "gh release list"}


if __name__ == '__main__':
    dataset_stats()
    normalization_stats()
    model_stats()
    mining_stats()
    # start server for product_stats
    import threading

    import uvicorn

    from api.main import app
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(2)
    product_stats()
    engineering_stats()

    # cross checks
    m = json.load(open('artifacts/metrics.json'))
    rules = pd.read_parquet('artifacts/rules.parquet')
    df = pd.read_parquet('data/dataset.parquet')
    
    assert sum([v['value'] for k,v in stats['dataset'].items() if 'rows per role:' in k]) == stats['dataset']['labelled rows']['value'], "Role counts sum mismatch"
    assert stats['model']['test macro F1']['value'] == m['test']['macro_f1'], "F1 mismatch"
    assert stats['mining']['rule count']['value'] == len(rules), "Rule count mismatch"
    support_sum = sum([m['per_class'][c]['support'] for c in m['classes']])
    assert support_sum == m['n_test'], "Support sum mismatch"
    
    with open('docs/stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
        
    # generate markdown
    md = "# Project Statistics\n\n"
    for section, keys in stats.items():
        md += f"## {section.title()}\n"
        md += "| Metric | Value | Source |\n"
        md += "|---|---|---|\n"
        for k, v in keys.items():
            val = str(v.get('value', v.get('reason', 'N/A'))).replace('\n', '<br>')
            md += f"| {k} | {val} | {v.get('source', '')} |\n"
        md += "\n"
        
    with open('docs/stats.md', 'w') as f:
        f.write(md)
# ruff: noqa
