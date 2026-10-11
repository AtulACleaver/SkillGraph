# AI Assistance Disclosure

This project used Google Antigravity with Gemini models to assist development.

## Tools Used

- Environment: Google Antigravity IDE.
- Models: Gemini 3.1 Pro (Planning mode) and Gemini 3.1 Flash.

## Tasks Assisted by AI

1. Repository scaffolding: Directory structures, Makefile automation targets, and GitHub Actions CI pipelines.
2. Data normalization: Fuzzy matching logic using RapidFuzz, alias resolution maps, and duplicate detection scripts.
3. Mining algorithms: Apriori level-wise candidate generation and integration of FP-growth benchmarks with `mlxtend`.
4. Serving layer: Export of trained logistic regression coefficients to lightweight JSON artifacts and stable softmax inference in NumPy.
5. User interface: React frontend setup with Vite, Tailwind CSS tokens, and Framer Motion micro-interactions.
6. Documentation and test generation: API test cases, smoke verification scripts, and numbers auditing scripts.

## Manual Human Verification

1. Data integrity: Cross-checked row counts and drop reasons across raw datasets, clean Parquet tables, and baskets.
2. Production testing: Validated live responses from `https://skillgraph-exp.vercel.app` using `curl` and browser inspection.
3. Metric validation: Verified classification metrics and calibration errors directly against `artifacts/metrics.json`.
4. Code review: Inspected all pull requests, contract schemas, and git authorship history.
