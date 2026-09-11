#!/usr/bin/env python3
"""Practise memorizing a text one line at a time.

Run it:  python3 trainer.py
Press Enter for the next line, Ctrl-C to stop.

Remembers where you were between runs.
"""

import json
import os

LINES = [
    "Shall I compare thee to a summer's day?",
    "Thou art more lovely and more temperate:",
    "Rough winds do shake the darling buds of May,",
    "And summer's lease hath all too short a date;",
    "Sometime too hot the eye of heaven shines,",
    "And often is his gold complexion dimm'd;",
    "And every fair from fair sometime declines,",
    "By chance or nature's changing course untrimm'd;",
    "But thy eternal summer shall not fade,",
    "Nor lose possession of that fair thou ow'st;",
    "Nor shall Death brag thou wander'st in his shade,",
    "When in eternal lines to time thou grow'st:",
    "So long as men can breathe or eyes can see,",
    "So long lives this, and this gives life to thee.",
]


STATE_FILE = os.path.expanduser("~/.lyrics-trainer.json")


def main():
    current = 0
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                stored = json.load(f).get("line_index")
            if isinstance(stored, int) and not isinstance(stored, bool) \
                    and 0 <= stored < len(LINES):
                current = stored
        except (json.JSONDecodeError, OSError, AttributeError):
            current = 0

    while True:
        print()
        print(f"Line {current + 1} of {len(LINES)}")
        print(LINES[current])
        try:
            input("  [Enter] next  ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        current = (current + 1) % len(LINES)
        with open(STATE_FILE, "w") as f:
            json.dump({"line_index": current}, f)


if __name__ == "__main__":
    main()
