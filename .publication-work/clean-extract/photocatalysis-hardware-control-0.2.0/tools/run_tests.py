"""Run each station suite in its own process to isolate local package names."""

from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SUITES = (
    "automatic-control-system",
    "liquid-handling-workstation",
    "mobile_robot",
    "photocatalytic_reactor",
    "solid_handling_station",
    ".",
)


def main():
    start = time.perf_counter()
    failed = []
    for name in SUITES:
        print(f"Running software-only tests: {name}", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"],
            cwd=ROOT / name,
        )
        if result.returncode:
            failed.append(name)
    print(f"Elapsed: {time.perf_counter() - start:.2f} seconds")
    if failed:
        print(f"Failed suites: {failed}")
        return 1
    print("All software-only test suites passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
