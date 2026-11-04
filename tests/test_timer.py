import io
import time
from datetime import datetime

import pytest

from lap_bell import cli
from lap_bell.timer import awake_clock, run_timer


class FakeClock:
    def __init__(self, start=100.0):
        self.now = start
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class Tty(io.StringIO):
    def isatty(self):
        return True


def frames(output):
    return [f.replace("\x1b[K", "") for f in output.strip("\n").split("\r") if f]


def test_counts_down_each_second():
    clock = FakeClock()
    out = Tty()
    run_timer(3, "tea", clock=clock, sleep=clock.sleep, out=out)
    assert frames(out.getvalue()) == ["00:03  tea", "00:02  tea", "00:01  tea", "00:00  tea"]
    assert sum(clock.sleeps) == pytest.approx(3)
    assert out.getvalue().endswith("\n")


def test_fractional_start_aligns_to_seconds():
    clock = FakeClock()
    out = Tty()
    run_timer(2.5, clock=clock, sleep=clock.sleep, out=out)
    assert frames(out.getvalue()) == ["00:03", "00:02", "00:01", "00:00"]
    assert clock.sleeps[0] == pytest.approx(0.5)


def test_slow_sleep_does_not_drift():
    clock = FakeClock()
    out = Tty()

    def late_sleep(seconds):
        clock.now += seconds + 0.3

    run_timer(3, clock=clock, sleep=late_sleep, out=out)
    # Overshooting sleeps get absorbed; the timer still ends at the 3 s mark or just after.
    assert clock.now - 100.0 < 3.5
    assert frames(out.getvalue())[-1] == "00:00"


def test_suspend_mid_countdown_ends_at_wake():
    clock = FakeClock()
    out = Tty()
    naps = []

    def suspended_sleep(seconds):
        naps.append(seconds)
        clock.now += seconds if len(naps) > 1 else 3600  # first sleep: laptop closed for an hour

    run_timer(600, clock=clock, sleep=suspended_sleep, out=out)
    assert len(naps) == 1
    assert frames(out.getvalue()) == ["10:00", "00:00"]


def test_awake_clock_per_platform(monkeypatch):
    if hasattr(time, "CLOCK_BOOTTIME"):
        assert abs(awake_clock("linux")() - time.clock_gettime(time.CLOCK_BOOTTIME)) < 1
    assert awake_clock("win32") is time.monotonic
    monkeypatch.delattr(time, "CLOCK_BOOTTIME", raising=False)
    assert awake_clock("linux") is time.monotonic


def test_non_tty_prints_start_and_end_lines_only():
    clock = FakeClock()
    out = io.StringIO()
    run_timer(3, "tea", clock=clock, sleep=clock.sleep, out=out)
    assert out.getvalue() == "00:03  tea\n00:00  tea\n"
    assert sum(clock.sleeps) == pytest.approx(3)


def test_narrow_terminal_cuts_the_line():
    clock = FakeClock()
    out = Tty()
    run_timer(1, "a rather long label", clock=clock, sleep=clock.sleep, out=out, width=12)
    assert frames(out.getvalue()) == ["00:01  a ra", "00:00  a ra"]


def test_cli_rejects_bad_duration(capsys):
    assert cli.main(["timer", "soon"]) == 2
    assert "bad duration" in capsys.readouterr().err


def test_cli_notifies_with_label(monkeypatch):
    seen = {}
    monkeypatch.setattr(cli, "run_timer", lambda seconds, label: seen.update(seconds=seconds, label=label))
    monkeypatch.setattr(cli, "notify", lambda title, body: seen.update(title=title, body=body))
    assert cli.main(["timer", "4m", "green", "tea"]) == 0
    assert seen == {"seconds": 240, "label": "green tea", "title": "Time is up", "body": "green tea"}


def test_cli_cancel_skips_notification(monkeypatch, capsys):
    def interrupted(seconds, label):
        raise KeyboardInterrupt

    notified = []
    monkeypatch.setattr(cli, "run_timer", interrupted)
    monkeypatch.setattr(cli, "notify", lambda *a: notified.append(a))
    assert cli.main(["timer", "1m"]) == 130
    assert notified == []
    assert "cancelled" in capsys.readouterr().err


def test_cli_absolute_end_time(monkeypatch):
    class FixedNow(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 3, 10, 14, 0, 0)

    seen = {}
    monkeypatch.setattr(cli, "datetime", FixedNow)
    monkeypatch.setattr(cli, "run_timer", lambda seconds, label: seen.update(seconds=seconds, label=label))
    monkeypatch.setattr(cli, "notify", lambda title, body: None)
    assert cli.main(["timer", "@14:30", "meeting"]) == 0
    assert seen == {"seconds": 1800, "label": "meeting"}


def test_cli_rejects_bad_end_time(capsys):
    assert cli.main(["timer", "@25:00"]) == 2
    assert "no such time of day" in capsys.readouterr().err
