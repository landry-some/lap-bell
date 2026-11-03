import pytest

from lap_bell.duration import format_clock, parse_duration


@pytest.mark.parametrize(
    "text, seconds",
    [
        ("90s", 90),
        ("25m", 1500),
        ("1h", 3600),
        ("1h30m", 5400),
        ("1h2m3s", 3723),
        ("2m30s", 150),
        ("1.5h", 5400),
        ("25", 1500),
        ("1:30", 90),
        ("0:25:00", 1500),
        ("1:00:05", 3605),
        (" 10M ", 600),
    ],
)
def test_parse_valid(text, seconds):
    assert parse_duration(text) == seconds


@pytest.mark.parametrize(
    "text",
    ["", "   ", "abc", "10x", "m", "5m5h", "5m5m", "1:75", "1:2:3:4", "1:-5", "0s", "0:00", "5m ago"],
)
def test_parse_invalid(text):
    with pytest.raises(ValueError):
        parse_duration(text)


@pytest.mark.parametrize(
    "seconds, text",
    [
        (0, "00:00"),
        (-3, "00:00"),
        (0.2, "00:01"),
        (59, "00:59"),
        (60, "01:00"),
        (1500, "25:00"),
        (3599.5, "1:00:00"),
        (3723, "1:02:03"),
    ],
)
def test_format_clock(seconds, text):
    assert format_clock(seconds) == text
