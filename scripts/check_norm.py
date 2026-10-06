import time
from collections import Counter
from pathlib import Path

import pandas as pd

from etl.normalize import (
    _aliases,
    _clean_map,
    _clean_token,
    load_vocab,
    normalize_skill,
)


def main() -> None:
    t0 = time.time()
    data_path = Path(__file__).resolve().parents[1] / "data" / "clean.parquet"

    if not data_path.exists():
        raise FileNotFoundError(
            f"{data_path} is missing. Run the ETL pipeline or download the data artifact."
        )

    raw = pd.read_parquet(data_path)
    all_tokens = []

    for skills in raw["tagsAndSkills"].dropna():
        all_tokens.extend(
            token.strip().lower()
            for token in skills.split(",")
            if token.strip()
        )

    token_counts = Counter(all_tokens)
    print(
        f"Total tokens: {len(all_tokens)}, "
        f"Unique tokens: {len(token_counts)}, "
        f"Time so far: {time.time() - t0:.2f}s"
    )

    load_vocab()
    mapped_mass = 0
    fuzzy_count = 0

    for index, (token, count) in enumerate(token_counts.items()):
        cleaned = _clean_token(token)
        if not cleaned:
            continue

        if cleaned in _clean_map or cleaned in _aliases:
            mapped_mass += count
        elif normalize_skill(token) is not None:
            fuzzy_count += count
            mapped_mass += count

        if index % 5000 == 0:
            print(f"Processed {index} items...")

    print(
        f"Mapped mass: {mapped_mass}, "
        f"fuzzy: {fuzzy_count}, "
        f"Total time: {time.time() - t0:.2f}s"
    )


if __name__ == "__main__":
    main()
