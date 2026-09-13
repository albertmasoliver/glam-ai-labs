#!/usr/bin/env python3
"""Estimate what a file costs to put in the context window.

    python3 window.py sample
    python3 window.py sample --window 200000

Four characters to a token is a rough heuristic and it is wrong in both
directions -- prose runs cheaper, dense code with long identifiers runs dearer.
It is close enough to plan with, which is the only claim this makes. The point
of the lab is to find out how wrong it is for your files, by comparing it with
what /context reports.

Run it:  python3 window.py <directory>
"""

import sys
from pathlib import Path

CHARS_PER_TOKEN = 4
DEFAULT_WINDOW = 200_000
SKIP = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"}


def estimate(path):
    return len(path.read_text(encoding="utf-8", errors="replace")) // CHARS_PER_TOKEN


def readable_files(root):
    for path in sorted(root.rglob("*")):
        if path.is_file() and not any(part in SKIP for part in path.parts):
            yield path


def table(root, window=DEFAULT_WINDOW):
    rows, running = [], 0
    measured = sorted(
        ((p, estimate(p)) for p in readable_files(root)),
        key=lambda pair: pair[1], reverse=True,
    )
    for path, tokens in measured:
        running += tokens
        rows.append((path.relative_to(root), tokens, running, running / window))
    return rows


def report(root, window=DEFAULT_WINDOW):
    rows = table(root, window)
    if not rows:
        print(f"  nothing readable under {root}")
        return
    width = max(len(str(r[0])) for r in rows)
    print(f"\n  {root}  --  against a {window:,}-token window\n")
    print(f"    {'file'.ljust(width)}  {'tokens':>8}  {'running':>8}  {'% window':>8}")
    print(f"    {'-' * width}  {'-' * 8}  {'-' * 8}  {'-' * 8}")
    for name, tokens, running, share in rows:
        print(f"    {str(name).ljust(width)}  {tokens:8,}  {running:8,}  {share:7.1%}")
    print(f"\n    everything here: {rows[-1][2]:,} tokens, "
          f"{rows[-1][3]:.1%} of the window\n")


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    window = DEFAULT_WINDOW
    if "--window" in argv:
        window = int(argv[argv.index("--window") + 1])
    if not args:
        print("usage: window.py <directory> [--window N]", file=sys.stderr)
        return 2
    root = Path(args[0])
    if not root.is_dir():
        print(f"{root} is not a directory", file=sys.stderr)
        return 2
    report(root, window)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
