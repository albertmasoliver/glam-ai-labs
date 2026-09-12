# Lab 02 — the five jobs

A small notes app. Three handlers' worth of code, one validator, and a failing test:

```bash
python3 -m pytest
```

```
FAILED tests/test_web.py::test_create_rejects_empty_title - assert 200 == 400
```

An empty title is accepted and returns 200. It should return 400.

**Fixing this is not the exercise.** Any prompt will fix this. The exercise is what
else your prompt does — or fails to do — while fixing it.

## What to do

Write your prompt in `PROMPT.md` first, then send it. One prompt, not a conversation.

A prompt is a message to a colleague who is about to do the work: enough context to
decide well, a clear picture of what success looks like, the constraints they have to
respect. That framing also tells you what to leave out — you would not tell a colleague
which variable names to use.

Five jobs, and a good prompt does all five in about six lines:

| Job | What it means here |
|---|---|
| **The symptom**, in checkable terms | Not "validation is broken". A status code you can assert on. |
| **The desired behaviour**, as its own sentence | A separate claim from the symptom. Both are needed; they are not the same sentence. |
| **The likely location** | A real path in this repo. Saves a search, and a search costs tokens and time. |
| **The local convention**, by pointing at it | This app already has a validator pattern. Point at the file rather than describing it — cheaper and more exact. |
| **The boundary** | One line. The difference between a reviewable diff and a surprising one. |

> Kousen's *Claude Code: Up and Running* (ch. 3) runs this as a before/after pair — a
> two-word request against a six-line one. Both are his and neither is reproduced here.
> Write yours from the five jobs above.

## The sentence this lab is actually about

The same constraint, three ways:

```text
Don't put validation in the handler
Put validation in a validator function
Put validation in a validator function so every path that accepts user
input is checked the same way
```

The first can be obeyed while completely missing the point. The second names a target.
The third is the one to write, because **the agent generalises from the reason** — it
makes consistent choices in places your prompt never mentioned.

A reason is a rule that transfers. An instruction is a rule that does not.

This lab measures that difference instead of asserting it.

## What may change, and what may not

| | |
|---|---|
| **Yours to edit** | `notes/web.py`, `notes/store.py`, `notes/validation.py` |
| **Frozen** | `notes/formatting.py`, `notes/legacy_export.py`, `tests/test_web.py` |

`legacy_export.py` is genuinely ugly and carries a `TODO`. Nothing asked you to fix it.
`test_web.py` is frozen for a different reason: a red test goes green two ways, and only
one of them is a fix.

## Done when

`python check.py lab02` reports four things:

1. `PROMPT.md` carries the five jobs. **This is a grep, not a judge** — it checks that you
   wrote the pieces, not that you wrote them well. The other three do that.
2. The failing test passes.
3. **Transfer.** `update_note` has the same defect and nothing points at it. Did your fix
   reach it?
4. **The fence held.** The three frozen files still match `.baseline.json`.

Checks 3 and 4 live in `check.py`, and you can read it. Reading it is not the exercise.

## One honest caveat

Check 3 is not deterministic. A weak prompt can reach `update_note` by luck, and a good one
can miss it on a bad day. Run it twice before you conclude anything.
