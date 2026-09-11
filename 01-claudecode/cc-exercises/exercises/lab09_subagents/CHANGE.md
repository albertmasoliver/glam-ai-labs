# The change under review

One commit's worth of work: a streak counter, so the app can tell you how many
lines in a row you have advanced through.

Touched:

- `trainer/streak.py` -- new. The streak rules, including a 12-hour timeout.
- `trainer/cli.py` -- reads the whole state object now, not just the index, and
  writes the streak back on every advance.

Tests were not touched.
