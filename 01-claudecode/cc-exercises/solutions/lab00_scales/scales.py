#!/usr/bin/env python3
"""Measure a project, so you can place it on the three scales.

    python3 scales.py fixtures/alpha
    python3 scales.py fixtures/beta

Every number below is a size number. That is the point of the exercise, and
also its limitation -- the line this tool is supposed to help you draw is not
a size line, and nothing here can see it.

Run it:  python3 scales.py <directory>
"""

import subprocess
import sys
from pathlib import Path

SKIP = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"}


def python_files(root):
    for path in sorted(root.rglob("*.py")):
        if not any(part in SKIP for part in path.parts):
            yield path


def lines_of_code(paths):
    """Non-blank, non-comment lines. Rough on purpose -- it is a size proxy."""
    total = 0
    for path in paths:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                total += 1
    return total


def people_in_history(root):
    """How many different people have written into this project.

    The reference answer. It is not a size metric: a one-file script that four
    people maintain is a cabin, and a thirty-file project one person will
    delete next month is not. What moves a project up the scales is other
    people working inside it, and the history is where that is recorded.
    """
    result = subprocess.run(
        ["git", "-C", str(root), "log", "--format=%ae"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return 0
    return len({line.strip() for line in result.stdout.splitlines() if line.strip()})


def measure(root):
    files = list(python_files(root))
    tests = [p for p in files if "test" in p.name]
    return {
        "python files": len(files),
        "lines of code": lines_of_code(files),
        "test files": len(tests),
        "test functions": sum(
            path.read_text(encoding="utf-8", errors="replace").count("def test_")
            for path in tests
        ),
        "directories": len({p.parent for p in files}),
        "people in history": people_in_history(root),
    }


def report(root):
    numbers = measure(root)
    width = max(len(name) for name in numbers)
    print(f"\n  {root}\n")
    for name, value in numbers.items():
        print(f"    {name.ljust(width)}  {value}")
    print()


def main(argv):
    if len(argv) < 2:
        print("usage: scales.py <directory>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    if not root.is_dir():
        print(f"{root} is not a directory", file=sys.stderr)
        return 2
    report(root)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
