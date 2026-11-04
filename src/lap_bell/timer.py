"""Countdown timer with a live line in the terminal."""

import shutil
import sys
import time

from .duration import format_clock


def awake_clock(platform: str = sys.platform):
    """Return a clock that keeps counting while the machine sleeps and ignores
    wall-clock changes.

    ``time.monotonic`` stops during suspend on Linux, so a timer would run late by the
    time the laptop was closed. Linux has CLOCK_BOOTTIME for this; on macOS
    CLOCK_MONOTONIC already counts sleep. Elsewhere, fall back to ``time.monotonic``.
    """
    if platform.startswith("linux") and hasattr(time, "CLOCK_BOOTTIME"):
        return lambda: time.clock_gettime(time.CLOCK_BOOTTIME)
    if platform == "darwin" and hasattr(time, "CLOCK_MONOTONIC"):
        return lambda: time.clock_gettime(time.CLOCK_MONOTONIC)
    return time.monotonic


def run_timer(
    seconds: float, label: str = "", *, clock=None, sleep=time.sleep, out=None, width=None
) -> None:
    """Count down ``seconds``, redrawing one terminal line until time is up.

    The default clock keeps counting through suspend and ignores wall-clock changes, so
    the timer ends on time after the laptop sleeps (see ``awake_clock``). Sleeps are at
    most a second, so the countdown catches up as soon as the machine wakes.
    KeyboardInterrupt propagates to the caller, which treats it as a cancel.

    When ``out`` isn't a terminal (a pipe or a log file), it gets one line at the start
    and one at the end instead of a redrawn line. On a terminal the line is cut to
    ``width`` (default: the terminal width) so it never wraps and breaks the redraw.
    """
    clock = clock or awake_clock()
    out = out or sys.stdout
    live = out.isatty()
    if width is None:
        width = shutil.get_terminal_size().columns
    suffix = f"  {label}" if label else ""
    end = clock() + seconds
    first = True
    while True:
        left = end - clock()
        line = f"{format_clock(left)}{suffix}"
        if live:
            out.write(f"\r{line[: max(1, width - 1)]}\x1b[K")
            out.flush()
        elif first or left <= 0:
            out.write(line + "\n")
            out.flush()
        first = False
        if left <= 0:
            break
        # Wake up right after the next whole second boundary so the display stays on time.
        sleep(min(left, (left % 1) or 1.0))
    if live:
        out.write("\n")
        out.flush()
