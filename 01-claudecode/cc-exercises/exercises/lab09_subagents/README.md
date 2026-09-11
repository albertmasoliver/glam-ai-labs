# Lab 09 — subagents

The trainer package plus one commit's worth of new work: a streak counter.
`CHANGE.md` describes what was touched. Read it, then look at the diff.

A subagent is a **fresh context with a narrow job and a reporting contract**. The
fresh context is the point: a reviewer that has been watching you write the code
has already been convinced by your reasoning. One that has not, has not.

## What to do

**1. Review the change with a subagent** you write yourself, in
`.claude/agents/<name>.md`. Four things it needs:

- **frontmatter**: `name`, a `description` saying *when to delegate to it* (this
  is what gets matched against the situation, exactly as with a skill),
- **a tool list** — an unrestricted subagent is just another session. A reviewer
  gets read and search tools and nothing that writes. The narrowing is the point,
- **standards to review against**, not "review this code",
- **a reporting contract**: what comes back, in what shape. Without it you get
  whatever the subagent felt like summarising, and you cannot act on it.

**2. Ask for the review through its interface**, not by restating the job. If you
have to re-explain the task every time, the file is not earning its place.

**3. Judge the result.** There is a real gap in this change, and a good review
names it. There is also at least one thing that looks like a problem and is not.

**4. Then run two lenses at once** — for instance a test-coverage reviewer and a
naming/API reviewer over the same diff. They are read-only, so they cannot
collide. Note what the second one saw that the first did not.

The rule for parallel agents: **read-only lenses parallelise freely; writers need
disjoint ownership and a stop condition, or you get two agents editing the same
file and one of them losing.**

> Kousen's ch. 8 has a full subagent file, the invocation that goes with it, and a
> worked anti-example of parallel agents that collide. All of them are his. Yours
> has to be written from the four requirements above.

## Done when

`python check.py lab09` passes: a file under `.claude/agents/` whose frontmatter
parses, with a description, an explicit tool list, and a body that states what
comes back.

And you can say what the review missed. Two lenses is not two opinions; it is two
coverage areas, and neither covers everything.
