"""Send a desktop notification, falling back to the terminal bell."""

import shutil
import subprocess
import sys


def notify_command(title: str, body: str, platform: str = sys.platform, which=shutil.which):
    """Return the command that shows a notification on this platform, or None."""
    if platform.startswith("linux") or "bsd" in platform:
        if which("notify-send"):
            return ["notify-send", "--app-name=lap-bell", title, body]
    elif platform == "darwin":
        if which("osascript"):
            script = f"display notification {_applescript_str(body)} with title {_applescript_str(title)}"
            return ["osascript", "-e", script]
    return None


def _applescript_str(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def notify(title: str, body: str, out=None) -> bool:
    """Show a desktop notification. Rings the terminal bell if that isn't possible.

    Returns True if a desktop notification was sent.
    """
    cmd = notify_command(title, body)
    if cmd:
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            if result.returncode == 0:
                return True
        except (OSError, subprocess.TimeoutExpired):
            pass
    out = out or sys.stdout
    out.write("\a")
    out.flush()
    return False
