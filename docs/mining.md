# Association Mining and Gap Recommendation Engine

This document details market basket construction, the Apriori and FP-growth algorithms, mining thresholds, benchmark comparisons, gap scoring logic, and non-tech leakage analysis.

## 1. Market Baskets Construction

Market baskets were built from cleaned tech postings (`data/clean.parquet`):

- Total baskets in `data/baskets.parquet`: 34,569 baskets.
- Non-empty baskets: 32,949 baskets contain at least one canonical skill ID from `artifacts/skill_vocab.json`.
- Empty baskets: 1,620 baskets contain zero recognized canonical skill IDs after normalization.
- Basket format: Record mapping `posting_id` to a deduplicated integer list of canonical `skill_ids`.

## 2. Frequent Itemset Mining: Apriori vs FP-Growth

Both algorithms were implemented to mine frequent itemsets over identical baskets:

- Apriori (`mining/apriori.py`): Built from scratch using standard level-wise candidate generation (self-join) and subset pruning.
- FP-Growth (`mining/rules.py` and `mining/fpgrowth_bench.py`): Built using `mlxtend.frequent_patterns.fpgrowth` over one-hot sparse basket matrices.

### Benchmark Results

Itemset generation was timed across five minimum support thresholds on 34,569 baskets (`docs/bench.json`):

| Min Support (%) | Support Value | Itemsets Found | Apriori Time (s) | FP-Growth Time (s) | Speedup | Identical Sets | Max Support Diff |
|---|---|---|---|---|---|---|---|
| 5.00% | 0.050 | 13 | 0.1459 | 0.0915 | 1.60x | Yes | 0.0 |
| 3.00% | 0.030 | 34 | 0.5189 | 0.0969 | 5.35x | Yes | 0.0 |
| 2.00% | 0.020 | 62 | 1.5869 | 0.1017 | 15.61x | Yes | 0.0 |
| 1.00% | 0.010 | 168 | 8.0566 | 0.2550 | 31.60x | Yes | 0.0 |
| 0.50% | 0.005 | 501 | 43.6936 | 0.3454 | 126.49x | Yes | 0.0 |

At the production threshold of 0.50% support, FP-growth ran in 0.3454 seconds compared to 43.6936 seconds for Apriori (126.49x speedup). Both algorithms generated identical 501 itemsets. Hardware environment was not recorded in `docs/bench.json`.

## 3. Mining Thresholds and Rule Generation

Rules were derived from frequent itemsets using `mlxtend.frequent_patterns.association_rules`:

- Minimum Support: 0.005 (0.50%, roughly 173 postings). Lower thresholds caused memory blowup on dense tech combinations, while higher thresholds eliminated specialized tools.
- Minimum Confidence: 0.30 (30%). Required that the consequent appear in at least 30% of baskets containing the antecedent.
- Minimum Lift: 1.20. Discarded independent or negatively correlated skill pairs.
- Total Rules Generated: 231 association rules stored in `artifacts/rules.parquet` and `artifacts/rules.json`.

## 4. Gap Scoring and Recommendations

Skill gaps for a target role are ranked using counterfactual probability gains combined with posting frequencies (`mining/gap.py`):

### Candidate Selection
Candidate skills are pulled from the target role top 20 skills (`artifacts/role_profiles.json`) and filtered:
1. Exclude skills already present in the user input.
2. Exclude non-learnable tokens from `taxonomy/non_learnable.txt` (such as soft skills and general management terms).
3. Exclude redundant terms via `_is_redundant_skill` (such as "software development life cycle" if "software" is present).

### Ranking Formula
For each candidate skill `s`:

$$\text{Score}(s) = \Delta \text{Readiness}(s) \times \text{Coverage}(s)$$

Where:
- $\Delta \text{Readiness}(s) = \max(0, P(\text{role} \mid \mathbf{x} \cup \{s\}) - P(\text{role} \mid \mathbf{x}))$ evaluates counterfactual readiness gain via `ml.predict.delta_readiness`.
- $\text{Coverage}(s)$ is the empirical frequency of skill `s` among training postings for the target role (`role_profiles.json`).

### Companion Skills (`learn_with`)
For each recommended skill, `_find_companions` identifies up to 2 other gap skills that co-occur in association rules with `lift >= 1.50`.

## 5. Non-Tech Leakage Analysis

Job posting filters in `etl/clean.py` matched keywords from `etl/tech_terms.txt` across job titles and skill tags. Postings such as "Technical Recruiter" or "Mechanical Engineering Drafter" passed the filter because their titles contained "technical" or "engineer".

- Non-Tech Rules Count: 69 of the 231 rules (29.9%) in `artifacts/rules.parquet` contain zero terms from `etl/tech_terms.txt`.
- Top Rules by Lift: Top 10 rules by lift are HR generalist pairings (screening, hr generalist activities, joining formalities) with lift values exceeding 90.0.
- Top 20 Non-Tech Tokens in `data/baskets.parquet`:
  1. css: 3,175
  2. qa: 2,331
  3. c#: 2,194
  4. development: 2,133
  5. project management: 2,078
  6. sap: 1,893
  7. agile: 1,603
  8. rest: 1,603
  9. automation: 1,595
  10. continuous integration: 1,533
  11. troubleshooting: 1,423
  12. oracle: 1,376
  13. spring boot: 1,338
  14. application: 1,304
  15. microservices: 1,296
  16. html: 1,266
  17. ml: 1,167
  18. web services: 1,056
  19. networking: 1,018
  20. analytical: 989

These tokens were retained without retraining to preserve real-world job posting distribution patterns.
