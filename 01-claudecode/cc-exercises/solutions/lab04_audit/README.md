# Lab 04 — auditing the evidence

Somebody asked an agent to fix a bug. It did. Here is the repository afterwards:

```bash
bash make-history.sh      # replay the two commits -- the history is the evidence
python3 -m pytest         # 5 passed
git log --oneline
git diff HEAD~1
```

The suite is green. The commit message is honest. The diff is three lines.

**Nothing here is for you to fix yet.** Your job is to decide whether the evidence
actually supports the claim that the problem was solved correctly — and it does not.
There are at least three things wrong. Find them before you change anything.

> **The agent operates the tools. You audit the evidence.**

## The chain you are auditing

```text
failure observed → root cause → minimal change → evidence → invariants → challenge
```

A green suite sits at one link of that chain. It is not the chain.

## How to run the audit

Work through it in order, and **do not let it edit anything** until step 5.

**1. Failure observed.** Ask it to show you the failing test *before* the fix —
`git stash` is not needed, the history is right there. If the original test does not
fail on the pre-fix code, you have no red → green relationship and the green means
nothing. Check that first.

**2. Root cause.** Ask for the exact code path, not a summary. *Which input reaches
which line, and why does it get through?* A diagnosis you cannot trace in the file is
a guess wearing a lab coat.

**3. The change.** Ask whether it is the smallest correct change, what **other** inputs
the new condition affects, and whether a validator already exists that should have been
reused. This app has a validator convention; look at `shortener/validation.py` and ask
why the fix did not follow it.

**4. What else changed.** Read the whole diff, not the summary of it. For every changed
file: was it in scope? Production, tests, and anything else — separately.

**5. Confirm.** Now ask it to audit its own change and, for every claim, **show the
supporting evidence**. Claims without evidence are what you are here to catch.

**6. Challenge.** Ask it to argue that the fix is wrong. What assumptions did it make
about the input? What does the suite not cover?

## What to produce

- `AUDIT.md` — at least three findings, each with **claim, evidence, why it matters**.
  Evidence means a `file:line`, a command and its output, or a commit. Not a feeling.
- Then fix what the audit found, including the evidence chain itself.

## Done when

`python check.py lab04` reports:

1. `AUDIT.md` has three or more findings and each one cites evidence that exists.
2. **The verifier is a verifier again.** One assertion in the suite was widened so that
   it passes whether the bug is present or not. Behaviour happens to be correct today,
   which is exactly why this is easy to miss and exactly why it matters: the test will
   not catch the next regression either.
3. **The fix survives an input nobody tested.** There is one.
4. **The unrelated file is back.** The commit "tidied up" something it was not asked to
   touch, and the tidy-up changed behaviour no test covers. Read its docstring, then
   read what it does.

## A note on how this lab is different

Every other lab here asks you to produce something. This one asks you to **disbelieve
something**, on evidence, before you touch it. That is the harder skill and the one that
does not come back as a green checkmark.
