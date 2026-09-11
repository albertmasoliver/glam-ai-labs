"""Persistence rules.

`storage` is injected. The real app passes a JsonFileStorage; tests pass a fake.
This separates *what persistence means* from *where the state actually lives*.
"""

import json

from .navigation import normalize_index

KEY = "line_index"


def load_saved_index(storage, line_count):
    """Read the saved index, falling back to 0 for missing or invalid state."""
    try:
        state = storage.read()
    except Exception:
        return 0
    if not isinstance(state, dict):
        return 0
    return normalize_index(state.get(KEY), line_count)


def save_index(storage, index):
    storage.write({KEY: index})


class JsonFileStorage:
    """The real one. The only part of persistence that knows about the disk."""

    def __init__(self, path):
        self.path = path

    def read(self):
        try:
            with open(self.path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    def write(self, state):
        with open(self.path, "w") as f:
            json.dump(state, f)
