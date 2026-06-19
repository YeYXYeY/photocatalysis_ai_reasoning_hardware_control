"""Compatibility entrypoint for manual lighting and reactor runs."""

from __future__ import annotations

import argparse

from app.reactor_controller import build_default_reactor
from app.runtime import build_runtime_context


def parse_args() -> argparse.Namespace:
    """Parse manual control arguments for legacy workflows."""
    parser = argparse.ArgumentParser(description="Legacy reactor helper entrypoint")
    parser.add_argument(
        "--func",
        type=str,
        default="lighting",
        help="Operation to execute: lighting, start_reactor, or stop_reactor.",
    )
    parser.add_argument(
        "--taskfile",
        type=str,
        default=None,
        help="Accepted for compatibility with shared station-server commands.",
    )
    parser.add_argument(
        "--lighting-hours",
        type=float,
        default=0.25,
        help="Lighting-only duration in hours.",
    )
    parser.add_argument(
        "--reaction-hours",
        type=float,
        default=12.0,
        help="Reaction duration in hours for start_reactor.",
    )
    parser.add_argument(
        "--cooling-mode",
        type=int,
        default=0,
        help="Cooling mode: 0=off, 1=always on, 2=PID + PWM.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the requested legacy-compatible reactor routine."""
    args = parse_args()
    runtime = build_runtime_context()
    reactor = build_default_reactor(
        runtime,
        duration_seconds=int(args.reaction_hours * 3600),
        cooling_mode=args.cooling_mode,
    )

    if args.func == "lighting":
        reactor.lighting(args.lighting_hours)
        return 0
    if args.func in {"start_reactor", "start_reaction"}:
        reactor.start()
        return 0
    if args.func == "stop_reactor":
        reactor.stop()
        return 0

    print(
        "Unsupported operation. Use 'lighting', 'start_reactor', or 'stop_reactor'."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
