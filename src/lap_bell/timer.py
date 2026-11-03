"""Countdown timer with a live line in the terminal."""

import sys
import time

from .duration import format_clock


def run_timer(seconds: float, label: str = "", *, clock=time.monotonic, sleep=time.sleep, out=None) -> None:
    """Count down ``seconds``, redrawing one terminal line until time is up.

    Uses a monotonic clock, so the end time doesn't move if the wall clock changes.
    KeyboardInterrupt propagates to the caller, which treats it as a cancel.
    """
    out = out or sys.stdout
    suffix = f"  {label}" if label else ""
    end = clock() + seconds
    while True:
        left = end - clock()
        out.write(f"\r{format_clock(left)}{suffix}\x1b[K")
        out.flush()
        if left <= 0:
            break
        # Wake up right after the next whole second boundary so the display stays on time.
        sleep(min(left, (left % 1) or 1.0))
    out.write("\n")
    out.flush()
