"""Hardware-attached replenishment workflow; use the root demo for offline review."""

import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    from workflow.run_sample_workflow import main as run_workflow

    return run_workflow()


if __name__ == "__main__":
    raise SystemExit(main())
