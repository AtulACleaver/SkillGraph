import os
import time
from itertools import combinations
from typing import Any

import pandas as pd

from etl.stats import write_stage_stats


def generate_rules(
    frequent_itemsets: dict[frozenset, int],
    total_baskets: int,
    min_confidence: float = 0.2,
    min_lift: float = 1.0,
) -> pd.DataFrame:
    """
    Generate association rules X -> Y from frequent itemsets.
    
    Args:
        frequent_itemsets: dict mapping frozenset of items to support count
        total_baskets: total number of transactions N
        min_confidence: minimum confidence threshold (0 to 1.0)
        min_lift: minimum lift threshold (>1.0 indicates positive correlation)
        
    Returns:
        pd.DataFrame with columns: [antecedent, consequent, support, confidence, lift, rule_count]
    """
    rules: list[dict[str, Any]] = []

    for itemset, itemset_count in frequent_itemsets.items():
        k = len(itemset)
        if k < 2:
            continue

        itemset_support = itemset_count / total_baskets
        items_list = list(itemset)

        # Generate all non-empty proper subsets as antecedents
        for r in range(1, k):
            for ant_tuple in combinations(items_list, r):
                ant = frozenset(ant_tuple)
                consq = itemset - ant

                if ant not in frequent_itemsets or consq not in frequent_itemsets:
                    continue

                ant_count = frequent_itemsets[ant]
                consq_count = frequent_itemsets[consq]
                consq_support = consq_count / total_baskets

                confidence = itemset_count / ant_count
                if confidence < min_confidence:
                    continue

                lift = confidence / consq_support if consq_support > 0 else 0.0
                if lift < min_lift:
                    continue

                rules.append(
                    {
                        "antecedent": sorted(ant),
                        "consequent": sorted(consq),
                        "support": round(itemset_support, 6),
                        "confidence": round(confidence, 6),
                        "lift": round(lift, 4),
                        "rule_count": itemset_count,
                    }
                )

    df_rules = pd.DataFrame(rules)
    if not df_rules.empty:
        # Sort by lift descending, then confidence descending
        df_rules = df_rules.sort_values(["lift", "confidence"], ascending=[False, False]).reset_index(drop=True)
    else:
        df_rules = pd.DataFrame(
            columns=["antecedent", "consequent", "support", "confidence", "lift", "rule_count"]
        )

    return df_rules


def save_rules(rules_df: pd.DataFrame, output_path: str = "artifacts/rules.parquet") -> None:
    """Save generated association rules to parquet."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rules_df.to_parquet(output_path, index=False)
    print(f"Saved {len(rules_df):,} association rules to {output_path}")


def run_rule_mining(
    baskets_file: str = "data/baskets.parquet",
    output_rules_file: str = "artifacts/rules.parquet",
    min_sup_pct: float = 0.005,
    min_confidence: float = 0.3,
    min_lift: float = 1.2,
    max_rules: int = 50000,
) -> pd.DataFrame:
    """
    Full pipeline to mine frequent itemsets and generate association rules.
    Uses FP-growth for speed and aggressively prunes to keep artifacts lean.
    """
    t_start = time.time()
    from mlxtend.frequent_patterns import fpgrowth
    from mlxtend.preprocessing import TransactionEncoder

    print(f"Loading baskets from {baskets_file}...")
    df = pd.read_parquet(baskets_file)
    baskets = [list(skill_ids) for skill_ids in df["skill_ids"] if len(skill_ids) > 0]
    total_baskets = len(baskets)
    empty_baskets = len(df) - total_baskets

    print("Encoding transactions for FP-Growth...")
    te = TransactionEncoder()
    te_ary = te.fit(baskets).transform(baskets)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    print(f"Mining frequent itemsets with min_sup={min_sup_pct*100:.2f}% using FP-growth...")
    t0 = time.time()
    fpgrowth_res = fpgrowth(df_encoded, min_support=min_sup_pct, use_colnames=True)
    t1 = time.time()
    print(f"Found {len(fpgrowth_res):,} frequent itemsets in {t1-t0:.2f}s.")

    # Convert to dict format expected by our generate_rules: {frozenset: count}
    frequent_itemsets = {
        frozenset(row["itemsets"]): round(row["support"] * total_baskets)
        for _, row in fpgrowth_res.iterrows()
    }

    print(f"Generating rules with min_confidence={min_confidence}, min_lift={min_lift}...")
    rules_df = generate_rules(frequent_itemsets, total_baskets, min_confidence, min_lift)
    initial_rules_count = len(rules_df)
    pruned_count = 0

    # Hard pruning step to prevent bloated artifacts
    if len(rules_df) > max_rules:
        print(f"Pruning {len(rules_df):,} rules down to top {max_rules:,} by lift & confidence...")
        rules_df = rules_df.head(max_rules)
        pruned_count = initial_rules_count - len(rules_df)

    save_rules(rules_df, output_rules_file)

    elapsed = time.time() - t_start
    write_stage_stats(
        stage="rules",
        rows_in=len(df),
        rows_out=len(rules_df),
        drops_by_reason={"empty_baskets": empty_baskets, "pruned_rules": pruned_count},
        elapsed_seconds=elapsed,
        output_files=[output_rules_file],
    )
    return rules_df


if __name__ == "__main__":
    if os.path.exists("data/baskets.parquet"):
        run_rule_mining()
    else:
        print("data/baskets.parquet not found. Run ETL pipeline first.")
