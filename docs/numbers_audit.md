# Numbers Audit

This document records the audit of numbers in `docs/stats.json`, `README.md`, `docs/contracts.md`, test suites, and deployment scripts.

## Audit Summary Table

| Item | Claim | Value Today | What It Actually Counts | Fix |
|---|---|---|---|---|
| 1. Mapped mass | Normalization coverage | 69.9% in `README.md`; "69.9% over all clean rows vs 77.2% over tech subset" in `docs/stats.json`; 76.5% reported in v3 | 1. **69.9% (189,573 / 271,108)** was computed in `scripts/collect_stats.py` on all 34,569 rows in `data/clean.parquet`. The numerator 189,573 included 27,391 alias mentions from `taxonomy/skill_aliases.csv`, of which 12,153 map to canonical skills outside the 800-skill vocab. Denominator 271,108 is all skill tokens in `data/clean.parquet`.<br>2. **77.2% (77,917 / 100,912)** was computed by `build_vocab` in `etl/label.py` on the 12,872 labelled postings only (`tech_df`). Numerator 77,917 is mentions of the 800 vocab skills in labelled rows; denominator 100,912 is total tokens in labelled rows. Labelled rows were misnamed "tech subset", but `data/clean.parquet` is already the tech subset.<br>3. **76.5%** was the v3 baseline on labelled postings before duplicate token merges.<br>4. **True headline number: 65.4% (177,432 / 271,108)**. Defined in one sentence: share of skill mentions in the clean postings that map to the 800-skill vocab. Numerator is 177,432 (159,725 exact + 15,238 in-vocab alias + 2,469 fuzzy). Denominator is 271,108 clean tokens. | Keep one headline number: **65.4%** (177,432 / 271,108). Define it in one sentence in docs and make `scripts/collect_stats.py` emit only this number. |
| 2. Match counts | Token match method breakdown | exact 159,725 + alias 179,612 + fuzzy 2,457 = 341,794 in `docs/stats.json` | 1. In `scripts/collect_stats.py`, an initial loop accumulated 152,221 alias matches because `_clean_map` was imported as an empty dict before `load_vocab()` ran.<br>2. A second loop then ran without resetting counters. `exact_count` added 159,725. `alias_count` added another 27,391 (including aliases whose canonical target is outside the 800-skill vocab), yielding 179,612 (152,221 + 27,391).<br>3. `fuzzy_count` was 2,457 (or 2,469 with exact RapidFuzz matching).<br>4. The sum 341,794 exceeded both mapped tokens (177,432) and total tokens (271,108) due to double counting across loops and non-vocab aliases. | Remove the redundant loop in `scripts/collect_stats.py`. Partition all 271,108 tokens into mutually exclusive categories: exact match in vocab (159,725), alias match with canonical in vocab (15,238), fuzzy match score >= 88 (2,469), and unmapped (93,676). Sum of mapped matches equals 177,432. |
| 3. Non-tech leakage | Tech purity of mined rules and vocabulary | Top 10 rules by lift are HR skills; top unmapped strings include mechanical / CAD skills | 1. **69 of 231 rules (29.9%)** in `artifacts/rules.parquet` contain no skill matching terms in `etl/tech_terms.txt`. 162 rules contain at least one tech skill.<br>2. Leakage mechanism: `etl/clean.py` retained postings if any keyword in `etl/tech_terms.txt` appeared in either title or tags. Postings with titles like "HR Recruiter for Software Engineers" or "Mechanical Design Engineer" passed into `data/clean.parquet`. Mined baskets preserved co-occurring HR skills.<br>3. **Top 20 non-tech tokens in `data/baskets.parquet`** (skills in vocab not matching `etl/tech_terms.txt`): css (3,175), qa (2,331), c# (2,194), development (2,133), project management (2,078), sap (1,893), agile (1,603), rest (1,603), automation (1,595), continuous integration (1,533), troubleshooting (1,423), oracle (1,376), spring boot (1,338), application (1,304), microservices (1,296), html (1,266), ml (1,167), web services (1,056), networking (1,018), analytical (989). | Report rule count (69 non-tech rules out of 231) and basket token counts in `docs/mining.md` and `docs/numbers_audit.md`. Do not alter filter terms or retrain. |
| 4. Persona 1 flipped in v4 | Predictor behavior on python, sql, pandas | v3: 0.4313 Close (Data / BI Analyst); v4: 0.1080 Not yet (Backend 0.4906) | 1. Confirmed via curl against `https://skillgraph-exp.vercel.app/api/analyze`: matches Backend 0.4906, Data Science / ML 0.1957, Data / BI Analyst 0.1080; readiness 0.1080, band Not yet.<br>2. `pandas` appears in only 36 of 8,941 training postings (0.40%). In `artifacts/model.json`, its coefficient for Data / BI Analyst shifted from +0.8412 in v3 to -0.7813 in v4, while Backend kept +2.0626. | Do not retrain. Document as a known limitation in one line: "Persona 1 (python, sql, pandas) predicts Backend (0.4906) over Data / BI Analyst (0.1080) because pandas appears in only 36 of 8,941 training postings and received a negative coefficient (-0.7813)." |
| 5. Bands | Readiness band evaluation logic | Mobile 1.00 is Close, ERP 0.94 is Close, DevOps 0.75 is Ready | 1. Confirmed from `ml/predict.py`: `final_band = min(p_band, c_band)`.<br>2. Probability band cutoffs: >= 0.60 Ready, >= 0.30 Close, < 0.30 Not yet.<br>3. Coverage band cutoffs: >= 0.20 Ready, >= 0.10 Close, < 0.10 Not yet.<br>4. Mobile (prob 0.9957 Ready, cov 0.1500 Close) held back by coverage to Close.<br>5. ERP (prob 0.9367 Ready, cov 0.1500 Close) held back by coverage to Close.<br>6. DevOps (prob 0.7498 Ready, cov 0.2000 Ready) meets both thresholds and receives Ready. | Add a "Limiting Factor" column to the persona evaluation table in `docs/stats.md` explaining which band governed the outcome. |
| 6. Contributions | Git commit and PR attribution | AtulACleaver (17), Archit1302-wolf (7), eccentricAryan404 (2), ssp0009 (1) in `docs/stats.json`; Aditya missing | 1. Inspected git log authors, committers, and Co-authored-by trailers across the entire repository history.<br>2. No commit or trailer references an author named Aditya or a related handle.<br>3. Handles found: Atul Anand (`AtulACleaver`), Archit Kumar (`Archit1302-wolf`), Shashank Shekhar Pandey (`ssp0009`), and Aryan (`eccentricAryan404`).<br>4. Confirmed by user: Aditya's GitHub username is `real-aditya-kumar`. | Record Aditya as `real-aditya-kumar` across team documentation and contributor summaries. |
| 7. Screenshots | Web application preview images | Old screenshots in `docs/screenshots/` showed v3 numbers (Persona 1 at 43%) | 1. Recaptured all 6 persona screenshots from production (`https://skillgraph-exp.vercel.app`) at 1280 px and 390 px viewports.<br>2. Verified on-screen figures match `/api/analyze`:<br>- Persona 1 (`sql, excel, power bi, tableau` -> `Data / BI Analyst`): readiness 97%, band Close, coverage 10%.<br>- Persona 2 (`java, spring boot, mysql, docker` -> `Backend`): readiness 75%, band Close, coverage 15%.<br>- Persona 3 (`react, javascript, html, css` -> `Full Stack`): match Frontend 74%, readiness 24%, band Not yet, coverage 20%.<br>3. Overwrote existing files in `docs/screenshots/`. Per user instruction, README will feature desktop screenshots only. | Screenshots recaptured and validated against production API responses. |
| 8. Persona numbers in contracts, tests, smoke | Consistency of test assertions | Discrepancies between v3 and v4 figures across repo scripts | 1. `docs/contracts.md`: Contains v4 numbers (0.9733 Close, 0.7520 Close, 0.7369 Frontend / 0.2395 Not yet, 0.4906 Backend / 0.1080 Not yet).<br>2. `tests/test_runtime.py`: Contains v4 numbers (0.9733, 0.7520, 0.7369, 0.2395, 0.4906, 0.1080).<br>3. `scripts/smoke.sh`: Already updated on main with v4 numbers and verified passing against `https://skillgraph-exp.vercel.app`. | Verified all 4 personas in `scripts/smoke.sh` and `tests/test_runtime.py` match v4 contract numbers. |

## Detailed Findings

### Item 1: Mapped Mass Numerator and Denominator
- **Definition**: Share of skill mentions in the clean postings that map to the 800-skill vocab.
- **Clean Postings Total Mentions**: 271,108 tokens across 34,569 rows in `data/clean.parquet`.
- **Exact Vocabulary Matches**: 159,725 tokens.
- **In-Vocab Alias Matches**: 15,238 tokens (tokens whose canonical target in `taxonomy/skill_aliases.csv` exists in `artifacts/skill_vocab.json`).
- **Fuzzy Matches**: 2,469 tokens (tokens matching a vocabulary string with RapidFuzz ratio >= 88).
- **Total Mapped Mentions**: 177,432 tokens.
- **Headline Calculation**: 177,432 / 271,108 = **65.45%** (rounds to **65.4%**).
- **Prior 77.2% Figure**: 77,917 mapped mentions / 100,912 mentions in the 12,872 labelled rows (`tech_df`), misnamed in `docs/stats.json` as the tech subset.
- **Prior 69.9% Figure**: 189,573 mentions / 271,108 tokens. Included 12,153 mentions mapping to aliases outside the 800-skill vocabulary.

### Item 2: Match Counters Reconciliation
In `scripts/collect_stats.py`:
- `exact_count` = 159,725
- `alias_count` = 15,238 (filtered to canonicals in `artifacts/skill_vocab.json`)
- `fuzzy_count` = 2,469
- **Sum of Mapped Tokens** = 159,725 + 15,238 + 2,469 = 177,432
- **Unmapped Tokens** = 93,676
- **Total Clean Tokens** = 177,432 + 93,676 = 271,108
The prior sum of 341,794 was caused by an uninitialized second loop and inclusion of non-vocab aliases.

### Item 3: Non-Tech Leakage Counts
Evaluated against `etl/tech_terms.txt` (32 keywords):
- **Total rules in `artifacts/rules.parquet`**: 231
- **Rules containing at least one tech skill**: 162 (70.1%)
- **Rules containing zero tech skills**: 69 (29.9%)
- **Top 20 non-tech vocabulary tokens in `data/baskets.parquet`**:
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

### Item 4: Persona 1 Verification
CURL against production (`POST https://skillgraph-exp.vercel.app/api/analyze` with `{"skills":["python","sql","pandas"],"desired_role":"Data / BI Analyst"}`):
- Match probabilities: Backend 0.4906, Data Science / ML 0.1957, Data / BI Analyst 0.1080.
- Readiness probability: 0.1080, band: Not yet, coverage: 0.10 (covered: Python, SQL).
- Cause: `pandas` appears in 36 of 8,941 training rows. Its coefficient for Data / BI Analyst shifted from +0.8412 (v3) to -0.7813 (v4), while Backend received +2.0626.

### Item 5: Persona Readiness Bands Breakdown
Evaluated on all 10 standard personas:

| Persona | Role | Probability | Probability Band | Coverage | Coverage Band | Final Band | Limiting Factor |
|---|---|---|---|---|---|---|---|
| Data / BI Analyst | Data / BI Analyst | 0.1080 | Not yet | 0.1000 | Close | Not yet | Probability |
| Backend | Backend | 0.7520 | Ready | 0.1500 | Close | Close | Coverage |
| Full Stack | Full Stack | 0.2395 | Not yet | 0.2000 | Ready | Not yet | Probability |
| Frontend | Frontend | 0.8529 | Ready | 0.2500 | Ready | Ready | Both equal |
| DevOps / Cloud | DevOps / Cloud | 0.7498 | Ready | 0.2000 | Ready | Ready | Both equal |
| QA / Test | QA / Test | 0.8553 | Ready | 0.2000 | Ready | Ready | Both equal |
| ERP / Enterprise | ERP / Enterprise | 0.9367 | Ready | 0.1500 | Close | Close | Coverage |
| Data Science / ML | Data Science / ML | 0.9186 | Ready | 0.1500 | Close | Close | Coverage |
| Support / IT Ops | Support / IT Ops | 0.8626 | Ready | 0.2000 | Ready | Ready | Both equal |
| Mobile | Mobile | 0.9957 | Ready | 0.1500 | Close | Close | Coverage |

### Item 6: Contributor Attribution
- `git log` author analysis identified:
  - Atul Anand (`AtulACleaver`)
  - Archit Kumar (`Archit1302-wolf`)
  - Aryan (`eccentricAryan404`)
  - Shashank Shekhar Pandey (`ssp0009`)
- Aditya was not found in git authors or Co-authored-by trailers.
- Confirmed by user: `real-aditya-kumar`.

### Item 7: Screenshot Recapture Status
All screenshots recaptured from `https://skillgraph-exp.vercel.app` at 1280 px and 390 px viewports and written to `docs/screenshots/`:
- `persona1-desktop.png`: 1280 x 2917 px
- `persona1-mobile.png`: 390 x 4331 px
- `persona2-desktop.png`: 1280 x 2917 px
- `persona2-mobile.png`: 390 x 4146 px
- `persona3-desktop.png`: 1280 x 2978 px
- `persona3-mobile.png`: 390 x 4482 px
- `prod-mobile.png`: 390 x 4331 px
Numbers on screen match live `/api/analyze` responses. Per user instruction, README will show desktop screenshots only.

### Item 8: Stale Script Inventory
- `docs/contracts.md`: Carries v4 numbers.
- `tests/test_runtime.py`: Carries v4 numbers.
- `scripts/smoke.sh`: Verified with v4 numbers and passes all checks against `https://skillgraph-exp.vercel.app`.

### Item 9: Report Baselines, Deltas, and Audit Numbers
- **Data audit nulls and percentages** (`docs/data_audit.md`): tagsAndSkills null count 571 (0.58%), experience null count 2,105 (2.15%), ReviewsCount and AggregateRating null count 35,252 (36.00%). Non-empty baskets: 32,949.
- **Role exclusions**: Unmatched titles 16,142 plus generic Software Engineer titles 5,555 sum to 21,697 excluded postings.
- **Taxonomy v3 baselines and deltas** (`docs/taxonomy_v4.md`):
  - v3 vocabulary size: 800, v4: 800 (delta: 0).
  - v3 duplicate groups: 28, v4: 0 (delta: -28).
  - v3 rules count: 336, v4: 231 (delta: -105).
  - v3 full-input test accuracy: 0.7463, v4: 0.7527 (delta: +0.0064).
  - v3 full-input test macro F1: 0.7424, v4: 0.7499 (delta: +0.0075).
  - v3 short-input test accuracy: 0.6269, v4: 0.6215 (delta: -0.0054).
  - v3 short-input test macro F1: 0.6234, v4: 0.6116 (delta: -0.0118).
  - v3 top-3 test accuracy: 0.9248, v4: 0.9254 (delta: +0.0006).
  - v3 test ECE: 0.0133, v4: 0.0120 (delta: -0.0013).
  - v3 raw training postings: 8,938, v4: 8,941 (delta: +3).
  - v3 augmented training rows: 25,990, v4: 26,039 (delta: +49).
  - v3 postings dropped with 0 skills: 103, v4: 98 (delta: -5).
- **Model evaluation deltas**:
  - LightGBM test macro F1 (0.7648) minus Logistic Regression test macro F1 (0.7499) equals 0.0149 (or 1.49 percentage points).
  - Majority baseline improvement: test accuracy 0.7527 minus majority baseline 0.1774 equals 0.5753 (or 57.53 percentage points).
  - Short-input degradation: test macro F1 0.7499 minus short-input macro F1 0.6116 equals 0.1383 (or 13.83 percentage points).
- **Normalization token shares**: exact matches 159,725 (58.92% of 271,108 clean tokens), in-vocab alias matches 15,238 (5.62%), fuzzy matches 2,469 (0.91%), total mapped mentions 177,432 (65.45% or 65.4%), unmapped tokens 93,676 (34.55%). Among mapped mass: exact matches form 90.02%, alias matches form 8.59%, fuzzy matches form 1.39% (total 100.00%).

### Item 10: Group 8 Team Roster and Registration Numbers
- Group: Group 8
- Shashank Shekhar Pandey (Group Coordinator): Roll No. 2405382
- Atul Anand: Roll No. 2405339
- Aditya Kumar: Roll No. 24156038
- Aryan: Roll No. 2405005
- Archit Kumar: Roll No. 24052551


