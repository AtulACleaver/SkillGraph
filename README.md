# SkillGraph — India Job Market Mining Engine

A student types the skills they have and the job they want. They get back: the role that actually fits them, whether they are ready for the one they asked for, and the skills that would move them fastest.

## Quick Start

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the ETL pipeline (requires data/raw/ with the source xlsx)
python -m etl.clean
python -m etl.normalize

# Start the API
uvicorn api.main:app --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

## Project Structure

```
skillgraph/
├── etl/           # Atul — cleaning, normalization, labelling
├── ml/            # Aditya — features, training, prediction
├── mining/        # Aryan — Apriori, FP-growth, gap ranking
├── taxonomy/      # Aryan — hand-edited skill aliases & role families
├── api/           # Archit — FastAPI serving layer
├── frontend/      # Sashang — Vite + React UI
├── fixtures/      # Archit — fake artifacts for dev
├── tests/         # each person owns their module's tests
├── docs/          # data audit, contracts, model writeup
├── data/          # GITIGNORED — rebuilt by the pipeline
└── artifacts/     # GITIGNORED — built artifacts shipped via GitHub Releases
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Status, artifacts loaded, row counts |
| GET | `/roles` | Role families with posting counts |
| GET | `/skills?q=` | Autocomplete over canonical names |
| POST | `/match` | Top 3 roles with probabilities |
| POST | `/readiness` | Probability, band, coverage for desired role |
| POST | `/gap` | 5 ranked skills with reasons |
| POST | `/analyze` | All three in one response |

## Mining Module

The `mining` module implements skill association rule mining to power our gap recommendations.

### Apriori Pruning Efficiency
Our scratch implementation of the generalized Apriori algorithm (`mining.apriori`) efficiently prunes the candidate space. By strictly enforcing the Apriori property (an itemset can only be frequent if all of its subsets are frequent), we avoid unnecessary counting. For example, at lower support thresholds, over 85% of candidate 3-itemsets and 4-itemsets are discarded before the database scan, avoiding exponential explosion.

### Benchmark: Apriori vs. FP-growth
For production rules, we use `mlxtend`'s FP-growth (`mining.rules`) which avoids candidate generation entirely by compressing transactions into an FP-tree. This offers dramatic speedups over Apriori, especially as `min_sup` drops. 

| Min Support | Frequent Itemsets | Apriori (s) | FP-growth (s) | Speedup (FP/Ap) |
|-------------|-------------------|-------------|---------------|-----------------|
| 5.0%        | 19                | 0.202       | 0.122         | 1.65x           |
| 3.0%        | 43                | 0.587       | 0.100         | 5.86x           |
| 2.0%        | 95                | 1.790       | 0.112         | 15.96x          |
| 1.0%        | 284               | 11.111      | 0.153         | 72.52x          |
| 0.5%        | 835               | 126.495     | 0.201         | 628.10x         |

*(Benchmark on full dataset of ~18,000 baskets)*

### Gap Recommendation Formula
The `POST /gap` endpoint ranks the highest-impact missing skills for a desired role using the following scoring formula:

```python
score = readiness_gain * base_coverage
```

- **`readiness_gain`**: Evaluated via the ML module's `delta_readiness(user_vector, target_role, skill)` which simulates the counterfactual bump in candidate probability if they acquire this skill.
- **`base_coverage`**: The estimated relative frequency/importance of the skill within the target role's historical postings.

Once top skills are scored, we query our **association rules (lift > 1.5)** to attach "companions"—related skills often acquired together (e.g. suggesting `pandas` as a companion to `numpy`).