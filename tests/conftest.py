import pytest


@pytest.fixture(autouse=True)
def isolated_presets(tmp_path, monkeypatch):
    """Point every test at an empty presets file, never the real ~/.config one."""
    path = tmp_path / "presets.toml"
    monkeypatch.setenv("LAPBELL_PRESETS", str(path))
    return path
