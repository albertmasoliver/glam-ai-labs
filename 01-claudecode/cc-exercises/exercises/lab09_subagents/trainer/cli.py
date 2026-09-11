"""Glue. Prints, reads input, and owns the real storage.

Holds none of the rules. If a manual run misbehaves, the bug is here; if a test
fails, it is in navigation or storage.
"""

import os

from .lines import LINES
from .navigation import LineTrainer
from .storage import JsonFileStorage, load_saved_index
from .streak import advance, describe

STATE_PATH = os.path.expanduser("~/.lyrics-trainer.json")


def main():
    storage = JsonFileStorage(STATE_PATH)
    trainer = LineTrainer(LINES, load_saved_index(storage, len(LINES)))
    state = storage.read() or {}

    while True:
        print()
        print(f"Line {trainer.current_index + 1} of {len(LINES)}  ({describe(state.get('streak', 0))})")
        print(trainer.current_line)
        try:
            input("  [Enter] next  ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        trainer.next()
        state = advance({**state, "line_index": trainer.current_index})
        storage.write(state)


if __name__ == "__main__":
    main()
