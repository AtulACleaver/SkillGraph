import math
from collections import defaultdict
from itertools import combinations
from typing import Any


def get_L1(baskets: list[list[Any]], min_sup_count: int) -> dict[frozenset, int]:
    """Generate frequent 1-itemsets (L1)."""
    counts = defaultdict(int)
    for basket in baskets:
        for item in basket:
            counts[item] += 1

    # L1 contains 1-itemsets (frozensets) that meet min support
    L1 = {frozenset([item]): count for item, count in counts.items() if count >= min_sup_count}
    return L1


def get_C2(L1_keys: set[frozenset]) -> list[frozenset]:
    """Generate candidate 2-itemsets (C2) from L1."""
    items = [next(iter(k)) for k in L1_keys]
    items.sort()
    C2 = [frozenset(c) for c in combinations(items, 2)]
    return C2


def get_L2(baskets: list[list[Any]], C2: list[frozenset], min_sup_count: int) -> dict[frozenset, int]:
    """Generate frequent 2-itemsets (L2) from C2."""
    counts = defaultdict(int)
    for basket in baskets:
        basket_set = frozenset(basket)
        for candidate in C2:
            if candidate.issubset(basket_set):
                counts[candidate] += 1

    L2 = {c: count for c, count in counts.items() if count >= min_sup_count}
    return L2


def run_apriori_l2(baskets: list[list[Any]], min_sup_pct: float) -> tuple[dict[frozenset, int], dict[frozenset, int]]:
    """
    Runs Apriori up to L2 (Day 3 paper-test baseline).
    baskets: list of lists (or sets) of items.
    min_sup_pct: float, e.g. 0.005 for 0.5%
    """
    total_baskets = len(baskets)
    min_sup_count = math.ceil(total_baskets * min_sup_pct)

    L1 = get_L1(baskets, min_sup_count)
    C2 = get_C2(set(L1.keys()))
    L2 = get_L2(baskets, C2, min_sup_count)

    return L1, L2


def generate_candidates_k(
    prev_frequent_itemsets: set[frozenset], k: int
) -> tuple[list[frozenset], int, int]:
    """
    Generate candidate k-itemsets (Ck) from L_{k-1} with prefix-join and subset pruning.
    Returns (surviving_candidates, total_generated_before_prune, candidates_pruned).
    """
    # Represent each (k-1) itemset as a sorted tuple
    sorted_itemsets = sorted([sorted(itemset) for itemset in prev_frequent_itemsets])
    n = len(sorted_itemsets)
    candidates_set = set()
    total_generated = 0
    pruned_count = 0

    # Join step: join two (k-1)-itemsets if they share the first (k-2) items
    for i in range(n):
        for j in range(i + 1, n):
            itemset1 = sorted_itemsets[i]
            itemset2 = sorted_itemsets[j]

            # Check if first k-2 items match
            if k == 2 or itemset1[: k - 2] == itemset2[: k - 2]:
                total_generated += 1
                candidate = frozenset(itemset1 + [itemset2[k - 2]])

                # Prune step (Apriori property): every (k-1)-subset must be in prev_frequent_itemsets
                is_valid = True
                for subset in combinations(candidate, k - 1):
                    if frozenset(subset) not in prev_frequent_itemsets:
                        is_valid = False
                        break

                if is_valid:
                    candidates_set.add(candidate)
                else:
                    pruned_count += 1
            else:
                # Since sorted_itemsets is lexicographically sorted, if prefix doesn't match, we can break inner loop
                if k > 2 and itemset1[: k - 2] != itemset2[: k - 2]:
                    break

    return list(candidates_set), total_generated, pruned_count


def run_apriori(
    baskets: list[list[Any]], min_sup_pct: float, verbose: bool = True
) -> tuple[dict[frozenset, int], dict[int, dict[str, Any]]]:
    """
    Full generalized Apriori algorithm from k=1 until Lk is empty.
    
    Returns:
      all_frequent: dict mapping frozenset itemset to support count.
      level_stats: dict mapping level k to stats dict (candidates_gen, pruned, survivors, prune_pct).
    """
    total_baskets = len(baskets)
    min_sup_count = math.ceil(total_baskets * min_sup_pct)

    if verbose:
        print(f"Total baskets: {total_baskets:,} | Min support count: {min_sup_count:,} ({min_sup_pct*100:.2f}%)")

    # Fast basket lookup using set representation
    basket_sets = [frozenset(b) for b in baskets]

    all_frequent: dict[frozenset, int] = {}
    level_stats: dict[int, dict[str, Any]] = {}

    # k = 1
    L1 = get_L1(baskets, min_sup_count)
    all_frequent.update(L1)
    level_stats[1] = {
        "candidates_generated": len(L1),
        "candidates_pruned": 0,
        "survivors": len(L1),
        "pruning_pct": 0.0,
    }
    if verbose:
        print(f"Level 1: {len(L1):,} frequent 1-itemsets")

    current_L = set(L1.keys())
    k = 2

    while current_L:
        candidates, gen_count, pruned_count = generate_candidates_k(current_L, k)
        if not candidates:
            break

        # Count support for candidates
        counts = defaultdict(int)
        for bset in basket_sets:
            for cand in candidates:
                if cand.issubset(bset):
                    counts[cand] += 1

        Lk = {cand: count for cand, count in counts.items() if count >= min_sup_count}
        all_frequent.update(Lk)

        prune_pct = (pruned_count / gen_count * 100.0) if gen_count > 0 else 0.0
        level_stats[k] = {
            "candidates_generated": gen_count,
            "candidates_pruned": pruned_count,
            "survivors": len(Lk),
            "pruning_pct": prune_pct,
        }

        if verbose:
            print(
                f"Level {k}: Generated {gen_count:,} candidates, "
                f"Pruned {pruned_count:,} ({prune_pct:.1f}%), "
                f"Frequent itemsets {len(Lk):,}"
            )

        current_L = set(Lk.keys())
        k += 1

    return all_frequent, level_stats
