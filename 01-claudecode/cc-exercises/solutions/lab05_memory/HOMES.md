# Three instructions, three homes

A reference answer. The readings are from one real run of three sessions; yours
will differ, and the point survives either way.

## The placement

| Instruction | Home | Kind |
|---|---|---|
| For nontrivial changes, propose a plan before editing. | `CLAUDE.md` | advisory |
| Never construct a `JsonFileStorage` in a unit test; pass a fake. | `.claude/rules/testing.md` | scoped |
| Never edit `trainer/lines.py` by hand. | `.claude/hooks/protect-lines.sh` | enforced |

Why the third one is not a sentence in `CLAUDE.md`: nothing downstream would
notice it being broken. Every navigation test compares `LINES` to itself, so a
mangled sonnet passes the suite. An instruction whose violation is invisible is
the one that has to be a mechanism.

## Proof 1 — the advisory one is obeyed, but not always

**The request I repeated:** "Add a `--start N` option to the CLI so practice
resumes from a given line."

| Session | Obeyed | What it did instead |
|---|---|---|
| 1 | yes | proposed the argparse change and the navigation seam before touching anything |
| 2 | no | edited `cli.py` immediately, then described the plan afterwards as a summary |
| 3 | yes | |

**Compliance:** 2 of 3

The instruction was in context all three times, identical, twelve lines from the
top of a 43-line file. Session 2 is not a bug and there is nothing to fix; it is
what advisory means.

## Proof 2 — the scoped one is only there sometimes

**Loaded with no matching file in play:** no

**Loaded once a matching file is in play:** yes

**What made it appear:** asking about `tests/test_storage.py`. Before that,
`/context` listed `CLAUDE.md` under project memory and nothing else. After, it
listed `testing.md` as well, 180 tokens. Cleared the session, asked about
`trainer/storage.py` instead, and it was gone again.

Those 180 tokens are the ones you are not paying while you edit `navigation.py`,
which is the whole argument for the `paths:` key.

## Proof 3 — the enforced one does not ask

**The edit I asked for:** "In `trainer/lines.py`, change `dimm'd` to `dimmed` so
the text reads naturally."

**Hook exit code:** 2

**Did the edit happen:** no. `git diff -- trainer/lines.py` is empty, and the
file still reads `dimm'd`. The refusal text came back into the session and it
offered to change the display instead, which is the right answer.

Whether another exit code would have done the same thing is lab 07's subject.
What is recorded here is only that the edit did not happen.

## What I measured

Two of the three outcomes could have gone the other way and one could not. The
advisory instruction was obeyed twice out of three with no variable changed
between runs; the scoped one was absent for most of the session by design and
only cost tokens when it was relevant; the hook refused on every attempt because
refusing is not a judgement it makes. So the placement question is not about
importance — "propose a plan first" matters more to me day to day than the
sonnet's spelling. It is about whether I can afford a 2-in-3. Where I cannot,
advice is the wrong container no matter how firmly it is written.
