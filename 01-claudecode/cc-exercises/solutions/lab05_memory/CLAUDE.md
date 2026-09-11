# Lyrics Trainer

## What this is

Small command-line app for practising a public-domain text one line at a time.
Dependency-free, with behaviour in testable modules.

## Architecture

- `trainer/navigation.py` holds the line-navigation rules. No I/O.
- `trainer/storage.py` holds persistence. `storage` is injected.
- `trainer/cli.py` is glue only: printing, input, and the real file storage.
- Tests live under `tests/` and run with pytest.

## Commands

- `python3 -m pytest` -- run the tests.
- `python3 -m trainer.cli` -- run the app.

## Conventions

- Standard library only. Do not add a runtime dependency.
- Pass storage in as a parameter; only `cli.py` may construct a `JsonFileStorage`.
- Keep `cli.py` free of rules -- if it grows a conditional, the rule belongs in a module.
- Use public-domain text in examples.

## Workflow

- For nontrivial changes, propose a plan before editing.
- After a feature lands, run the tests and then review the whole app for issues
  the change introduced or revealed.
