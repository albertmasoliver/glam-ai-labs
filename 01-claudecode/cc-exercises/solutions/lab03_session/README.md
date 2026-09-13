# Lab 03 — the window, measured

A directory of three files in `sample/`, and a tool that guesses what they cost.
Twenty-five minutes: the four /context readings are what costs, not the writing. You will end up with two numbers you measured yourself and one
failure mode you caused on purpose.

```bash
python3 window.py sample
```

One of those three files is twenty times the size of the other two put together, and
forty times the size of the module you actually care about. Nothing in it is
interesting. That is the shape of the problem.

## The thing to internalise first

Every request is stateless. The model does not remember the last turn — Claude Code
rebuilds the whole conversation and sends it again, every time. The window is not a
container that fills up once; it is a budget you re-spend on every message.

Which means there are **two** ways it goes wrong, and only one of them is obvious:

| | What it looks like |
|---|---|
| **Window full** | You run out of space. It tells you. It compacts. |
| **Context polluted** | You have space left and the answers get worse anyway, because most of what you are re-sending is not about the question. |

The first is loud. The second is the one that costs you an afternoon.

## What to do

**1. Read the baseline before you spend anything.** Start a session in this folder
and run `/context`. Write the token count into `WINDOW.md` under *baseline*. Do this
first — once you have asked anything at all, the baseline is gone.

**2. Predict, then find out.** `python3 window.py sample` prints an estimate for the
whole directory. Write that number down as *estimate* **before** the next step, while
it can still be wrong.

**3. Spend it.** Ask Claude Code to read all three files in `sample/` and summarise
what the module does. Run `/context` again, write it down as *after*, and work out
the two numbers that matter: what it actually cost, and by how much the estimate
missed. Four characters to a token is a heuristic; this is you finding out its error
bar on your own files.

**4. Pollute it on purpose.** Stay in the same session. Ask three questions that have
nothing to do with this code — a shell incantation, a question about a different
language, anything. Then ask something precise about `geometry.py` that you already
know the answer to, like what `union_area` returns for two boxes that do not touch.

Run `/context` once more. **You will have space left.** Note whether the answer was
as good as it was in step 3. This is the failure mode with no error message.

**5. Clear, and ask it again.** `/clear`, then the same precise question. That is the
cheapest habit in the whole course, and you have just seen what it buys.

> Chapter 3 of Kousen's *Claude Code: Up and Running* covers session drift and the
> commands that manage it. His text is not reproduced here; the measurement and the
> deliberate pollution are this lab's.

## Done when

`python check.py lab03` passes: `WINDOW.md` carries a baseline, an estimate, an after
and the cost, the arithmetic between them agrees, the error against the estimate is
worked out, and you have written one sentence that says how a polluted window is
different from a full one.

## One honest caveat

`/context` counts things `window.py` cannot see — the system prompt, tool definitions,
your `CLAUDE.md`. Subtract the baseline and you are comparing the right things. If
your error comes out above about 40%, say so rather than rounding it into line: a
heuristic that is badly wrong for your files is a useful thing to have found out.
