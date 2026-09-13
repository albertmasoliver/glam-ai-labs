#!/usr/bin/env python3
"""Split a subagent's report into findings you have to answer one at a time.

    python3 triage.py report.txt        # writes TRIAGE.md
    python3 triage.py -                 # read the report on stdin
    python3 triage.py report.txt --force

Paste what came back into a file, run this, and you get one numbered block per
finding with a verdict and a reason waiting under it. That is the whole trick:
a report read as a wall of prose gets skimmed and agreed with, and the same
report read as nine separate claims gets argued with one claim at a time.

The split is deliberately dumb. A bullet, a numbered item or a level-three
heading at the left margin opens a new finding; anything indented or unmarked
underneath belongs to it. A dumb split you can see through beats a clever one
that quietly folds two claims into one line you then accept together.

NOTE(rm, 2024-11): this refuses to overwrite an existing TRIAGE.md. The
verdicts are the expensive part, and re-running the tool after a second report
used to eat them. Pass --force when you mean it.

Run it:  python3 triage.py report.txt
"""

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "TRIAGE.md"

# Left margin only. An indented bullet is a detail of the finding above it,
# not a new one, and treating it as new is how a triage turns into a chore.
OPENER = re.compile(r"^(?:[-*+]\s+|\d+[.)]\s+|#{3,6}\s+)(.*)")


def findings(text):
    """Group the report's lines into findings, in the order they were written."""
    out, current = [], None
    for line in text.splitlines():
        opened = OPENER.match(line)
        if opened:
            current = [opened.group(1).strip()]
            out.append(current)
        elif current is not None and line.strip():
            current.append(line.strip())
    return [block for block in ("\n".join(b).strip() for b in out) if block]


def quote(block):
    return "\n".join(("> " + line) if line else ">" for line in block.splitlines())


def render(items, source):
    """One block per finding. The placeholders are there to be conspicuous --
    a TRIAGE.md still carrying them is a report nobody checked."""
    out = [
        "# Triage of the subagent's report",
        "",
        f"{len(items)} findings, split out of {source}. Mark every one, and say why. "
        "A finding you",
        "did not triage is a finding you did not verify, and verification is the cost",
        "that delegating does not remove.",
        "",
    ]
    for number, block in enumerate(items, 1):
        out += [
            f"## Finding {number}",
            "",
            quote(block),
            "",
            "**Verdict:** <accept / reject>",
            "",
            "**Because:** <one line. For a reject, say what you checked and what you",
            "found there instead.>",
            "",
        ]
    return "\n".join(out).rstrip() + "\n"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", help="file holding the pasted report, or - for stdin")
    parser.add_argument("--out", default=str(OUT), help="where to write (default TRIAGE.md)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing TRIAGE.md")
    args = parser.parse_args(argv[1:])

    if args.report == "-":
        text, source = sys.stdin.read(), "the pasted report"
    else:
        path = Path(args.report)
        if not path.is_file():
            print(f"{path} is not a file", file=sys.stderr)
            return 2
        text, source = path.read_text(), f"`{path.name}`"

    items = findings(text)
    if not items:
        print("no findings in that report -- nothing in it starts with a bullet, a "
              "number or a ### heading at the left margin.\nPaste the list part, not "
              "the covering sentence.", file=sys.stderr)
        return 2

    target = Path(args.out)
    if target.exists() and not args.force:
        print(f"{target.name} already exists, and your verdicts are in it. "
              "--force to replace it.", file=sys.stderr)
        return 1

    target.write_text(render(items, source))
    print(f"{len(items)} findings -> {target}")
    print("Mark every one. At least one of them is wrong.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
