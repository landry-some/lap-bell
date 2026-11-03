# lap-bell

A terminal timer and stopwatch. `lapbell timer 25m` counts down in the terminal and
sends a desktop notification when the time is up, so you notice it even when the
terminal is buried under other windows. `lapbell stopwatch` records laps when you press
Enter.

It's meant for people who live in a terminal and want a quick "remind me in 10 minutes"
or "how long does this build take" without opening an app or reaching for a phone.

Built with Python 3.11+ and the standard library only. Notifications go through
`notify-send` on Linux and `osascript` on macOS. If neither is available, lap-bell rings
the terminal bell instead.

Status: early (v0.1). See [ROADMAP.md](ROADMAP.md) for what's planned.

## Install

```bash
git clone https://github.com/landry-some/lap-bell.git
cd lap-bell
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
```

On Linux, `notify-send` comes from the `libnotify-bin` package (Debian/Ubuntu) or
`libnotify` (Fedora/Arch).

## Run

Usage is filled in as the v0.1 features land.

## Test

```bash
pytest
```

## License

MIT, see [LICENSE](LICENSE).
