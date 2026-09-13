# Lab 10 — the contract and the gate

An issue that is not a task, a cart that already works, and a gate that reads your
contract back to you. Thirty-five minutes. It is the longest in the set and it is the one that looks most like the job.

```bash
python3 -m pytest -q     # 6 passing
python3 pr_gate.py       # red: the contract is still a template
```

Read `ISSUE.md` first. It is eight bullets long and it is somebody's idea of a
feature, not a unit of work. **Nothing in this lab happens until you have cut it
down**, and the gate will not let you pretend otherwise.

## What to do

**1. Narrow it to one slice, and write down what you are not doing.** One sentence
in `SPEC.md`, and if the sentence needs an "and", it is two slices. Then list the
bullets you are leaving in the backlog, by name. The list you refuse is the part
that survives review.

Ask Claude Code for candidate slices if it helps, but pick yourself. It will
happily implement all eight.

**2. Write the contract, not the steps.** Four sections in `SPEC.md`:
postconditions, preconditions, invariants, negative criteria. A procedure frays
when a session is compacted — step four of seven means nothing on its own. A
postcondition survives, because it is a claim about the world rather than a
position in a list.

**Every postcondition and every invariant names the test that proves it**, as a
pytest node id in backticks. A claim with no test under it is a sentence.

Your invariants are already written: they are the tests in `tests/test_cart.py`
that must still be green when you are done. Read `orders/cart.py` before you choose
them — there is a note in it about where the rounding lives and why, and that note
is an invariant somebody learned the hard way.

**3. Ask for a plan, and find the thing it trades away.** Give it the contract and
ask for a step-by-step plan before any edit. Then read the plan against the
contract, not against your hopes. Somewhere in it there will be a step that is
reasonable on its own and breaks a line you wrote down. Record it in `PR.md` — the
step, the line it broke, and what you asked for instead.

**4. Implement, and let the gate judge it.** `python3 pr_gate.py` runs every test
your contract names and tells you which claims are still sentences. Green means
every line of the contract points at something that passes. It does not mean the
slice is good.

**5. Run it headless, twice.** Once with `--bare` and once without, and write down
the difference in `PR.md`.

This folder has a `.claude/settings.json` with a `Stop` hook in it, so there is
something real to observe. The hook is deliberately trivial — it appends a line to
`.claude/runs.log` and exits 0 — but it is enough, and `Stop` fires whenever a session
ends, so a `-p` run always triggers it. Delete the log, run headless without `--bare`,
and look at the log. Then run it again with `--bare`, and look again.

Nobody asked you whether that hook should run. That is the single fact to carry out of
this lab if you are ever going to put Claude Code in CI: without `--bare`, a headless
run loads the project's hooks and connects its MCP servers, and there is no dialog.

> Chapter 9 of Kousen's *Claude Code: Up and Running* runs the issue-to-pull-request
> pipeline and chapter 5 covers headless mode. His prompts are not reproduced here;
> the issue, the cart, the contract format and the gate are the lab's.

## Done when

`python check.py lab10` passes: `SPEC.md` names one slice and what it leaves behind,
all four contract sections have content, `pr_gate.py` exits green, and `PR.md`
records the plan step you corrected and what `--bare` changed.

## One honest caveat

The gate checks that each claim points at a passing test. It cannot check that the
test proves the claim — `test_one_row_per_cart_line` could assert `True` and the gate
would be just as green. That is the same hole every verification has, and the reason
the module says to review the verifier before the implementation.
