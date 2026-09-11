---
name: coverage-gaps
description: Report which lines and branches of this project the test suite never executes, ranked by risk. Use when the user asks what is untested, where the coverage holes are, whether a change is covered, or whether the suite is good enough to open a pull request.
argument-hint: "[path, optional]"
allowed-tools:
  - Bash(python3 -m coverage *)
  - Read
  - Glob
---

Report this project's coverage gaps. Do not infer coverage by reading the source:
run the suite and read the numbers.

1. Run `python3 -m coverage run --branch -m pytest -q`, then
   `python3 -m coverage json -o .coverage.json`. If $ARGUMENTS names a path, pass
   `--source=$ARGUMENTS` to the first command.
2. Read `.coverage.json`. For each file use `missing_lines` and `missing_branches`,
   and `totals.percent_covered_display` for the headline number.
3. Rank the gaps by what a bug there would cost, not by how many lines are missing.
   A missing branch in a fallback path outranks an uncovered `__repr__`.
4. Report: the headline percentage, then at most five gaps, each as
   `file:line` with one sentence on what is untested and why it matters.
5. Name the single test you would write first.

Do not write tests. Do not edit files. Report only.
