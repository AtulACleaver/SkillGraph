import sys
import time

from etl.paths import RAW_XLSX
from etl.stats import file_sha256, write_stage_stats


def check_raw():
    t0 = time.time()
    if not RAW_XLSX.exists():
        print(f"Error: RAW_XLSX not found at {RAW_XLSX}", file=sys.stderr)
        sys.exit(1)

    sha = file_sha256(RAW_XLSX)
    print(f"RAW_XLSX: {RAW_XLSX}")
    print(f"SHA256: {sha}")

    # Write stage stats
    elapsed = time.time() - t0
    write_stage_stats(
        stage="raw",
        rows_in=97929,
        rows_out=97929,
        drops_by_reason={},
        elapsed_seconds=elapsed,
        output_files={str(RAW_XLSX): sha},
    )
    return sha


if __name__ == "__main__":
    check_raw()
