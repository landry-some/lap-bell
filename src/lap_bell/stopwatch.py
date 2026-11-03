"""Stopwatch with laps. Enter records a lap, ``q`` or end of input stops."""

import sys
import time
from dataclasses import dataclass


@dataclass
class Lap:
    number: int
    lap: float  # time since the previous lap
    total: float  # time since start


class Stopwatch:
    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._start = clock()
        self.laps: list[Lap] = []

    def elapsed(self) -> float:
        return self._clock() - self._start

    def lap(self) -> Lap:
        total = self.elapsed()
        previous = self.laps[-1].total if self.laps else 0.0
        lap = Lap(len(self.laps) + 1, total - previous, total)
        self.laps.append(lap)
        return lap


def format_elapsed(seconds: float) -> str:
    """Format as ``MM:SS.t``, or ``H:MM:SS.t`` from one hour up (tenths truncated)."""
    tenths = int(max(0.0, seconds) * 10 + 1e-6)
    whole, tenth = divmod(tenths, 10)
    hours, rest = divmod(whole, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}.{tenth}"
    return f"{minutes:02d}:{secs:02d}.{tenth}"


def lap_table(laps: list[Lap]) -> str:
    """Render laps as an aligned table, marking the fastest and slowest lap."""
    if not laps:
        return ""
    rows = [("lap", "time", "total", "")]
    fastest = min(laps, key=lambda l: l.lap)
    slowest = max(laps, key=lambda l: l.lap)
    if format_elapsed(fastest.lap) == format_elapsed(slowest.lap):
        fastest = slowest = None  # one lap, or all laps look the same: nothing to mark
    for lap in laps:
        mark = "fastest" if lap is fastest else "slowest" if lap is slowest else ""
        rows.append((str(lap.number), format_elapsed(lap.lap), format_elapsed(lap.total), mark))
    widths = [max(len(row[i]) for row in rows) for i in range(3)]
    lines = []
    for row in rows:
        cells = [row[0].rjust(widths[0]), row[1].rjust(widths[1]), row[2].rjust(widths[2])]
        lines.append("  ".join(cells + ([row[3]] if row[3] else [])))
    return "\n".join(lines)


def run_stopwatch(stdin=None, out=None, clock=time.monotonic) -> Stopwatch:
    """Run an interactive stopwatch until ``q``, end of input or Ctrl-C.

    The time when it stops counts as the last lap, so the table always covers the
    whole run.
    """
    stdin = stdin or sys.stdin
    out = out or sys.stdout
    out.write("Stopwatch started. Enter = lap, q + Enter or Ctrl-D = stop.\n")
    out.flush()
    watch = Stopwatch(clock)
    try:
        for line in stdin:
            if line.strip().lower() in ("q", "quit", "stop"):
                break
            lap = watch.lap()
            out.write(f"lap {lap.number}  {format_elapsed(lap.lap)}  (total {format_elapsed(lap.total)})\n")
            out.flush()
    except KeyboardInterrupt:
        out.write("\n")
    watch.lap()
    out.write("\n" + lap_table(watch.laps) + "\n")
    out.flush()
    return watch
