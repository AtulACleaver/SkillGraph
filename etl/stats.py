import hashlib
import json
from pathlib import Path
from typing import Any

from etl.paths import REPO_ROOT, STATS_DIR


def file_sha256(path: str | Path) -> str:
    path = Path(path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def write_stage_stats(
    stage: str,
    rows_in: int,
    rows_out: int,
    drops_by_reason: dict[str, int],
    elapsed_seconds: float,
    output_files: list[str | Path] | dict[str, str],
) -> Path:
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    stats_file = STATS_DIR / f"{stage}.json"

    sha256_map: dict[str, str] = {}
    if isinstance(output_files, dict):
        sha256_map = dict(output_files)
    else:
        for out in output_files:
            p = Path(out)
            rel_str = str(p.relative_to(REPO_ROOT)) if p.is_absolute() and p.is_relative_to(REPO_ROOT) else str(p)
            if p.exists() or (REPO_ROOT / p).exists():
                sha256_map[rel_str] = file_sha256(p)

    payload: dict[str, Any] = {
        "stage": stage,
        "rows_in": int(rows_in),
        "rows_out": int(rows_out),
        "drops_by_reason": {str(k): int(v) for k, v in drops_by_reason.items()},
        "elapsed_seconds": round(float(elapsed_seconds), 4),
        "output_files": sha256_map,
        "sha256": sha256_map,
    }

    with open(stats_file, "w") as f:
        json.dump(payload, f, indent=2)

    return stats_file
