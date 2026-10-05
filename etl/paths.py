import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", str(REPO_ROOT / "artifacts")))
DATA_DIR = REPO_ROOT / "data"
TAXONOMY_DIR = REPO_ROOT / "taxonomy"
RAW_XLSX = DATA_DIR / "raw" / "indian-job-market-dataset-2025.xlsx"
STATS_DIR = DATA_DIR / "stats"
