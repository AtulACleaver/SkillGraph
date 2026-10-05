import subprocess
import sys
import time

STAGES = [
    ("raw", [sys.executable, "-m", "etl.raw"]),
    ("profile", [sys.executable, "-m", "etl.profile"]),
    ("clean", [sys.executable, "-m", "etl.clean"]),
    ("label", [sys.executable, "-m", "etl.label"]),
    ("train", [sys.executable, "-m", "ml.train"]),
    ("rules", [sys.executable, "-m", "mining.rules"]),
    ("export", [sys.executable, "-m", "ml.export_runtime"]),
]


def run_all():
    times = {}
    total_start = time.time()
    for name, cmd in STAGES:
        print(f"\n{'='*20} Running stage: {name} {'='*20}")
        t0 = time.time()
        res = subprocess.run(cmd, check=False)
        if res.returncode != 0:
            print(f"Error: Stage {name} failed with exit code {res.returncode}", file=sys.stderr)
            sys.exit(res.returncode)
        elapsed = time.time() - t0
        times[name] = elapsed
        print(f"=== Stage {name} finished in {elapsed:.2f}s ===")

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 45)
    print("PIPELINE WALL TIME SUMMARY")
    print("=" * 45)
    for name, elapsed in times.items():
        print(f"  {name:15s}: {elapsed:6.2f}s")
    print(f"  {'TOTAL':15s}: {total_elapsed:6.2f}s")
    print("=" * 45)


if __name__ == "__main__":
    run_all()
