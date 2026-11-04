"""Named timer presets from a TOML file.

Each top-level key is a preset. The value is either a duration string or a table
with ``duration`` and an optional ``label``:

    tea = "4m"
    focus = { duration = "25m", label = "Focus block" }
"""

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .duration import parse_duration


@dataclass
class Preset:
    name: str
    seconds: float
    label: str


class PresetError(Exception):
    pass


def presets_path(env=os.environ) -> Path:
    """``$LAPBELL_PRESETS``, else ``$XDG_CONFIG_HOME/lap-bell/presets.toml``,
    else ``~/.config/lap-bell/presets.toml``."""
    if env.get("LAPBELL_PRESETS"):
        return Path(env["LAPBELL_PRESETS"]).expanduser()
    base = env.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "lap-bell" / "presets.toml"


def looks_like_duration(name: str) -> bool:
    """True if ``name`` would also parse as a duration, so a preset with that name
    hides the duration on the command line."""
    try:
        parse_duration(name)
    except ValueError:
        return False
    return True


def load_presets(path: Path) -> dict[str, Preset]:
    """Read presets from ``path``. A missing file means no presets."""
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except FileNotFoundError:
        return {}
    except tomllib.TOMLDecodeError as err:
        raise PresetError(f"{path}: {err}") from None

    presets = {}
    for name, value in data.items():
        if isinstance(value, str):
            duration, label = value, ""
        elif isinstance(value, dict) and isinstance(value.get("duration"), str):
            duration, label = value["duration"], str(value.get("label", ""))
        else:
            raise PresetError(f'{path}: preset {name!r} needs a duration string, e.g. {name} = "5m"')
        try:
            seconds = parse_duration(duration)
        except ValueError as err:
            raise PresetError(f"{path}: preset {name!r}: {err}") from None
        presets[name] = Preset(name, seconds, label)
    return presets
