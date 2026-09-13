# Lab 05 — project memory

A small trainer app with a tested core, and no `CLAUDE.md`. Every session starts by rediscovering
that storage is injected, that there are no dependencies, that `cli.py` holds no
rules — and half the time it rediscovers it wrong.

Two halves. Writing the file is the first and takes about about twenty-five minutes, because three fresh sessions cannot be hurried. The second
is fifteen, and it is the one that changes your mind: you put three instructions in
three different homes and then measure whether each one actually holds.

## What to do

**1. Write it yourself first, then ask for a review.** `/init` will generate a
description of the code, which is the part the agent can already see by reading
the code. The value is in the constraints only you know: *standard library only*,
*only `cli.py` may construct real storage*, *if `cli.py` grows a conditional, the
rule belongs in a module*.

So: draft it by hand, then ask what is missing or what a new contributor would
get wrong. Then cut it back.

**2. Keep it short.** This file is prepended to every session in this project.
A 300-line `CLAUDE.md` is 300 lines of context you pay for on every request,
including the ones where none of it is relevant. Five sections, under a hundred
lines: what this is, architecture, commands, conventions, workflow.

**3. Then scope one rule.** Advice about tests is noise while you are editing
`storage.py`. Put it in `.claude/rules/testing.md` with frontmatter that scopes
it to the files it is about:

```markdown
---
paths:
  - "tests/**/*.py"
---

# Testing rules

- Tests must not touch the filesystem, stdout, or a real clock.
- ...
```

That is the difference between memory and a scoped rule: memory is always loaded,
a rule arrives when the matching file does.

**4. Now find the third instruction — the one you cannot afford to have ignored.**
There is one in this fixture. `trainer/lines.py` is a transcription of a
public-domain text, and nothing downstream would notice it being corrupted: every
navigation test compares `LINES` to itself, so a mangled sonnet passes the suite
green. Open `HOMES.md` and fill in the placement table — one instruction in
`CLAUDE.md`, one scoped to a path, and this one somewhere else entirely.

The rest of the lab is proving all three placements were right, which is not the
same as arguing for them. **Claude Code tries to do the right thing; it does not
make the wrong thing impossible.** You are about to watch the difference.

**5. Measure the advisory one.** Take a request that your `CLAUDE.md` has an
opinion about — "add a `--start N` option so practice resumes from a given line"
is a good one if you wrote the usual *propose a plan before editing*. Send it in a
fresh session, note whether the instruction was followed, `/clear`, and send the
**same words** again. Three times. Do not improve the prompt between runs; the
identical input is the only reason the results mean anything.

Record all three in `HOMES.md`. Two of three is the common outcome and it is not a
bug to be fixed — it is what "always loaded" buys you, which is influence.

**6. Watch the scoped one arrive and leave.** Run `/context` in a session where no
`tests/` file has come up, and look at what is listed under project memory. Then
ask something about `tests/test_storage.py` and run `/context` again. Write down
both readings and what made the rule appear. The tokens it does not cost you while
you are editing `navigation.py` are the entire argument for the `paths:` key.

**7. Make the third one refuse.** A `PreToolUse` hook is checked before the tool
runs and can stop it:

```text
Write a PreToolUse hook for this project that refuses any Edit or Write to
trainer/lines.py, and register it in .claude/settings.json. It must exit 2 on
that file and 0 on everything else, print the reason on stderr, and depend on
nothing that is not already installed. Show me both files before you write them.
```

Why that exit code and not another is lab 07's subject. Here you only need the
hook to refuse, and then to find out what the refusal was worth.

Then try it. Ask for a small change to `trainer/lines.py` — modernising `dimm'd`
is a plausible one — and afterwards open the file and look, rather than believing
the summary. Record the exit code and the outcome.

> Kousen's ch. 4 has the prompt he uses to generate a first draft, and ch. 5
> closes out the same app by asking what it is missing. Both are his; write yours.
> His ch. 6 builds a hook of its own, and that one is not reproduced here either.
> The three homes, the protocol for measuring them and every reading in `HOMES.md`
> are this lab's.

## Done when

`python check.py lab05` passes. It reads `CLAUDE.md` for length — under 100 lines,
since every session pays for it — and for five sections covering architecture,
commands, conventions and workflow; it parses the frontmatter of one file under
`.claude/rules/` and requires a `paths:` key with a rule beneath it.

Then it reads `HOMES.md` as evidence rather than as a form. Three distinct
instructions in three homes, each one traceable back to the file it claims to live
in. A compliance line whose arithmetic agrees with the session rows above it. Two
`/context` readings for the scoped rule that disagree with each other, and the file
that made the difference. And the hook, which it does not take on trust: it runs
your script with `CLAUDE_PROJECT_DIR` set and a real `PreToolUse` payload on stdin,
and wants exit 2 with a line on stderr for `trainer/lines.py`, exit 0 for five other
paths including one outside the project, the same answer both times it asks, and a
`PreToolUse` entry in `settings.json` whose command names a file that is really
there.

## One honest caveat

Three sessions is a sample of three. A 2 of 3 is not the model's compliance rate
and you should not quote it as one — it is an existence proof that the rate is not
1, which is the only thing the placement decision needs from it. If you get 3 of 3,
write that down and move on rather than re-running until it misbehaves. The point
was never to catch it out; it is that you now know which of your instructions are
guaranteed and which are merely likely, and you know it by measurement.

The checker is a grep, not a judge. It can tell that your compliance line agrees
with your table and that your hook refuses one path and leaves the rest alone. It
cannot tell whether the closing paragraph is a reading or a shape with the right
words in it, and a determined student can write the shape. That part is yours.
