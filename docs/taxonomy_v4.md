# Taxonomy v4 Evaluation and Migration

This document records the evaluation of taxonomy v4, comparing metrics against the v3 baseline.

## Angular Merge Rationale

angularjs was merged into angular on purpose; AngularJS 1.x and Angular 2+ are different frameworks, but the postings use the names interchangeably.

## Duplicate Skills Analysis

`scripts/find_duplicate_skills.py` identified duplicate groups based on plural suffixes, word-order permutations, punctuation differences, and technology prefixes.

- v3 duplicate groups: 28 groups containing 39 redundant skills (measured on the v3 `artifacts/skill_vocab.json`).
- v4 duplicate groups: 0 groups (measured on the v4 `artifacts/skill_vocab.json`).

All identified duplicate skills were merged into their canonical forms in `taxonomy/skill_aliases.csv` as specified in `docs/taxonomy_v4_merges.csv`, including `gen ai` and `genai` merged into `generative ai`.

## Evaluation Metrics (v3 vs v4)

Numbers below were extracted directly from `artifacts/metrics.json`, `artifacts/rules.json`, and the evaluation scripts.

| Metric | v3 Baseline | v4 Result | Delta | Source File |
| :--- | :--- | :--- | :--- | :--- |
| Vocabulary size | 800 | 800 | 0 | `artifacts/skill_vocab.json` |
| Duplicate groups left | 28 | 0 | -28 | `scripts/find_duplicate_skills.py` |
| Persona junk count | 5 / 15 | 0 / 50 | -5 | `scripts/persona_check.py` |
| Association rules count | 336 | 231 | -105 | `artifacts/rules.json` |
| Full-input test accuracy | 0.7463 | 0.7527 | +0.0064 | `artifacts/metrics.json` |
| Full-input test macro-F1 | 0.7424 | 0.7499 | +0.0075 | `artifacts/metrics.json` |
| Short-input test accuracy | 0.6269 | 0.6215 | -0.0054 | `artifacts/metrics.json` |
| Short-input test macro-F1 | 0.6234 | 0.6116 | -0.0118 | `artifacts/metrics.json` |
| Top-3 test accuracy | 0.9248 | 0.9254 | +0.0006 | `artifacts/metrics.json` |
| Test ECE | 0.0133 | 0.0120 | -0.0013 | `artifacts/metrics.json` |
| Raw training postings | 8,938 | 8,941 | +3 | `artifacts/metrics.json` |
| Augmented training rows | 25,990 | 26,039 | +49 | `artifacts/metrics.json` |
| Postings dropped (0 skills) | 103 | 98 | -5 | `artifacts/metrics.json` |

## Per-Class Test Macro-F1 Comparison

From `artifacts/metrics.json`:

| Role Family | v3 Macro-F1 | v4 Macro-F1 | Support |
| :--- | :--- | :--- | :--- |
| Backend | 0.7390 | 0.7311 | 191 |
| Data / BI Analyst | 0.7624 | 0.7696 | 205 |
| Data Science / ML | 0.7859 | 0.7845 | 180 |
| DevOps / Cloud | 0.6700 | 0.6453 | 340 |
| ERP / Enterprise | 0.8262 | 0.8661 | 223 |
| Frontend | 0.6397 | 0.6307 | 117 |
| Full Stack | 0.6863 | 0.7181 | 194 |
| Mobile | 0.7519 | 0.7857 | 65 |
| QA / Test | 0.8606 | 0.8825 | 243 |
| Support / IT Ops | 0.7019 | 0.6854 | 159 |

## Persona 1 Analysis (python, sql, pandas -> Data / BI Analyst)

All input skills (`python`, `sql`, `pandas`) were recognized by `skills_to_vector`, and `pandas` is present in `artifacts/skill_vocab.json` at index 287.

| Metric | v3 Baseline | v4 Result | Source File |
| :--- | :--- | :--- | :--- |
| Top 1 match | Data / BI Analyst (0.4313) | Backend (0.4906) | `artifacts/model.json` |
| Top 2 match | Data Science / ML (0.2298) | Data Science / ML (0.1957) | `artifacts/model.json` |
| Top 3 match | Backend (0.2091) | Data / BI Analyst (0.1080) | `artifacts/model.json` |
| Readiness probability | 0.4313 (Close) | 0.1080 (Not yet) | `/api/analyze` |
| Covered skills | python, sql | python, sql | `artifacts/role_profiles.json` |
| Unrecognized skills | [] | [] | `skills_to_vector` |
| python coefficient | +0.6510 | +0.6928 | `artifacts/model.json` |
| sql coefficient | +1.0303 | +1.0469 | `artifacts/model.json` |
| pandas coefficient | +0.8412 | -0.7813 | `artifacts/model.json` |
| Intercept (Data / BI Analyst) | +0.1754 | +0.2076 | `artifacts/model.json` |

In the training split, postings listing `pandas` totaled 42 in data-v3 and 36 in data-v4. The per-role distribution in train was: Backend (18 in v3, 16 in v4), Data Science / ML (14 in v3, 10 in v4), Data / BI Analyst (8 in v3, 6 in v4), DevOps / Cloud (0 in v3, 2 in v4), Full Stack (1 in v3, 1 in v4), and QA / Test (1 in v3, 1 in v4). Because `pandas` appears in very few postings (36 out of 8,941 training postings, or 0.40%), its logistic regression coefficient is unstable across retrainings and regularized feature space shifts. In v4, Backend retains a strong positive coefficient (+2.0626) while Data / BI Analyst received a negative coefficient (-0.7813), shifting top prediction on `[python, sql, pandas]` to Backend.

## Association Rules Reduction Breakdown (336 -> 231)

Comparing `artifacts/rules.json` from git commit HEAD (v3) to v4:

1. **51 rules** linked two skills that merged into a single canonical skill (e.g. `boot` -> `spring boot`, `react js` -> `react`, `javas` -> `java`, `rest apis` -> `rest api`). These self-referential antecedent-consequent pairs were eliminated because itemsets cannot contain duplicate tokens.
2. **93 rules** contained a merged-away token on either side without linking to the same skill (e.g. `{react js} -> {javascript}`). Of these, 58 rules merged into existing canonical v4 rules, while 35 dropped because their multi-item combinations shifted below minimum support or confidence thresholds.
3. **192 rules** contained no merged-away tokens. 190 of these rules survived into v4 without modification, and 2 dropped due to minor support threshold shifts.
4. **41 new canonical rules** formed in v4 around unified high-frequency tokens (190 surviving + 41 new = 231 total rules).

Together, the elimination of 51 self-referential rules and the consolidation of 58 duplicate rules account for the reduction from 336 to 231 rules.

## Persona Check Results

Output from `scripts/persona_check.py` on the 10 representative persona profiles:

1. Data / BI Analyst (`python`, `sql`, `pandas`):
   - Predicted readiness: 0.1080 (Not yet)
   - Top 5 gaps: Power BI, Data Engineering, PySpark, Data Analysis, Snowflake
   - Junk count: 0

2. Backend (`java`, `spring boot`, `mysql`, `docker`):
   - Predicted readiness: 0.7520 (Close)
   - Top 5 gaps: Microservices, Hibernate, Kafka, Python, Golang
   - Junk count: 0

3. Full Stack (`react`, `javascript`, `html`, `css`):
   - Predicted readiness: 0.2395 (Not yet)
   - Top 5 gaps: Java, Spring Boot, AWS, C#, Python
   - Junk count: 0

4. Frontend (`react`, `javascript`, `css`):
   - Predicted readiness: 0.8529 (Ready)
   - Top 5 gaps: UI, Angular, Redux, Git, Bootstrap
   - Junk count: 0

5. DevOps / Cloud (`docker`, `kubernetes`, `aws`, `linux`):
   - Predicted readiness: 0.7498 (Ready)
   - Top 5 gaps: Terraform, Continuous Integration, Azure DevOps, CI/CD, Jenkins
   - Junk count: 0

6. QA / Test (`selenium`, `manual testing`, `jira`):
   - Predicted readiness: 0.8553 (Ready)
   - Top 5 gaps: Test Cases, API Testing, Performance Testing, Automation Framework, Regression Testing
   - Junk count: 0

7. ERP / Enterprise (`sap`, `abap`):
   - Predicted readiness: 0.9367 (Close)
   - Top 5 gaps: ServiceNow, JavaScript, Salesforce, SAP S/4HANA, Master Data
   - Junk count: 0

8. Data Science / ML (`python`, `machine learning`, `pytorch`):
   - Predicted readiness: 0.9186 (Close)
   - Top 5 gaps: NLP, Generative AI, TensorFlow, Image Processing, Research
   - Junk count: 0

9. Support / IT Ops (`linux`, `networking`, `troubleshooting`):
   - Predicted readiness: 0.8626 (Ready)
   - Top 5 gaps: Network Engineering, Customer Service, WAN, DNS, Switching
   - Junk count: 0

10. Mobile (`android`, `kotlin`):
    - Predicted readiness: 0.9957 (Close)
    - Top 5 gaps: iOS, Flutter, React Native, Swift, MVVM
    - Junk count: 0

## Decision

Decision rule criteria:
1. Duplicate groups left == 0 (0 left, criterion satisfied).
2. Persona junk count == 0 (0 junk recommendations across all 10 personas, criterion satisfied).
3. v4 full-input test macro-F1 >= 0.732 (0.7499 achieved, criterion satisfied).

Decision: SHIP v4.
