import io

import pytest

from lap_bell import cli
from lap_bell.timer import run_timer


class FakeClock:
    def __init__(self, start=100.0):
        self.now = start
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def frames(output):
    return [f.replace("\x1b[K", "") for f in output.strip("\n").split("\r") if f]


def test_counts_down_each_second():
    clock = FakeClock()
    out = io.StringIO()
    run_timer(3, "tea", clock=clock, sleep=clock.sleep, out=out)
    assert frames(out.getvalue()) == ["00:03  tea", "00:02  tea", "00:01  tea", "00:00  tea"]
    assert sum(clock.sleeps) == pytest.approx(3)
    assert out.getvalue().endswith("\n")


def test_fractional_start_aligns_to_seconds():
    clock = FakeClock()
    out = io.StringIO()
    run_timer(2.5, clock=clock, sleep=clock.sleep, out=out)
    assert frames(out.getvalue()) == ["00:03", "00:02", "00:01", "00:00"]
    assert clock.sleeps[0] == pytest.approx(0.5)


def test_slow_sleep_does_not_drift():
    clock = FakeClock()
    out = io.StringIO()

    def late_sleep(seconds):
        clock.now += seconds + 0.3

    run_timer(3, clock=clock, sleep=late_sleep, out=out)
    # Overshooting sleeps get absorbed; the timer still ends at the 3 s mark or just after.
    assert clock.now - 100.0 < 3.5
    assert frames(out.getvalue())[-1] == "00:00"


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
