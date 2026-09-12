# Lab 05 — project memory

A small trainer app with a tested core, and no `CLAUDE.md`. Every session starts by rediscovering
that storage is injected, that there are no dependencies, that `cli.py` holds no
rules — and half the time it rediscovers it wrong.

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

> Kousen's ch. 4 has the prompt he uses to generate a first draft, and ch. 5
> closes out the same app by asking what it is missing. Both are his; write yours.

## Done when

`python check.py lab05` passes: `CLAUDE.md` is under 100 lines, has five sections
covering architecture, commands, conventions and workflow, and one file under
`.claude/rules/` has parsing frontmatter with a `paths:` key and a rule beneath it.
