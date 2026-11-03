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

### Timer

```bash
lapbell timer 25m                 # count down 25 minutes
lapbell timer 4m green tea        # the label shows in the countdown and the notification
lapbell timer 1:30                # MM:SS or HH:MM:SS also work
lapbell timer 10                  # a bare number means minutes
```

Durations: `90s`, `25m`, `1h`, `1h30m`, `1.5h`, `1:30`, `0:25:00`. The countdown redraws
one line in the terminal. When it hits zero you get a desktop notification ("Time is
up" plus the label). Ctrl-C cancels without notifying.

### Stopwatch

```bash
lapbell stopwatch
```

Press Enter to record a lap. Type `q` and Enter, or press Ctrl-D or Ctrl-C, to stop.
The time at stop counts as the last lap, and lap-bell prints a table with each lap's
time, the running total, and the fastest and slowest laps.

```
lap     time    total
  1  00:42.1  00:42.1
  2  00:38.6  01:20.7  fastest
  3  00:51.3  02:12.0  slowest
```

### Presets

Put named timers in `~/.config/lap-bell/presets.toml` (or
`$XDG_CONFIG_HOME/lap-bell/presets.toml`, or any file named by `$LAPBELL_PRESETS`):

```toml
tea = "4m"
focus = { duration = "25m", label = "Focus block" }
```

```bash
lapbell timer focus               # 25 minutes, labelled "Focus block"
lapbell timer tea oolong          # a label on the command line wins over the preset's
lapbell presets                   # list what's defined
```

There's a sample file in [examples/presets.toml](examples/presets.toml). Try it without
touching your config:

```bash
LAPBELL_PRESETS=examples/presets.toml lapbell presets
```

A preset name wins over a duration with the same text.

## Test

```bash
pytest
```

## License

MIT, see [LICENSE](LICENSE).
