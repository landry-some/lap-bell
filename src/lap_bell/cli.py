"""Command-line entry point: ``lapbell``."""

import argparse
import sys

from . import __version__
from .duration import format_clock, parse_duration
from .notify import notify
from .stopwatch import run_stopwatch
from .timer import run_timer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lapbell", description="Terminal timer and stopwatch with desktop notifications.")
    parser.add_argument("--version", action="version", version=f"lapbell {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    timer = sub.add_parser("timer", help="count down and notify when time is up")
    timer.add_argument("duration", help="e.g. 25m, 1h30m, 90s, 1:30 (a bare number means minutes)")
    timer.add_argument("label", nargs="*", help="text shown in the countdown and the notification")

    sub.add_parser("stopwatch", help="count up; Enter records a lap, q stops")
    return parser


def cmd_timer(args) -> int:
    try:
        seconds = parse_duration(args.duration)
    except ValueError as err:
        print(f"lapbell: {err}", file=sys.stderr)
        return 2
    label = " ".join(args.label)
    try:
        run_timer(seconds, label)
    except KeyboardInterrupt:
        print("\ncancelled", file=sys.stderr)
        return 130
    notify("Time is up", label or f"{format_clock(seconds)} timer finished")
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "timer":
        return cmd_timer(args)
    if args.command == "stopwatch":
        run_stopwatch()
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
