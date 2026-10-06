# Project Statistics

## Dataset
| Metric | Value | Source |
|---|---|---|
| raw rows | 97929 | data/stats/clean.json |
| rows surviving clean | 34569 | data/stats/clean.json |
| dropped (clean): Not in tech subset | 59658 | data/stats/clean.json |
| dropped (clean): Exact duplicates | 100 | data/stats/clean.json |
| dropped (clean): No skills after splitting | 80 | data/stats/clean.json |
| dropped (clean): Reposts | 3522 | data/stats/clean.json |
| labelled rows | 12872 | data/stats/label.json |
| dropped (label): unmatched | 16142 | data/stats/label.json |
| dropped (label): Software Engineer (generic) | 5555 | data/stats/label.json |
| rows per role: DevOps / Cloud | 2279 | data/dataset.parquet |
| rows per role: QA / Test | 1649 | data/dataset.parquet |
| rows per role: ERP / Enterprise | 1495 | data/dataset.parquet |
| rows per role: Data / BI Analyst | 1365 | data/dataset.parquet |
| rows per role: Full Stack | 1290 | data/dataset.parquet |
| rows per role: Backend | 1276 | data/dataset.parquet |
| rows per role: Data Science / ML | 1212 | data/dataset.parquet |
| rows per role: Support / IT Ops | 1088 | data/dataset.parquet |
| rows per role: Frontend | 784 | data/dataset.parquet |
| rows per role: Mobile | 434 | data/dataset.parquet |
| rows with no skill ids | 0 | data/stats/train.json |
| unique raw skill strings | 44078 | data/raw.parquet |
| baskets | 34569 | data/baskets.parquet |
| posting dates | no usable dates (relative strings like '6 Days Ago') | data/raw.parquet |

## Normalization
| Metric | Value | Source |
|---|---|---|
| vocab size | 800 | artifacts/skill_vocab.json |
| alias count | 834 | taxonomy/skill_aliases.csv |
| mapped mass | 189573 / 271108 (69.9%) (Note: 69.9% over all clean rows vs 77.2% over tech subset) | computed from data/clean.parquet |
| exact match count | 159725 | computed |
| alias match count | 179612 | computed |
| fuzzy match count | 2457 | computed |
| top 20 unmapped strings | {'design engineering': 213, 'simulation': 169, 'site engineering': 136, '3d modeling': 134, 'software development methodologies': 131, 'analyzing information': 120, 'software sales': 117, 'catia': 109, 'cobol': 105, 'business strategy': 103, 'hmi': 101, 'mechanical design': 101, 'electrical design': 100, 'rtos': 100, 'maintenance engineering': 98, 'sales engineering': 98, 'plm': 98, 'preventive maintenance': 96, 'equipment': 96, 'data entry operation': 94} | computed |

## Model
| Metric | Value | Source |
|---|---|---|
| n_train raw | 8941 | artifacts/metrics.json |
| n_train augmented | 26039 | artifacts/metrics.json |
| n_val | 1916 | artifacts/metrics.json |
| n_test | 1917 | artifacts/metrics.json |
| majority baseline | 0.1774 | artifacts/metrics.json |
| test macro F1 | 0.7499 | artifacts/metrics.json |
| test accuracy | 0.7527 | artifacts/metrics.json |
| test top-3 | 0.9254 | artifacts/metrics.json |
| short-input test macro F1 | 0.6116 | artifacts/metrics.json |
| per-class Backend F1 | 0.7311 | artifacts/metrics.json |
| per-class Data / BI Analyst F1 | 0.7696 | artifacts/metrics.json |
| per-class Data Science / ML F1 | 0.7845 | artifacts/metrics.json |
| per-class DevOps / Cloud F1 | 0.6453 | artifacts/metrics.json |
| per-class ERP / Enterprise F1 | 0.8661 | artifacts/metrics.json |
| per-class Frontend F1 | 0.6307 | artifacts/metrics.json |
| per-class Full Stack F1 | 0.7181 | artifacts/metrics.json |
| per-class Mobile F1 | 0.7857 | artifacts/metrics.json |
| per-class QA / Test F1 | 0.8825 | artifacts/metrics.json |
| per-class Support / IT Ops F1 | 0.6854 | artifacts/metrics.json |
| ECE pooled | 0.012 | artifacts/metrics.json |
| ECE top-label | 0.0614 | artifacts/metrics.json |
| LR val macro F1 | 0.7435 | artifacts/metrics.json |
| LGBM val macro F1 | 0.7532 | artifacts/metrics.json |
| LR test macro F1 | 0.7499 | artifacts/metrics.json |
| LGBM test macro F1 | 0.7648 | artifacts/metrics.json |

## Mining
| Metric | Value | Source |
|---|---|---|
| rule count | 231 | artifacts/rules.parquet |
| min_support | 0.005 | mining logs |
| min_confidence | 0.3 | mining logs |
| min_lift | 1.2 | mining logs |
| bench support | 0.005 | docs/bench.json |
| bench itemsets | 501 | docs/bench.json |
| bench Apriori s | 43.6936 | docs/bench.json |
| bench FP-growth s | 0.3454 | docs/bench.json |
| bench speedup | 126.49 | docs/bench.json |
| bench identical | yes | docs/bench.json |
| itemsets per level | L1: 104 (pruned 0)<br>L2: 47 (pruned 0)<br>L3: 4 (pruned 164) | run_apriori at 1% |
| top 10 rules by lift | screening, hr generalist activities -> joining formalities (lift=125.665, conf=1.000, sup=0.007)<br>joining formalities -> screening, hr generalist activities (lift=125.665, conf=0.932, sup=0.007)<br>screening, joining formalities -> hr generalist activities (lift=112.415, conf=1.000, sup=0.007)<br>hr generalist activities -> screening, joining formalities (lift=112.415, conf=0.833, sup=0.007)<br>joining formalities -> hr generalist activities (lift=109.850, conf=0.977, sup=0.008)<br>hr generalist activities -> joining formalities (lift=109.850, conf=0.874, sup=0.008)<br>hr generalist activities, joining formalities -> screening (lift=92.125, conf=0.953, sup=0.007)<br>screening -> hr generalist activities, joining formalities (lift=92.125, conf=0.716, sup=0.007)<br>joining formalities -> screening (lift=90.023, conf=0.932, sup=0.007)<br>screening -> joining formalities (lift=90.023, conf=0.716, sup=0.007) | artifacts/rules.parquet |
| top 10 rules by lift among tech skills | software, software development life cycle -> root cause analysis (lift=62.442, conf=0.720, sup=0.005)<br>root cause analysis -> software, software development life cycle (lift=62.442, conf=0.438, sup=0.005)<br>sap abap -> sap hana (lift=54.926, conf=0.538, sup=0.006)<br>sap hana -> sap abap (lift=54.926, conf=0.562, sup=0.006)<br>software, root cause analysis -> software development life cycle (lift=54.409, conf=0.960, sup=0.005)<br>design principles -> application design (lift=40.402, conf=0.539, sup=0.006)<br>application design -> design principles (lift=40.402, conf=0.438, sup=0.006)<br>root cause analysis -> software development life cycle (lift=28.568, conf=0.504, sup=0.006)<br>software development life cycle -> root cause analysis (lift=28.568, conf=0.329, sup=0.006)<br>python, application -> css, c# (lift=27.876, conf=0.671, sup=0.006) | artifacts/rules.parquet |

## Product
| Metric | Value | Source |
|---|---|---|
| personas | Data / BI Analyst (Data / BI Analyst): readiness 0.11, band Not yet, top match Backend, gaps ['Power BI', 'Data Engineering', 'PySpark', 'Data Analysis', 'Snowflake']<br>Backend (Backend): readiness 0.75, band Close, top match Backend, gaps ['Microservices', 'Hibernate', 'Kafka', 'Python', 'Golang']<br>Full Stack (Full Stack): readiness 0.24, band Not yet, top match Frontend, gaps ['Java', 'Spring Boot', 'AWS', 'C#', 'Python']<br>Frontend (Frontend): readiness 0.85, band Ready, top match Frontend, gaps ['UI', 'Angular', 'Redux', 'Git', 'Bootstrap']<br>DevOps / Cloud (DevOps / Cloud): readiness 0.75, band Ready, top match DevOps / Cloud, gaps ['Terraform', 'Continuous Integration', 'Azure DevOps', 'CI/CD', 'Jenkins']<br>QA / Test (QA / Test): readiness 0.86, band Ready, top match QA / Test, gaps ['Test Cases', 'API Testing', 'Performance Testing', 'Automation Framework', 'Regression Testing']<br>ERP / Enterprise (ERP / Enterprise): readiness 0.94, band Close, top match ERP / Enterprise, gaps ['ServiceNow', 'JavaScript', 'Salesforce', 'SAP S/4HANA', 'Master Data']<br>Data Science / ML (Data Science / ML): readiness 0.92, band Close, top match Data Science / ML, gaps ['NLP', 'Generative AI', 'TensorFlow', 'Image Processing', 'Research']<br>Support / IT Ops (Support / IT Ops): readiness 0.86, band Ready, top match Support / IT Ops, gaps ['Network Engineering', 'Customer Service', 'WAN', 'DNS', 'Switching']<br>Mobile (Mobile): readiness 1.00, band Close, top match Mobile, gaps ['iOS', 'Flutter', 'React Native', 'Swift', 'MVVM'] | in-process analyze_skills |

## Engineering
| Metric | Value | Source |
|---|---|---|
| test pass count | 30 | pytest tests/ |
| lines of code | <br>.github: 41<br>api: 353<br>etl: 718<br>frontend: 5446<br>mining: 795<br>ml: 649<br>root: 167<br>scripts: 1007<br>taxonomy: 987<br>tests: 703 | git ls-files per dir |
| slim runtime install size | 66M | fresh venv from requirements.txt |
| frontend dist size | 276K | du -sh frontend/dist |
| Vercel function size | 39.1 MB | docs/deploy.md |
| production latency (cold start ms) | 2521.1 | docs/deploy.md |
| production latency (p50 ms) | 454.4 | docs/deploy.md |
| production latency (p95 ms) | 728.8 | docs/deploy.md |
| commits and merged PRs | <br>7 Archit1302-wolf<br>  17 AtulACleaver<br>   2 eccentricAryan404<br>   1 ssp0009 | gh pr list |
| releases | <br>rules-v2	Latest	rules-v2	2026-10-05T19:34:48Z<br>model-v4		model-v4	2026-10-05T19:34:26Z<br>data-v4		data-v4	2026-10-05T19:34:17Z<br>rules-v1		rules-v1	2026-10-04T07:06:17Z<br>model-v3		model-v3	2026-10-04T04:16:41Z<br>data-v3		data-v3	2026-10-03T18:20:30Z<br>data-v2		data-v2	2026-10-03T17:13:22Z<br>model-v2		model-v2	2026-10-03T17:13:21Z<br>Data Handoff v1		data-v1	2026-10-02T07:47:18Z | gh release list |

