import io
import subprocess

from lap_bell import notify as notify_mod
from lap_bell.notify import notify, notify_command


def has(*names):
    return lambda name: f"/usr/bin/{name}" if name in names else None


def test_linux_uses_notify_send():
    cmd = notify_command("Time is up", "tea", platform="linux", which=has("notify-send"))
    assert cmd == ["notify-send", "--app-name=lap-bell", "Time is up", "tea"]


def test_linux_without_notify_send():
    assert notify_command("t", "b", platform="linux", which=has()) is None


def test_macos_uses_osascript_and_escapes_quotes():
    cmd = notify_command("Time is up", 'say "hi" \\ bye', platform="darwin", which=has("osascript"))
    assert cmd[:2] == ["osascript", "-e"]
    assert cmd[2] == 'display notification "say \\"hi\\" \\\\ bye" with title "Time is up"'


def test_unknown_platform():
    assert notify_command("t", "b", platform="win32", which=has("notify-send")) is None


def test_notify_falls_back_to_bell(monkeypatch):
    monkeypatch.setattr(notify_mod, "notify_command", lambda title, body: None)
    out = io.StringIO()
    assert notify("t", "b", out=out) is False
    assert out.getvalue() == "\a"


def test_notify_runs_command(monkeypatch):
    calls = []
    monkeypatch.setattr(notify_mod, "notify_command", lambda title, body: ["notify-send", title, body])

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(notify_mod.subprocess, "run", fake_run)
    out = io.StringIO()
    assert notify("Time is up", "tea", out=out) is True
    assert calls == [["notify-send", "Time is up", "tea"]]
    assert out.getvalue() == ""


def test_notify_bell_when_command_fails(monkeypatch):
    monkeypatch.setattr(notify_mod, "notify_command", lambda title, body: ["notify-send", title, body])
    monkeypatch.setattr(notify_mod.subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1))
    out = io.StringIO()
    assert notify("t", "b", out=out) is False
    assert out.getvalue() == "\a"
