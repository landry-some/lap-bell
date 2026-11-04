from pathlib import Path

import pytest

from lap_bell import cli
from lap_bell.presets import Preset, PresetError, load_presets, looks_like_duration, presets_path

EXAMPLE = Path(__file__).parent.parent / "examples" / "presets.toml"


def test_path_from_env_var():
    assert presets_path({"LAPBELL_PRESETS": "/x/p.toml"}) == Path("/x/p.toml")


def test_path_from_xdg_config_home():
    assert presets_path({"XDG_CONFIG_HOME": "/cfg"}) == Path("/cfg/lap-bell/presets.toml")


def test_path_default(monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: Path("/home/someone"))
    assert presets_path({}) == Path("/home/someone/.config/lap-bell/presets.toml")


def test_missing_file_means_no_presets(tmp_path):
    assert load_presets(tmp_path / "nope.toml") == {}


def test_load_example_file():
    presets = load_presets(EXAMPLE)
    assert presets["tea"] == Preset("tea", 240, "")
    assert presets["eggs"] == Preset("eggs", 450, "Soft-boiled eggs")
    assert presets["standup"].seconds == 900


@pytest.mark.parametrize(
    "content, message",
    [
        ("tea = ", "presets.toml"),
        ('tea = "soon"', "preset 'tea': bad duration"),
        ("tea = 4", "needs a duration string"),
        ('tea = { label = "x" }', "needs a duration string"),
    ],
)
def test_bad_files(isolated_presets, content, message):
    isolated_presets.write_text(content)
    with pytest.raises(PresetError, match=message):
        load_presets(isolated_presets)


def fake_timer(monkeypatch):
    seen = {}
    monkeypatch.setattr(cli, "run_timer", lambda seconds, label: seen.update(seconds=seconds, label=label))
    monkeypatch.setattr(cli, "notify", lambda title, body: seen.update(body=body))
    return seen


def test_timer_uses_preset_and_its_label(isolated_presets, monkeypatch):
    isolated_presets.write_text('eggs = { duration = "7m30s", label = "Soft-boiled eggs" }\ntea = "4m"\n')
    seen = fake_timer(monkeypatch)
    assert cli.main(["timer", "eggs"]) == 0
    assert seen == {"seconds": 450, "label": "Soft-boiled eggs", "body": "Soft-boiled eggs"}
    assert cli.main(["timer", "tea"]) == 0
    assert seen["label"] == "tea"
    assert cli.main(["timer", "tea", "oolong"]) == 0
    assert seen["label"] == "oolong"


def test_timer_bad_preset_file(isolated_presets, monkeypatch, capsys):
    isolated_presets.write_text("tea = [")
    fake_timer(monkeypatch)
    assert cli.main(["timer", "5m"]) == 2
    assert "presets.toml" in capsys.readouterr().err


def test_presets_command_lists(isolated_presets, capsys):
    isolated_presets.write_text('tea = "4m"\nfocus = { duration = "25m", label = "Focus block" }\nlong = "1h30m"\n')
    assert cli.main(["presets"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "tea       04:00",
        "focus     25:00  Focus block",
        "long    1:30:00",
    ]


def test_presets_command_empty(isolated_presets, capsys):
    assert cli.main(["presets"]) == 0
    assert capsys.readouterr().out.strip() == f"no presets in {isolated_presets}"


@pytest.mark.parametrize("name, expected", [("10m", True), ("25", True), ("1:30", True), ("tea", False), ("m", False)])
def test_looks_like_duration(name, expected):
    assert looks_like_duration(name) is expected


def test_timer_warns_when_preset_hides_duration(isolated_presets, monkeypatch, capsys):
    isolated_presets.write_text('10m = "5m"\ntea = "4m"\n')
    seen = fake_timer(monkeypatch)
    assert cli.main(["timer", "10m"]) == 0
    assert seen["seconds"] == 300
    err = capsys.readouterr().err
    assert "preset '10m' (05:00), not the duration 10m" in err
    assert cli.main(["timer", "tea"]) == 0
    assert capsys.readouterr().err == ""
