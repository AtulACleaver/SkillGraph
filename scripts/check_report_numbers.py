#!/usr/bin/env python3
"""Check that all formatted numbers in docs/report/report.md exist in audited source files."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = ROOT / "docs" / "report" / "report.md"

SOURCE_FILES = [
    ROOT / "docs" / "numbers_audit.md",
    ROOT / "docs" / "stats.json",
    ROOT / "docs" / "bench.json",
    ROOT / "docs" / "deploy.md",
    ROOT / "artifacts" / "metrics.json",
]


def load_source_texts() -> str:
    combined = []
    for p in SOURCE_FILES:
        if p.exists():
            combined.append(p.read_text(encoding="utf-8"))
        else:
            print(f"Warning: source file missing: {p}", file=sys.stderr)
    return "\n".join(combined)


def extract_numbers(text: str) -> list[str]:
    # Match numbers with thousands comma, decimal point, or percent sign
    # e.g., 97,929; 0.7499; 65.4%; 126.49; 2,521.1; 0.50%
    pattern = r"(?<![A-Za-z0-9_])(\d{1,3}(?:,\d{3})+(?:\.\d+)?%?|\d+\.\d+%?|\d+%)(?![A-Za-z0-9_])"
    return re.findall(pattern, text)


def main():
    if not REPORT_FILE.exists():
        print(f"Report file not found: {REPORT_FILE}", file=sys.stderr)
        sys.exit(1)

    report_text = REPORT_FILE.read_text(encoding="utf-8")
    report_numbers = extract_numbers(report_text)
    source_corpus = load_source_texts()

    unmatched = []
    for num in set(report_numbers):
        # Clean comma or percent for raw match check if literal token isn't found
        raw_val = num.replace(",", "").replace("%", "")
        # Check direct occurrence in sources
        if num in source_corpus:
            continue
        if raw_val in source_corpus:
            continue
        # Also check rounded float matches from source
        try:
            val_float = float(raw_val)
            if str(val_float) in source_corpus:
                continue
            # Check if any float in source rounds to val_float
            matched_float = False
            for src_num in extract_numbers(source_corpus):
                try:
                    src_f = float(src_num.replace(",", "").replace("%", ""))
                    if round(src_f, 4) == round(val_float, 4):
                        matched_float = True
                        break
                    if round(src_f, 2) == round(val_float, 2) and "%" in num:
                        matched_float = True
                        break
                except ValueError:
                    continue
            if matched_float:
                continue
        except ValueError:
            pass
        unmatched.append(num)

    unmatched.sort()
    if unmatched:
        print(f"Found {len(unmatched)} numbers in report.md not present in source files:")
        for u in unmatched:
            print(f"  - {u}")
        sys.exit(1)
    else:
        print("All formatted numbers in report.md are verified against audited source files.")
        sys.exit(0)


if __name__ == "__main__":
    main()
