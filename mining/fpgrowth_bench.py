import time
from typing import Any

import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.preprocessing import TransactionEncoder

from mining.apriori import run_apriori


def benchmark_mining(
    baskets_file: str = "data/baskets.parquet",
    min_sup_list: list[float] | None = None,
    sample_size: int | None = None,
) -> pd.DataFrame:
    """
    Benchmark scratch Apriori vs mlxtend FP-Growth across multiple min_sup levels.
    """
    if min_sup_list is None:
        min_sup_list = [0.05, 0.03, 0.02, 0.01, 0.005]

    print(f"Loading baskets from {baskets_file}...")
    df = pd.read_parquet(baskets_file)
    baskets = [list(skill_ids) for skill_ids in df["skill_ids"] if len(skill_ids) > 0]

    if sample_size and sample_size < len(baskets):
        baskets = baskets[:sample_size]
        print(f"Sampled {len(baskets):,} baskets for benchmark.")
    else:
        print(f"Using full {len(baskets):,} baskets.")

    print("Encoding transactions for FP-Growth (one-hot binary)...")
    te = TransactionEncoder()
    te_ary = te.fit(baskets).transform(baskets)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

    results: list[dict[str, Any]] = []

    print("\nStarting Benchmark...")
    print(f"{'Min Sup':>10} | {'Itemsets':>10} | {'Apriori (s)':>12} | {'FP-growth (s)':>14} | {'Speedup (FP/Ap)':>15}")
    print("-" * 75)

    for min_sup in min_sup_list:
        # 1. Apriori
        t0 = time.perf_counter()
        apriori_frequent, _ = run_apriori(baskets, min_sup, verbose=False)
        t_apriori = time.perf_counter() - t0

        # 2. FP-growth
        t0 = time.perf_counter()
        fpgrowth_res = fpgrowth(df_encoded, min_support=min_sup, use_colnames=True)
        t_fpgrowth = time.perf_counter() - t0

        num_apriori = len(apriori_frequent)
        num_fp = len(fpgrowth_res)

        speedup = t_apriori / t_fpgrowth if t_fpgrowth > 0 else 0.0

        print(
            f"{min_sup*100:>9.2f}% | {num_apriori:>10,} | {t_apriori:>12.3f} | {t_fpgrowth:>14.3f} | {speedup:>14.2f}x"
        )

        results.append(
            {
                "min_sup_pct": f"{min_sup*100:.2f}%",
                "min_sup": min_sup,
                "apriori_itemsets": num_apriori,
                "fpgrowth_itemsets": num_fp,
                "apriori_time_sec": round(t_apriori, 4),
                "fpgrowth_time_sec": round(t_fpgrowth, 4),
                "speedup": round(speedup, 2),
            }
        )

    res_df = pd.DataFrame(results)
    return res_df


if __name__ == "__main__":
    benchmark_mining()
