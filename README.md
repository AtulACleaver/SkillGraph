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

## Data Pipeline (Atul)
- **Source**: Kaggle Indian Job Market Dataset 2025 (`indian-job-market-dataset-2025.xlsx`)
- **Raw Size**: 97,929 rows
- **Filtered Tech Subset**: 33,724 rows (34.4%)
- **Data Cleaning**: Handled noisy nulls, stripped reposts/exact duplicates (~9,514 dropped), and removed postings with empty skill lists.
- **Normalization**: Cleaned distinct raw skills into canonical skill IDs based on string matching and manual aliases. Mapped 10,038 canonical skills covering >75% of token mass.
- **Role Labeling**: Applied rule-based title mapping to compress 17,404 distinct titles into 10 key Role Families.
- **Final Training Dataset**: 12,863 labeled rows across 10 families, and 30,134 baskets for mining.

## The Model (Aditya)
- **Framing**: Multiclass Role Classification. Postings are treated as 'skill profiles'. The model predicts `P(Role | Skills)`, converting standard classification into a 'Readiness' gauge.
- **Augmentation**: To prevent the model from being overconfident on short user inputs (students typing 3-6 skills vs employers posting 8 skills), the training set was augmented by artificially shortening postings (random 40%, 60%, 80% fractions).
- **Algorithm**: Multinomial Logistic Regression (`class_weight='balanced'`). Chosen over LightGBM due to better probability calibration.
- **Accuracy**: Reached ~67.1% Macro F1 / Accuracy across 10 families, with a Top-3 Accuracy of 90.6%.
- **Readiness Gap**: Evaluated using counterfactual prediction. The skill that raises `P(desired_role)` the most is recommended.