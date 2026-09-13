# Three instructions, three homes

One instruction in each home, and one piece of evidence for each. Fill the
readings in as you take them — the ones you reconstruct afterwards are guesses.

## The placement

| Instruction | Home | Kind |
|---|---|---|
| <the sentence you left in CLAUDE.md> | `CLAUDE.md` | advisory |
| <the sentence you scoped to a path> | `.claude/rules/<file>.md` | scoped |
| <the sentence you refused to leave to advice> | `.claude/hooks/<file>.sh` | enforced |

## Proof 1 — the advisory one is obeyed, but not always

**The request I repeated:** <the same words, three fresh sessions, /clear between>

| Session | Obeyed | What it did instead |
|---|---|---|
| 1 | <yes/no> | <leave blank if it obeyed> |
| 2 | <yes/no> | <> |
| 3 | <yes/no> | <> |

**Compliance:** <n> of 3

## Proof 2 — the scoped one is only there sometimes

**Loaded with no matching file in play:** <yes/no, read off /context>

**Loaded once a matching file is in play:** <yes/no, read off /context>

**What made it appear:** <the file you opened or asked about>

## Proof 3 — the enforced one does not ask

**The edit I asked for:** <the request the hook refused>

**Hook exit code:** <n>

**Did the edit happen:** <yes/no — open the file and look, rather than believing
the transcript>

## What I measured

<Three or four sentences. Which of the three outcomes could have gone the other
way, and what that means for the instruction you care about most.>
