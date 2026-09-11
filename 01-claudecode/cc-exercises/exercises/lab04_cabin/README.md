# Lab 04 — tests force the design

`trainer.py` now persists, and it is still one file. Everything in it that could
be wrong is tangled with `print`, `input` and `open`, which means none of it can
be tested without a terminal and a home directory.

Ask for tests. **Do not ask for a refactor.** The refactor is what you are
watching for.

## What to do

```text
Please add automated tests for this app. I want at least tests for advancing to
the next line, wrapping at the end, resuming from the saved position, and falling
back to line 0 when the saved position is invalid.

Keep the behavior unchanged. Keep the app dependency-free apart from a test runner.
Before editing, show me the tests you plan to add. If the current structure makes
those tests awkward, explain the issue and propose the smallest change needed.
```

The last sentence is the lab. You have not asked for modules; you have made the
structural problem *reportable*. A single-file app whose persistence calls `open`
directly cannot be tested without writing to disk — so it should come back and
tell you so, and propose the seam.

> Kousen's ch. 4 makes this argument in JavaScript, and the prompt he uses is
> his. This is the course's Python port of the same six requirements.

**Take the seam, not the mocking.** If it offers to monkeypatch `open` or patch
the home directory, that is the wrong half of the fork: it keeps the tangle and
adds machinery to work around it. What you want is storage passed in as a
parameter, so a test hands it a fake object with `read()` and `write()` and
never touches a disk.

## The contract the checker verifies

So the seam is machine-checkable, this lab fixes two names:

- `trainer/storage.py` exposes `load_saved_index(storage, line_count)` returning
  a usable index, and `0` for missing, malformed or out-of-range state — including
  when `storage.read()` raises.
- `trainer/storage.py` exposes `save_index(storage, index)`, which writes through
  the injected object.

Everything else — how many modules, what they are called — is yours.

## Done when

`python check.py lab04` passes: the package imports, the tests pass **without
writing anything to `$HOME`**, and `load_saved_index` works when handed a fake.

The test run touching no files is the real result. If it still writes to your home
directory during tests, the seam is decorative.
