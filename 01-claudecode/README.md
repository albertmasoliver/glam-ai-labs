# 01 · Claude Code — working with an agentic coding tool

A one-day lab set: **twelve hands-on labs** with a `check.py` verifier over the
artifacts they produce, plus a printable **study guide**.

- **Study guide (read / print):** [`study-guide.pdf`](study-guide.pdf) — the ideas,
  in order, with the argument for each one.
- **Runnable workbook:** [`cc-exercises/`](cc-exercises/) — one folder per lab, each
  with a brief and a starting state; see its [README](cc-exercises/README.md) to set
  up and run.

Covers: what an agentic tool is good and bad at, writing a request that gets what you
asked for, driving a session (context, modes, plans), letting tests force a design,
project memory and scoped rules, permissions and the trust boundary, skills and hooks,
subagents, landing in code you did not write, spec-to-pull-request, review and
recovery, and where to stop.

## What you need

Claude Code installed and working, Python 3.9+, and `git`. The fixtures are standard
library only apart from `pytest` and one Flask app.

## Rebuilding the material

```bash
python tools/build.py      # study-guide.md -> study-guide.pdf  (needs: markdown weasyprint pygments)
```

## On sources

This lab set is original material. It is informed by Ken Kousen's *Claude Code: Up
and Running* (O'Reilly), and **none of its text or prompts is reproduced here** —
where a move comes from the book, the brief describes what the prompt has to do and
cites the chapter, and you write your own. The fixtures, the verifier, the prompts
that are quoted in full, and the study guide are this repo's.

A reader who owns the book gets more out of the labs. That is the honest trade, and
it is worth saying rather than pretending the set is complete on its own.
