# <title of the pull request>

Closes part of #39.

## What this is

<two or three lines. The slice, not the issue.>

## Boundary

**In scope:** <one line>

**Out of scope:** <the bullets you left, by name>

## Verification

<paste the output of `python3 pr_gate.py`>

## The plan I had to correct

**What it proposed:** <the step that traded something away>

**Which contract line it broke:** <name it>

**What I asked for instead:** <one line>

## Headless, with and without --bare

**Command:** <the claude -p command you ran>

**Difference:** <what loaded in the run without --bare that did not load with it.
If you cannot see a difference, say so -- that is a finding about this project, and
it stops being true the moment someone adds a hook.>
