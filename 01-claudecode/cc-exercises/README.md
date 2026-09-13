# Claude Code labs — runnable workbook

Twelve labs. The printable explanation lives in [`../study-guide.md`](../study-guide.md);
this folder is the part you run.

It is not shaped like `00-introduction/`, and it cannot be. There, an exercise is a
function with blanks and the verifier calls it. Here the exercise is *"send this
request and notice that it did not run the tests"* — so the verifier checks **the
artifact the lab leaves behind**: a package that imports and passes its tests with
an injected storage, a `settings.json` whose deny rules are well formed, a `SKILL.md`
whose frontmatter actually parses. Labs whose result is judgement report `MANUAL` and
print their definition of done.

## Layout

```
exercises/     the starting state, one folder per lab, each with its brief in README.md
solutions/     reference end states for the same labs
check.py       the artifact verifier
requirements.txt
```

## Setup

```bash
cd cc-exercises
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Lab 12 replays a git history before you start it:

```bash
bash exercises/lab12_landing/make-history.sh
```

## Check it works before you start

```bash
python check.py --solutions      # expect 11 PASS, 3 MANUAL
python check.py                  # your side: TODO everywhere, no errors
```

If the first command passes, your environment is good.

## Workflow

1. Open `exercises/labNN_*/README.md`. It says what to do and what "done" means.
2. Work in that folder with Claude Code. The labs are the point; the artifacts are
   evidence.
3. Verify:
   ```bash
   python check.py              # all twelve
   python check.py lab05 lab07  # just some
   python check.py --solutions  # the reference answers
   ```

| Status | Meaning |
|---|---|
| `PASS` | The artifact is there and correct. |
| `TODO` | The artifact is not there yet — you have not done this lab. |
| `FAIL` | It is there and something about it is wrong; the message says what. |
| `MANUAL` | Nothing machine-checkable. The definition of done is printed instead. |

## The labs

| | Lab | Verified by |
|---|---|---|
| 00 | the three scales | both fixtures placed with reasons; `scales.py` measures something that is not a size |
| 01 | first contact | MANUAL |
| 02 | the five jobs | the fix transfers to the handler nobody named; frozen files unchanged |
| 03 | the window, measured | the readings agree with each other and with the estimate |
| 04 | auditing the evidence | the weakened assertion is strict again; the untested input no longer crashes |
| 05 | project memory | `CLAUDE.md` short and complete; one scoped rule parses; the hook the checker runs refuses `lines.py` and nothing else; the compliance table adds up |
| 06 | permissions | `settings.json` parses; `.env` **and variants** denied |
| 07 | skills and hooks | `SKILL.md` frontmatter survives YAML; routing recorded in three states; the PreToolUse gate exits 2 on annotated source |
| 08 | what a capability costs | the MCP server completes a handshake and answers; both context readings recorded |
| 09 | subagents | agent file with frontmatter, tool list, reporting contract; the two rounds subtract to the saving claimed; one finding rejected with a reason |
| 10 | the contract and the gate | four contract sections; `pr_gate.py` green over the tests they name |
| 11 | review and recovery | MANUAL |
| 12 | landing in a codebase | fixture intact; `ORIENTATION.md` records what you checked |
| 13 | when not to use it | MANUAL |

Lab 08 used to be missing, because the study guide's section 8 is a discussion with
nothing to build. The published deck gives module 8 to MCP, which has plenty to
build, so 08 is now the MCP lab and the numbering finally runs without a gap.

## What the verifier cannot do

It can tell you the broken links in lab 04's evidence chain are repaired. It cannot
tell you whether you would have found them unprompted, and finding them unprompted is
the point. The `MANUAL` definitions of done carry that weight, and they are not
decoration.
