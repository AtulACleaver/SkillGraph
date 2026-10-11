# SkillGraph Project Report: Concise Outline (Max 10 Pages)

This document defines the condensed outline, target page budget (strictly 9 to 10 pages total), figure and table allocations, and numerical citation sources for the project report (`docs/report/report.md`).

## Page Budget Overview (Target: Max 10 Pages)

Total page ceiling: 10.0 pages (including embedded figures and tables).

| Section | Content Summary | Estimated Pages |
|---|---|---|
| Front Matter | Title, Team, Placeholders, Abstract (~200 words, 4 key numbers), TOC | 1.0 |
| Chapter 1 | Introduction: Problem, Beneficiaries, Objectives (1-6), Organization | 0.5 |
| Chapter 2 | Related Work: Mining, Taxonomies, Calibration (IEEE [1]-[10]) | 0.5 |
| Chapter 3 | Dataset and Audit: Source, Drop Funnel, Class Distribution, Constraints | 1.0 |
| Chapter 4 | Preprocessing and Normalization: Tokenization, 3 Tiers, v3 to v4 Merges | 0.75 |
| Chapter 5 | Methodology: Vectorization, Augmentation, LR vs LightGBM, Readiness, Gap | 1.0 |
| Chapter 6 | Scope Decisions: Pruned Components Table, Excluded Syllabus Units | 0.5 |
| Chapter 7 | Architecture and Implementation: Pipeline & Serving PNGs, Artifacts, API | 1.0 |
| Chapter 8 | Results: Classifier Metrics, Apriori vs FP-Growth, Personas, Latency | 1.75 |
| Chapter 9 | Discussion and Limitations: 10 Numbered Specific Items with Exact Counts | 0.75 |
| Chapter 10 | Conclusion and Future Work: Summary and 5 Concrete Extensions | 0.5 |
| References & Appendices | IEEE Citations [1]-[10]; Appendices A (API), B (Team), C (AI), D (Audit) | 0.75 |
| **Total** | | **10.0** |

---

## Front Matter (Budget: 1.0 page)

### Title and Meta
- Title: "SkillGraph: Skill Demand Mining and Role Readiness for the Indian Tech Job Market"
- Subtitle: B.Tech Project Report, KIIT University, October 2026.
- Course: Data Mining and Data Warehousing [COURSE CODE].
- Academic Guide: [GUIDE NAME].
- Group: Group 8
- Team: Shashank Shekhar Pandey (Group Coordinator, 2405382), Atul Anand (2405339), Aditya Kumar (24156038), Aryan (2405005), Archit Kumar (24052551).

### Formal Preliminaries
- Combined Certificate, Declaration, and Acknowledgement with compact [PLACEHOLDER] blocks.

### Executive Summary (Abstract)
- Compact abstract (~200 words) with the 4 headline numbers:
  1. 97,929 raw postings filtered down to 34,569 clean postings and 12,872 supervised postings across 10 role families (`docs/stats.json`).
  2. Normalization coverage of 65.4% (177,432 / 271,108 skill mentions) mapping to an 800-skill canonical vocabulary (`docs/numbers_audit.md`).
  3. Logistic regression classification test macro F1 of 0.7499 and top-3 accuracy of 0.9254 against a majority baseline of 0.1774 (`artifacts/metrics.json`).
  4. FP-growth mining speedup of 126.49x over Apriori at 0.5% support (0.3454 s vs 43.6936 s) yielding 231 association rules (`docs/bench.json`, `artifacts/rules.parquet`).
- Compact Table of Contents, List of Figures, and List of Tables.

---

## Chapter 1: Introduction (Budget: 0.5 page)

- **1.1 Background & Context**: Engineering placement challenges in India; student difficulty evaluating industrial role readiness across unstructured listings.
- **1.2 Beneficiaries**: Graduating students, early-career engineers, university placement cells.
- **1.3 Objectives**: Numbered list (1: Audit corpus; 2: Build 800-token taxonomy; 3: Model readiness bands; 4: Mine co-occurrences; 5: Rank counterfactual gaps; 6: Deploy serverless app).
- **1.4 Report Structure**: Roadmap of Chapters 2 to 10.

---

## Chapter 2: Related Work (Budget: 0.5 page)

- **2.1 Association Rule Mining**: Apriori level-wise pruning [1], FP-tree compression [2], data mining principles [3].
- **2.2 Skill Taxonomies**: ESCO competency classification [9], automated job extraction [10].
- **2.3 Supervised Role Classification**: Bag-of-words/skills text classification [6], gradient boosted trees [7].
- **2.4 Probability Calibration**: Probability calibration [4], expected calibration error [5], MLxtend mining library [8].

---

## Chapter 3: Dataset and Audit (Budget: 1.0 page)

- **3.1 Raw Dataset**: 97,929 raw postings from Indian portals across 16 fields (`docs/stats.json`, `docs/data_audit.md`).
- **3.2 Filtering Funnel**:
  - Dropped 59,658 non-tech rows, 100 duplicates, 80 empty skills, 3,522 reposts (`docs/stats.json`).
  - Surviving clean postings: 34,569 (`docs/stats.json`).
  - Dropped 16,142 unmatched titles and 5,555 generic "Software Engineer" titles (`docs/stats.json`).
  - Supervised labelled postings: 12,872 (`docs/stats.json`).
- **Figure 3.1**: Attrition funnel (`docs/figures/funnel.png`).
- **Table 3.1**: Row drop summary by filter stage and reason (`docs/stats.json`).
- **Figure 3.2**: Class distribution across 10 role families (`docs/figures/class_distribution.png`).
- **3.3 Data Constraints**: The 8-tag aggregator cap; absence of calendar dates (relative strings like "6 Days Ago") preventing time-series splits (`docs/data_audit.md`).

---

## Chapter 4: Preprocessing and Normalization (Budget: 0.75 page)

- **4.1 Text Hygiene**: Trimming, lowercasing, delimiter parsing; 44,078 unique raw skill strings (`docs/stats.json`).
- **4.2 Canonical Vocabulary & 3-Tier Mapping**:
  - 800 canonical skills (`artifacts/skill_vocab.json`).
  - Tier 1: 159,725 exact matches (`docs/numbers_audit.md`).
  - Tier 2: 15,238 in-vocab alias matches via 834 rules in `taxonomy/skill_aliases.csv` (`docs/numbers_audit.md`).
  - Tier 3: 2,469 fuzzy matches with RapidFuzz ratio >= 88 (`docs/numbers_audit.md`).
  - Unmapped tokens: 93,676 (`docs/numbers_audit.md`).
- **Table 4.1**: Token normalization breakdown and mapped mass: 65.4% (177,432 / 271,108) (`docs/numbers_audit.md`).
- **4.3 Taxonomy v4 Duplicate Merges**:
  - Elimination of 28 redundant groups down to 0; `angularjs` merged into `angular`; `gen ai` merged into `generative ai` (`docs/taxonomy_v4.md`).
- **Table 4.2**: Taxonomy v3 vs v4 metrics comparison (`docs/taxonomy_v4.md`).

---

## Chapter 5: Methodology (Budget: 1.0 page)

- **5.1 Formulation**: Input $\mathbf{x} \in \{0, 1\}^{800}$, multi-class role probabilities $\mathbf{p} = [P(y=c \mid \mathbf{x})]_{c=1}^{10}$.
- **5.2 Augmentation**: Uniform subsampling (size 2 to $k-1$, $n_{\text{copies}}=2$) expanding 8,941 raw train postings to 26,039 rows (`artifacts/metrics.json`).
- **5.3 Partitioning**: Stratified split with seed 42 (70% train / 15% val / 15% test: 8,941 / 1,916 / 1,917) (`artifacts/metrics.json`).
- **5.4 Classification & 3-Point Rule**: L2 Logistic Regression vs LightGBM; LightGBM delta was +0.0149 test macro F1, failing the +0.0300 requirement; Logistic Regression selected for deployment (`docs/model.md:Section 4`).
- **5.5 Readiness Decision Rule**:
  - Probability: $\ge 0.60 \implies 2$ (Ready), $\ge 0.30 \implies 1$ (Close), $< 0.30 \implies 0$ (Not yet).
  - Coverage: $\ge 0.20 \implies 2$ (Ready), $\ge 0.10 \implies 1$ (Close), $< 0.10 \implies 0$ (Not yet).
  - Final band: $\min(p_{\text{band}}, c_{\text{band}})$ (`ml/predict.py`).
- **5.6 Association Mining**: Apriori and FP-Growth over 34,569 baskets; thresholds: min_sup 0.005, min_conf 0.30, min_lift 1.20 yielding 231 rules (`docs/mining.md`).
- **5.7 Counterfactual Gap Scoring**: $\text{Score}(s) = \Delta \text{Readiness}(s) \times \text{Coverage}(s)$; companion skills via lift $\ge 1.50$; non-learnable filter applied (`mining/gap.py`).

---

## Chapter 6: Scope Decisions (Budget: 0.5 page)

- **6.1 Pruned Architecture Components**:
  - **Table 6.1**: Cut components and rationale:
    - Clustering: Supervised classifier already resolves role fit with confusion matrices.
    - OLAP Cube / Star Schema: No analytical roll-ups or slice-and-dice needed at runtime.
    - Salary Modelling: Readiness evaluates skill competence, not compensation; salary data contained wide ranges.
    - Scraping Engine: Static audited dataset ensured reproducibility.
    - LLMs: High latency (500+ ms), cost, non-determinism, and large memory footprint.
- **6.2 Syllabus Coverage Statement**: Explicit statement identifying omitted syllabus units (multi-dimensional OLAP cubes, dimension tables, spatial clustering).

---

## Chapter 7: Architecture and Implementation (Budget: 1.0 page)

- **7.1 Pipeline and Serving Diagrams**:
  - **Figure 7.1**: Pipeline flowchart exported from Mermaid (`docs/report/figures/pipeline_arch.png`).
  - **Figure 7.2**: Serving architecture flowchart (`docs/report/figures/serving_arch.png`).
- **7.2 Implementation Details**:
  - Pure NumPy inference: Model weights in 77 KB JSON (`artifacts/model.json`); keeps Vercel function at 39.1 MB (`docs/deploy.md`).
  - React 18 client with Vite 6 and Tailwind CSS tokens (`README.md`).
- **Table 7.1**: Committed artifacts summary (`docs/stats.json`).
- **Table 7.2**: FastAPI endpoints (`/api/health`, `/api/roles`, `/api/skills`, `/api/match`, `/api/readiness`, `/api/gap`, `/api/analyze`) (`docs/api.md`).
- **7.3 Team Workflow**: Protected main, PR per task, 30 passing tests (`docs/stats.json`).

---

## Chapter 8: Results (Budget: 1.75 pages)

- **8.1 Classifier Performance**:
  - Test accuracy 0.7527, macro F1 0.7499, top-3 0.9254 vs majority baseline 0.1774 (`artifacts/metrics.json`).
  - Short-input macro F1 drops to 0.6116 (`artifacts/metrics.json`).
  - **Table 8.1**: Model comparison (LR vs LightGBM) (`docs/model.md`).
  - **Table 8.2**: Per-class precision, recall, F1 across 10 roles (`artifacts/metrics.json`).
  - **Figure 8.1**: Per-class F1 chart (`docs/figures/per_class_f1.png`).
  - **Figure 8.2**: Normalized confusion matrix (`docs/figures/confusion_matrix.png`); Full Stack vs Frontend confusion (19 and 17 errors) (`artifacts/metrics.json`).
  - **Figure 8.3**: Calibration curve (pooled ECE 0.0120, top-label ECE 0.0614) (`docs/figures/calibration.png`).
- **8.2 Mining Benchmark**:
  - **Table 8.3**: Apriori vs FP-growth benchmark across 5 thresholds (501 itemsets, 126.49x speedup at 0.5% support: 43.6936 s vs 0.3454 s, identical sets) (`docs/bench.json`).
  - **Figure 8.4**: Apriori vs FP-growth scaling curve (`docs/figures/apriori_vs_fpgrowth.png`).
  - **Table 8.4**: Top tech association rules by lift (`docs/stats.json`).
- **8.3 Persona Evaluation & Walkthroughs**:
  - **Table 8.5**: 10-persona evaluation showing probability, coverage, final band, and limiting factor (`docs/numbers_audit.md:Item 5`).
  - **Figure 8.5**: Persona 1 desktop UI screenshot (`docs/screenshots/persona1-desktop.png`).
  - Production latency: Cold start 2521.1 ms, warm p50 454.4 ms, warm p95 728.8 ms (`docs/deploy.md`).

---

## Chapter 9: Discussion and Limitations (Budget: 0.75 page)

Ten specific, numbered engineering limitations:
1. **8-Tag Truncation Cap**: Input listings capped at 8 tags, truncating secondary tools (`docs/data_audit.md`).
2. **Exclusion of Generic/Unmatched Titles**: 21,697 postings (16,142 unmatched + 5,555 generic) omitted from training (`docs/stats.json`).
3. **Non-Tech Skill Leakage**: 69 of 231 rules (29.9%) contain zero tech terms, led by HR pairings (`docs/numbers_audit.md:Item 3`).
4. **Posted Demand vs Hiring Outcomes**: Postings reflect recruiter requests rather than accepted candidate profiles.
5. **No Temporal Dimension**: Lack of calendar timestamps forced a random split instead of temporal backtesting (`docs/data_audit.md`).
6. **Short-Input Degradation**: F1 drops from 0.7499 to 0.6116 on 2 to 3 skill profiles (`artifacts/metrics.json`).
7. **Rare Skill Instability (Persona 1)**: `pandas` appeared in 36 of 8,941 rows (0.40%), shifting weight to -0.7813 and flipping top prediction to Backend (`docs/numbers_audit.md:Item 4`).
8. **Top-Bin Overconfidence**: Predicted probabilities > 0.90 average 0.976 predicted vs 0.911 true (`docs/model.md:Section 6`).
9. **Regional Focus**: Data reflects Indian metro tech hiring, not global remote patterns.
10. **Discarded Architectures**: LightGBM was discarded because +0.0149 macro F1 fell short of the 0.0300 threshold (`docs/model.md:Section 4`).

---

## Chapter 10: Conclusion and Future Work (Budget: 0.5 page)

- **10.1 Summary**: Production-ready mining and readiness system with audited pipeline, 800-skill taxonomy, and calibrated inference.
- **10.2 Future Extensions**:
  1. Time-stamped ingestion for temporal validation.
  2. Negative filtering to purge HR and CAD terms.
  3. Minimum frequency floors (e.g. count >= 100) to stabilize rare skills like `pandas`.
  4. Unsupervised clustering as a supplementary exploratory view.
  5. User study with graduating students to measure placement impact.

---

## References & Appendices (Budget: 0.75 page)

### References
- IEEE References [1] through [10] exactly as specified.

### Appendices
- **Appendix A: API Reference**: Compact endpoint route table from `docs/api.md`.
- **Appendix B: Team Contributions**: Module ownership (Shashank as Group Coordinator, Atul, Aditya, Aryan, Archit). Commit and PR counts omitted.
- **Appendix C: AI Use Statement**: Summary from `AI-USE.md`.
- **Appendix D: Reproducibility**: `make all` verification table from `docs/reproducibility.md`.
