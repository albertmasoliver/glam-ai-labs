#!/usr/bin/env python3
"""Practise memorizing a text one line at a time.

Run it:  python3 trainer.py
Press Enter for the next line, Ctrl-C to stop.
"""

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


def main():
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


if __name__ == "__main__":
    main()
