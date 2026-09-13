# Lab 07 — skills and hooks

The trainer package, with no `.claude/` directory. Thirty minutes: about fifteen for
the skill and the formatter hook, about fifteen for the two experiments that follow
them.

A **skill** is a procedure the agent reaches for when the situation matches. A
**hook** is code that runs whether or not anyone reached for anything. That is the
whole distinction, and it decides which one you should be writing.

## Part 1 — a skill

Write `.claude/skills/coverage-gaps/SKILL.md`: a procedure for reporting which
lines and branches the suite never executes, ranked by risk.

**The description is the entire interface.** Only frontmatter is loaded at
startup; the body is read after the skill is chosen. So the description has to
carry both *what it does* and *when to use it*, in the words someone would
actually use — "what is untested", "are the coverage holes", "good enough to open
a pull request".

Two failure modes, both common:

- A description that says only what it does. It will never fire, because nothing
  in it matches how anyone phrases the question.
- **An unquoted colon.** `description: Reports coverage: gaps and risks` is a
  nested mapping in YAML, and your description silently truncates at `Reports
  coverage`. Quote it.

Test it without naming it:

```text
Is the trainer package well enough tested to open a pull request?
```

If the skill does not fire on that, the description is the bug, not the body.

> Kousen's ch. 6 demonstrates a skill that wraps a local CLI; that example is his.

## Part 2 — a hook

```text
Write a PostToolUse hook for this project that runs `ruff format` and
`ruff check --fix` on any .py file after an Edit or Write. Put the script
in .claude/hooks/ and the configuration in .claude/settings.json.

The script must exit 0 if ruff is not installed, and must not touch
non-Python files. Show me both files before writing them, and tell me
whether this hook can block an edit.
```

Three things are deliberate. **Exit 0 without ruff**, because a hook that fails on
a machine without the tool turns every edit into an error for someone who never
asked for the check. **Show me both files first**, because a hook runs on every
matching tool call and you are about to install it into your own loop. And the
last question is a fact check with a real answer: `PostToolUse` fires after the
edit has already happened and cannot block it. If you want to stop an edit, you
need `PreToolUse` and exit code 2.

## Part 3 — the description is dispatch logic

Claude does not guess which skill applies. It scores the descriptions it loaded at
startup against the words you typed and runs the best match. **That makes the
description a routing table, and a routing table nobody has tested is a routing
table that does not work.** Part 1 told you to test yours by not naming the skill.
This part tests it the other way round: break the description on purpose and watch
the routing go away. You are about to watch the scoring happen, so take the
direction from your own three runs rather than from a number anyone quotes you.

Fill in `ROUTING.md`. Three states, one question, and the question never names the
skill. Write the question into the file verbatim before you start: the three states
only compare if it was the same sentence every time, and the check reads it.

**1. Invoke it by name.** `/coverage-gaps`, or "use the coverage-gaps skill". This
separates two failures that look identical from the outside — a skill that cannot
run, and a skill that runs fine but never gets chosen. Everything after this step
is about the second one.

**2. Replace the description with `helps with code`, then ask the question again.**
Start a new session first: descriptions are read at startup, so an edit you make
mid-session changes nothing you can observe, and you will conclude the wrong thing.
This is the state worth writing down, because it is the one that shows the body was
never the problem.

**3. Rewrite the description in the words someone would say out loud, and ask
again.** Not the words you would put in a commit message — the ones in the question
you actually typed. Paste what you ended up with into `ROUTING.md`. The check
compares it against the description that is live in `SKILL.md`, because a record of
a state you have since edited away is not a record.

## Done when

`python check.py lab07` passes: the `SKILL.md` frontmatter parses and its description
survives YAML intact and names its trigger, the formatter hook exits 0 when `ruff` is
off the PATH, and `ROUTING.md` records the same question asked of three states of one
description, with the winning description pasted in full.

## One honest caveat

You are running the routing three times, not three hundred, and selection is not
deterministic. A description can fire once and miss on the same sentence a minute
later, so three states give you the direction of the effect and not a number you
can quote. The checker does not grade the middle result for that reason: if the
generic description fires anyway, write that down — it is an observation about a
probabilistic system, and the two usual explanations are printed back at you. What
is graded is that the rewrite routes on a question that never names the skill.

The rest is a grep and a set of hook events, not a judge. It can tell you the gate
exited 2 on annotated source; it cannot tell you the reason you put on stderr was
worth reading.
