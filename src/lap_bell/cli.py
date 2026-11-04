"""Command-line entry point: ``lapbell``."""

import argparse
import sys
from datetime import datetime

from . import __version__
from .duration import format_clock, parse_duration, seconds_until
from .notify import notify
from .presets import PresetError, load_presets, looks_like_duration, presets_path
from .stopwatch import run_stopwatch
from .timer import run_timer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lapbell", description="Terminal timer and stopwatch with desktop notifications.")
    parser.add_argument("--version", action="version", version=f"lapbell {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    timer = sub.add_parser("timer", help="count down and notify when time is up")
    timer.add_argument(
        "duration",
        help="a preset name, e.g. 25m, 1h30m, 90s, 1:30 (a bare number means minutes), or an end time like @14:30",
    )
    timer.add_argument("label", nargs="*", help="text shown in the countdown and the notification")

    sub.add_parser("stopwatch", help="count up; Enter records a lap, q stops")
    sub.add_parser("presets", help="list the presets from the presets file")
    return parser


def cmd_timer(args) -> int:
    label = " ".join(args.label)
    try:
        presets = load_presets(presets_path())
    except PresetError as err:
        print(f"lapbell: {err}", file=sys.stderr)
        return 2
    preset = presets.get(args.duration)
    if preset:
        if looks_like_duration(preset.name):
            print(
                f"lapbell: using preset {preset.name!r} ({format_clock(preset.seconds)}), "
                f"not the duration {preset.name}; rename the preset to get the duration back",
                file=sys.stderr,
            )
        seconds = preset.seconds
        label = label or preset.label or preset.name
    else:
        try:
            if args.duration.startswith("@"):
                seconds = seconds_until(args.duration[1:], datetime.now())
            else:
                seconds = parse_duration(args.duration)
        except ValueError as err:
            print(f"lapbell: {err}", file=sys.stderr)
            return 2
    try:
        run_timer(seconds, label)
    except KeyboardInterrupt:
        print("\ncancelled", file=sys.stderr)
        return 130
    notify("Time is up", label or f"{format_clock(seconds)} timer finished")
    return 0


def cmd_presets() -> int:
    path = presets_path()
    try:
        presets = load_presets(path)
    except PresetError as err:
        print(f"lapbell: {err}", file=sys.stderr)
        return 2
    if not presets:
        print(f"no presets in {path}")
        return 0
    width = max(len(name) for name in presets)
    for preset in presets.values():
        line = f"{preset.name.ljust(width)}  {format_clock(preset.seconds):>8}"
        print(f"{line}  {preset.label}" if preset.label else line)
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "timer":
        return cmd_timer(args)
    if args.command == "stopwatch":
        run_stopwatch()
        return 0
    if args.command == "presets":
        return cmd_presets()
    return 2


if __name__ == "__main__":
    sys.exit(main())
