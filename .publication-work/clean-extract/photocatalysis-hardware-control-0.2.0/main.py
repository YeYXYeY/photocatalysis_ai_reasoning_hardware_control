"""Safe root commands for software-only demonstration, tests, and packaging."""

import argparse


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "test", "check", "package"))
    args, remainder = parser.parse_known_args(argv)
    if args.command == "demo":
        from tools.run_demo import main as execute

        return execute(remainder)
    if args.command == "package":
        from tools.build_release import main as execute

        return execute(remainder)
    if remainder:
        parser.error("Unexpected arguments: " + " ".join(remainder))
    if args.command == "test":
        from tools.run_tests import main as execute
    else:
        from tools.validate_release import main as execute
    return execute()


if __name__ == "__main__":
    raise SystemExit(main())
