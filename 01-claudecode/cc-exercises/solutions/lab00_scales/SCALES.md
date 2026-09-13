# The two fixtures, placed

A reference answer, not the only one. What makes it an answer is that every claim
below names the file or command it came from.

## fixtures/alpha

**Scale:** doghouse

**Because:** if I changed what it prints tomorrow, the only person who would notice
is the person who wrote it, and they would notice next quarter.

## fixtures/beta

**Scale:** cabin

**Because:** its output is an identifier two other services store, so changing what
`slugify` returns is a data migration in systems I do not own.

## Three things scales.py cannot see

1. **Three people in the history.** `git -C fixtures/beta log --format='%an'` returns
   Rita, Dan and Priya; alpha returns one name and one commit. Shared code is the
   cabin line.
2. **A breaking change that had to be scheduled.** The 2024-11-04 commit body says
   the content-api backfill and the search-index reindex were coordinated around it.
   That is a rewrite gate: the change was not the hard part, the agreement was.
3. **A pipeline someone else reads.** `.github/workflows/ci.yml` runs the suite on
   every pull request, so a red test is now a message to a reviewer rather than a
   note to self.

`notes/consumers.md` and `CHANGELOG.md` say the same thing as (1) and (2) in other
words, which is why they are not listed as a fourth and fifth.

## The one I taught it

**Metric added:** `people in history`

**What it means:** one means whatever you do to this project, you do alone and can
undo alone. More than one means a change is a negotiation, and that is the cabin
line whatever the line count says.

**alpha:** 1   **beta:** 3
