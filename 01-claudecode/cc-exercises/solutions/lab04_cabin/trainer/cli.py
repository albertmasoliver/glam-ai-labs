"""Glue. Prints, reads input, and owns the real storage.

Holds none of the rules. If a manual run misbehaves, the bug is here; if a test
fails, it is in navigation or storage.
"""

import os

from .lines import LINES
from .navigation import LineTrainer
from .storage import JsonFileStorage, load_saved_index, save_index

STATE_PATH = os.path.expanduser("~/.lyrics-trainer.json")


def main():
    storage = JsonFileStorage(STATE_PATH)
    trainer = LineTrainer(LINES, load_saved_index(storage, len(LINES)))

    while True:
        print()
        print(f"Line {trainer.current_index + 1} of {len(LINES)}")
        print(trainer.current_line)
        try:
            input("  [Enter] next  ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        trainer.next()
        save_index(storage, trainer.current_index)


if __name__ == "__main__":
    main()
