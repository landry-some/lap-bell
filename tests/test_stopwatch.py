import io

import pytest

from lap_bell import cli
from lap_bell.stopwatch import Lap, Stopwatch, format_elapsed, lap_table, run_stopwatch


class TickingClock:
    """Each call returns the next value from a list."""

    def __init__(self, *times):
        self.times = list(times)

    def __call__(self):
        return self.times.pop(0)


@pytest.mark.parametrize(
    "seconds, text",
    [(0, "00:00.0"), (1.25, "00:01.2"), (61.99, "01:01.9"), (0.3, "00:00.3"), (3725.5, "1:02:05.5"), (-1, "00:00.0")],
)
def test_format_elapsed(seconds, text):
    assert format_elapsed(seconds) == text


def test_laps_track_split_and_total():
    watch = Stopwatch(TickingClock(10.0, 12.5, 15.0, 22.0))
    assert watch.lap() == Lap(1, 2.5, 2.5)
    assert watch.lap() == Lap(2, 2.5, 5.0)
    assert watch.lap() == Lap(3, 7.0, 12.0)


def test_lap_table_marks_fastest_and_slowest():
    table = lap_table([Lap(1, 2.5, 2.5), Lap(2, 1.0, 3.5), Lap(3, 7.0, 10.5)])
    assert table.splitlines() == [
        "lap     time    total",
        "  1  00:02.5  00:02.5",
        "  2  00:01.0  00:03.5  fastest",
        "  3  00:07.0  00:10.5  slowest",
    ]


def test_lap_table_single_lap_has_no_marks():
    assert "fastest" not in lap_table([Lap(1, 4.0, 4.0)])
    assert lap_table([]) == ""


def test_lap_table_equal_laps_have_no_marks():
    table = lap_table([Lap(1, 2.0, 2.0), Lap(2, 2.04, 4.04)])
    assert "fastest" not in table and "slowest" not in table


def test_run_stopwatch_until_q():
    out = io.StringIO()
    watch = run_stopwatch(io.StringIO("\n\nq\nignored\n"), out, TickingClock(0.0, 1.0, 3.0, 3.5))
    assert [l.total for l in watch.laps] == [1.0, 3.0, 3.5]
    text = out.getvalue()
    assert "lap 1  00:01.0  (total 00:01.0)" in text
    assert "lap 2  00:02.0  (total 00:03.0)" in text
    assert "  3  00:00.5  00:03.5  fastest" in text


def test_run_stopwatch_eof_stops():
    watch = run_stopwatch(io.StringIO(""), io.StringIO(), TickingClock(0.0, 4.0))
    assert watch.laps == [Lap(1, 4.0, 4.0)]


def test_run_stopwatch_ctrl_c_still_prints_table():
    class Interrupting:
        def __iter__(self):
            yield "\n"
            raise KeyboardInterrupt

    out = io.StringIO()
    watch = run_stopwatch(Interrupting(), out, TickingClock(0.0, 1.0, 3.0))
    assert len(watch.laps) == 2
    assert "slowest" in out.getvalue()


def test_cli_stopwatch(monkeypatch):
    called = []
    monkeypatch.setattr(cli, "run_stopwatch", lambda: called.append(True))
    assert cli.main(["stopwatch"]) == 0
    assert called == [True]
