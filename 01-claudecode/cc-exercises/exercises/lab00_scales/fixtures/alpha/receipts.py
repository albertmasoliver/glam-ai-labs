#!/usr/bin/env python3
"""Totals the receipts I photograph and dump into a folder, once a quarter.

Written in an afternoon and used four times a year by one person. It reads
whatever CSVs are in the directory, adds them up per category, and prints a
table. If the format changes I will fix it then.

Run it:  python3 receipts.py ~/receipts/2026-Q1
"""

import csv
import sys
from collections import defaultdict


def read_rows(directory):
    rows = []
    for path in sorted(directory.glob("*.csv")):
        with path.open(newline="") as fh:
            for row in csv.DictReader(fh):
                rows.append(row)
    return rows


def totals_by_category(rows):
    out = defaultdict(float)
    for row in rows:
        category = (row.get("category") or "uncategorised").strip().lower()
        try:
            out[category] += float(row.get("amount") or 0)
        except ValueError:
            continue
    return dict(out)


def format_table(totals):
    if not totals:
        return "nothing to total"
    width = max(len(k) for k in totals)
    lines = []
    for name in sorted(totals, key=totals.get, reverse=True):
        lines.append(f"{name.ljust(width)}  {totals[name]:9.2f}")
    lines.append("-" * (width + 11))
    lines.append(f"{'total'.ljust(width)}  {sum(totals.values()):9.2f}")
    return "\n".join(lines)


def main(argv):
    from pathlib import Path

    if len(argv) < 2:
        print("usage: receipts.py <directory>", file=sys.stderr)
        return 2
    print(format_table(totals_by_category(read_rows(Path(argv[1])))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
