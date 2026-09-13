---
name: library
description: >
  Answer questions about the books on our local shelves -- what a given author
  has here, and how many books sit on each shelf. Use it whenever someone asks
  what we have by someone, which shelf something is on, or for a breakdown of
  the collection.
allowed-tools:
  - Bash
---

# Local library

The shelf data lives in `library.db` and `library_cli.py` is the only thing that
should read it.

1. For "what do we have by X", run `python3 library_cli.py author X`.
2. For totals or a breakdown, run `python3 library_cli.py shelves`.
3. Answer from the output and nothing else. If the tool returns no rows, say the
   author is not on these shelves -- do not fill the gap from what you know about
   their bibliography, because the question was about this collection.
