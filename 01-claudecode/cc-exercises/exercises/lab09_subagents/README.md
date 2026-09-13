# Lab 09 — subagents

The trainer package plus one commit's worth of new work: a streak counter.
`CHANGE.md` describes what was touched. Read it, then look at the diff.

A subagent is a **fresh context with a narrow job and a reporting contract**. The
fresh context is the point: a reviewer that has been watching you write the code
has already been convinced by your reasoning. One that has not, has not.

Steps 1 to 4 are the file. Steps 5 to 7 are twelve minutes of finding out what the
file bought you, on real code, in numbers you take yourself — and that is the half
that changes what you delegate next week.

## Delegation as a context strategy

The window you care about is the main session's. Survey a codebase you have never
opened and it fills with search results, file contents, test output and two false
starts, when what you needed out of all that was a paragraph. Delegate the survey
and the same reading still happens, somewhere else; what comes back is the
paragraph.

**Delegate when the process is noisy and the result is small.** That is the rule,
and notice that it says nothing about difficulty. A hard question with a one-line
answer is a good delegation. An easy one you have to watch every step of is not.

What delegating does not do is save tokens. The subagent opens the same files, and
pays for a fresh system prompt and a fresh tool list on top, so the same task
delegated costs more in total than the same task done inline, and a team of
parallel agents costs more again. **You moved a cost out of your window. You did
not take it off the bill.** By how much, on your model and your machine, is what
steps 5 and 6 are for — the two readings you take there are the only figures in
this lab worth quoting, because they are the only ones you can show your working
for.

So there are three costs, and only the first one is obvious:

| | What it is |
|---|---|
| **Tokens** | Delegating spends more of them, not fewer. What improves is *where* they are spent. |
| **Coordination** | Someone has to write the brief. A thin brief comes back as a confident answer to a question you did not ask. |
| **Verification** | The report arrives with no working shown. Every line of it is a claim until you check it. |

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
collide. Note what the second one saw that the first did not. The rule for
parallel agents: **read-only lenses parallelise freely; writers need disjoint
ownership and a stop condition, or you get two agents editing the same file and
one of them losing.**

**5. Now measure it, in the main session first.** The trainer package here is too
small for the effect to clear the noise, so point at `../lab12_landing/invoicing`
— eight modules and two test files you have never opened. Read `/context` before
you ask anything, ask the main session where the test coverage is missing and
which gap it would close first, then read `/context` again. Both numbers go in
`DELEGATION.md`, under round A.

**6. `/clear`, then ask the same question of the subagent.** Same files, same
question, through the reviewer you wrote in step 1 — a survey for missing coverage
is its job, so this is still an invocation and not a restatement. `/context` on
each side of that too, under round B, and then do the subtraction twice. The claim
under test is that the main window stays clean. You are finding out by how much,
on files that are actually there.

**7. Triage what came back.** Paste the report into `report.txt` and split it:

```bash
python3 triage.py report.txt        # writes TRIAGE.md, one block per finding
```

Mark every finding accept or reject, with a reason under it. **At least one of
them is wrong** — the reviewer read the code and not the docstring beside it at
least once, and a finding you accepted without opening the file it names is a
finding you did not verify. Verification is the third cost, it is the one that
does not shrink when you delegate, and this is the step that makes you pay it on
purpose instead of discovering the bill later.

> Kousen's ch. 8 has a full subagent file, the invocation that goes with it, and a
> worked anti-example of parallel agents that collide. All of them are his. Yours
> has to be written from the four requirements above, and the measurement in steps
> 5 to 7 is this lab's.

## Done when

`python check.py lab09` passes: a file under `.claude/agents/` whose frontmatter
parses, with a description, an explicit tool list, and a body that states what
comes back; a `DELEGATION.md` whose four readings subtract to the saving you
claimed; and a `TRIAGE.md`, written by `triage.py` and not by you, where every
finding has a verdict and a reason, at least one of them is a reject, and the
reject names the path, the line or the sentence you checked it against.

And you can say what the review missed. Two lenses is not two opinions; it is two
coverage areas, and neither covers everything.

## Fair warning

Three of them. The reviewer is read-only, and it has to stay that way for step 5:
lab 12's checker fails if anything edits that fixture, so an agent with `Edit` in
its tool list can quietly cost you another lab. Reading it also spends a little of
lab 12's surprise — you will arrive there having seen `invoicing/` from the
outside once. That is a trade made on purpose: code you have never opened is the
only place the effect is large enough to clear the noise, and this repo has one
such package.

And `/context` moves between versions and between models. The absolute numbers are
worth little on their own; the gap between round A and round B is the finding, and
if it comes out smaller than you expected, write that down rather than re-running
until it looks better. A saving of 2K on a survey you do twice a day is still a
saving, and a saving of zero is the more interesting result.

Last, what the checker can see. It re-does your subtraction, it refuses a reading
too small to have come off `/context`, and it asks that a reject name a path, a
line or the sentence you found there. **This is a grep, not a judge** — it cannot
tell a reading you took from one you invented, and it cannot open the file behind
a finding and see whether your verdict was right. Five plausible sentences you
never checked will pass it. The person being checked on here is you.
