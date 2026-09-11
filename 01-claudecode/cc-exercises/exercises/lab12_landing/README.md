# Lab 12 — landing in a codebase you did not write

`legacy-service` is an invoicing service: five years of history, fifteen modules, two adapters,
an HTTP surface and four tests. Standard library only, so it runs anywhere.

**You are not supposed to understand it yet. That is the exercise.**

## Setting it up

The history is part of the lab, and a repository cannot hold another repository's `.git`, so
you replay it once:

```bash
bash make-history.sh          # six commits, 2019-2024
python3 -m pytest             # 4 tests, all passing
python3 scripts/serve.py      # http://127.0.0.1:8099
```

```bash
curl -s localhost:8099/invoices/preview -d '{
  "issuer":   {"code":"ACME","name":"Acme Iberia SL","vat_number":"ESB00000000"},
  "customer": {"code":"C1","name":"Cliente Uno"},
  "lines":    [{"description":"widget","quantity":2,"unit_price_cents":1000}]
}'
```

## Why this lab exists

Every other lab in this set happens in an app you built four minutes earlier, where you already
know where everything is. That is not the job. The job is landing in code nobody has explained
to you — and it is the most common thing you will do with an agentic tool in your first month.

This fixture is deliberately sized so no one can hold it in their head, and small enough to read
in an afternoon if you had to.

## What to do

**1. Ask for an orientation, read-only.** Write the prompt yourself. It needs four things, and
the fourth is the one people leave out:

- what the repository does,
- **where execution starts** — the single most useful fact in an unfamiliar codebase, and the one
  a README most often gets wrong. In this fixture it is not where the file names suggest;
- which files to read first, so you get a *reading order* rather than a summary you cannot check;
- **where it is guessing versus where the code is explicit.** In your own project you would
  notice a confident wrong answer. Here you have no such reflex, so make it mark the seam.

And tell it not to change anything, which makes the whole exercise free.

> Kousen's *Claude Code: Up and Running* (ch. 4, *When You Inherit the Project*) gives the
> read-only orientation prompt he uses. Ours is not reproduced here; write your own from the
> four requirements above and compare.

**2. Mine the history.** The code tells you what; the commits tell you why.

```text
Look through the git history for <module> and summarise how its API came to be.
What decisions does the history explain that the code does not?
```

Scoped to one module, because "summarise the history" of a five-year repo is a request for a
shrug. Asking *how its API came to be* gets you a sequence rather than a summary. And *what the
history explains that the code does not* is the whole point — you are mining for intent that
never made it into a comment, and subtracting what you could have read yourself.

**3. Spot-check the map against the territory.** If it says the request flow runs one way, open
one file and follow it. If it calls something dead code, `grep` for the symbol before you believe
it.

**4. Write down only what you verified**, as a `CLAUDE.md` — deleting the parts that are merely
plausible. Chapter 4 of the book has a prompt for turning a trusted map into project memory;
the point holds without it. Orientation is expensive, and paying for it twice is waste.

## Fair warning

There are things in here that are wrong, things that look wrong and are deliberate, and at least
one module whose name does not describe what it holds. Some of that is in comments; some of it
exists only in `git log`. A confident answer is not a correct one, and finding out which is which
is the exercise.

## Done when

`ORIENTATION.md` in this folder says, in your own words, what the service does, **where execution
actually starts** (with the file and function), and one thing the orientation got wrong or
guessed at that you caught by opening the code.
