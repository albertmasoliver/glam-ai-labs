# Lab 07 — skills and hooks

The trainer package, with no `.claude/` directory.

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

## Done when

`python check.py lab07` passes: the `SKILL.md` frontmatter parses, the description
survives YAML intact and names its trigger, and the hook exits 0 when run with
`ruff` off the PATH.
