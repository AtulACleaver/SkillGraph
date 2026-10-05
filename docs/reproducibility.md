# Reproducibility Audit

The pipeline was verified by running `make reset` followed by `make all`. All rebuilt artifacts were compared against the committed artifacts in `artifacts/`.

## Artifact Comparison

| Metric / Artifact | Committed Value | Rebuilt Value | Match |
|---|---|---|---|
| Vocab size (`skill_vocab.json`) | 800 | 800 | yes |
| Vocab SHA256 (`skill_vocab.json`) | d749eb5d5044fea1e366972fba1bf94351c822dd580ac66a0e711a6f8f92dece | d749eb5d5044fea1e366972fba1bf94351c822dd580ac66a0e711a6f8f92dece | yes |
| Test macro F1 (`metrics.json`) | 0.7424 | 0.7424 | yes |
| Test accuracy (`metrics.json`) | 0.7463 | 0.7463 | yes |
| Test top-3 accuracy (`metrics.json`) | 0.9254 | 0.9254 | yes |
| Rule count (`rules.json` and `rules.parquet`) | 336 | 336 | yes |

## Test Set Class Counts

Test class supports were compared between committed `artifacts/metrics.json` and the rebuilt run.

| Role Family | Committed Test Support | Rebuilt Test Support | Match |
|---|---|---|---|
| Backend | 191 | 191 | yes |
| Data / BI Analyst | 204 | 204 | yes |
| Data Science / ML | 180 | 180 | yes |
| DevOps / Cloud | 340 | 340 | yes |
| ERP / Enterprise | 223 | 223 | yes |
| Frontend | 117 | 117 | yes |
| Full Stack | 194 | 194 | yes |
| Mobile | 65 | 65 | yes |
| QA / Test | 243 | 243 | yes |
| Support / IT Ops | 159 | 159 | yes |
| **Total Test Postings** | **1,916** | **1,916** | **yes** |

Every rebuilt metric and artifact matched the committed baseline exactly.
