"""Countdown timer with a live line in the terminal."""

import shutil
import sys
import time

from .duration import format_clock


def run_timer(
    seconds: float, label: str = "", *, clock=time.monotonic, sleep=time.sleep, out=None, width=None
) -> None:
    """Count down ``seconds``, redrawing one terminal line until time is up.

    Uses a monotonic clock, so the end time doesn't move if the wall clock changes.
    KeyboardInterrupt propagates to the caller, which treats it as a cancel.

    When ``out`` isn't a terminal (a pipe or a log file), it gets one line at the start
    and one at the end instead of a redrawn line. On a terminal the line is cut to
    ``width`` (default: the terminal width) so it never wraps and breaks the redraw.
    """
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
