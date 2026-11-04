"""Parse and format durations like ``25m``, ``1h30m``, ``90s`` or ``1:30``."""

import re
from datetime import datetime, timedelta

_UNIT_SECONDS = {"h": 3600, "m": 60, "s": 1}
_UNIT_PART = re.compile(r"(\d+(?:\.\d+)?)([hms])")


def parse_duration(text: str) -> float:
    """Return the number of seconds in ``text``.

    Accepted forms:
      - unit form: ``90s``, ``25m``, ``1h30m``, ``1.5h`` (units h, m, s, each at most once,
        in that order)
      - a bare number, read as minutes: ``25``
      - clock form: ``MM:SS`` or ``HH:MM:SS``
    Raises ValueError for anything else, and for a zero duration.
    """
    raw = text.strip().lower()
    if not raw:
        raise ValueError("empty duration")

    if ":" in raw:
        seconds = _parse_clock(raw)
    elif re.fullmatch(r"\d+(?:\.\d+)?", raw):
        seconds = float(raw) * 60
    else:
        seconds = _parse_units(raw)

    if seconds <= 0:
        raise ValueError(f"duration must be more than zero: {text!r}")
    return seconds


def _parse_clock(raw: str) -> float:
    parts = raw.split(":")
    if len(parts) not in (2, 3) or not all(p.isdigit() for p in parts):
        raise ValueError(f"bad clock duration: {raw!r} (use MM:SS or HH:MM:SS)")
    numbers = [int(p) for p in parts]
    if any(n >= 60 for n in numbers[1:]):
        raise ValueError(f"minutes and seconds must be below 60: {raw!r}")
    if len(numbers) == 2:
        minutes, secs = numbers
        return minutes * 60 + secs
    hours, minutes, secs = numbers
    return hours * 3600 + minutes * 60 + secs


def _parse_units(raw: str) -> float:
    pos = 0
    total = 0.0
    seen = ""
    for match in _UNIT_PART.finditer(raw):
        if match.start() != pos:
            break
        unit = match.group(2)
        if seen and "hms".index(unit) <= "hms".index(seen[-1]):
            raise ValueError(f"units out of order or repeated: {raw!r}")
        seen += unit
        total += float(match.group(1)) * _UNIT_SECONDS[unit]
        pos = match.end()
    if pos != len(raw) or not seen:
        raise ValueError(f"bad duration: {raw!r} (try 25m, 1h30m, 90s or 1:30)")
    return total


def seconds_until(text: str, now: datetime) -> float:
    """Return the seconds from ``now`` until the wall-clock time ``HH:MM`` or
    ``HH:MM:SS`` (24-hour). A time that has already passed today means tomorrow."""
    parts = text.strip().split(":")
    if len(parts) not in (2, 3) or not all(p.isdigit() for p in parts):
        raise ValueError(f"bad end time: {text!r} (use HH:MM or HH:MM:SS, e.g. @14:30)")
    hour, minute, second = (int(p) for p in parts + ["0"] * (3 - len(parts)))
    if hour > 23 or minute > 59 or second > 59:
        raise ValueError(f"no such time of day: {text!r}")
    end = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
    if end <= now:
        end += timedelta(days=1)
    return (end - now).total_seconds()


def format_clock(seconds: float) -> str:
    """Format seconds as ``MM:SS``, or ``H:MM:SS`` from one hour up. Rounds up partial
    seconds, so a countdown shows 00:01 until it really hits zero."""
    whole = max(0, int(-(-seconds // 1)))
    hours, rest = divmod(whole, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
