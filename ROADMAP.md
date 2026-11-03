# Roadmap

Planned work after v0.1, with rough estimates. Total: about 35 hours.

## v0.1 (current)

- [x] Duration parsing (`25m`, `1h30m`, `90s`, `1:30`, `0:25:00`)
- [x] `lapbell timer` with live countdown and a desktop notification at the end
- [x] `lapbell stopwatch` with laps and a split table
- [x] Named presets from `~/.config/lap-bell/presets.toml`

## Features

- [ ] Pause and resume a running timer with a key press (3h)
- [ ] Absolute end times: `lapbell timer @14:30` (2h)
- [ ] Pomodoro mode: work/break cycles with a counter (3h)
- [ ] Run timers in the background and list/cancel them (`lapbell ls`, `lapbell cancel`) (5h)
- [ ] Optional sound on finish, from a configurable file (2h)
- [ ] Windows notifications through PowerShell toast (3h)
- [ ] History log of finished timers and `lapbell history` with daily totals (3h)
- [ ] Live stopwatch display with single-key laps (raw terminal mode) (3h)

## Bugs and edge cases

- [ ] Keep the countdown correct after the laptop sleeps or the clock jumps (1.5h)
- [ ] Handle a narrow or non-TTY output without broken `\r` lines (1h)
- [ ] Warn when a preset name looks like a duration and hides it, e.g. `10m = "5m"` (0.5h)

## Refactors

- [ ] Move terminal drawing into one renderer used by timer and stopwatch (2h)

## Tests

- [ ] Notifier tests for macOS and fallback paths on every platform (1h)
- [ ] End-to-end CLI tests with a fake clock for timer and stopwatch (1.5h)

## Docs

- [ ] Shell completions for bash and zsh, plus a short man page (2h)
- [ ] Publish to PyPI and document `pipx install lap-bell`, with a CI workflow (1.5h)
