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
├── frontend/      # Shashank — Vite + React UI
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