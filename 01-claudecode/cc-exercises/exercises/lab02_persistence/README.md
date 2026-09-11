# Lab 02 — get what you asked for

`trainer.py` is a doghouse: one file, no dependencies, shows a line of Sonnet 18
and advances on Enter. It works, and it forgets everything when you quit.

Add persistence. The point of the lab is not the feature — it is that a vague
request and a precise one produce different code from the same model.

## What to do

**1. Ask badly, on purpose.** "Save my place" or "make it remember where I was."
Note what you get: where it decided to write, what it called the key, whether it
extracted a module you did not ask for.

**2. Throw that away** (`git checkout .`, or start from the copy here) and ask
precisely:

```text
Add persistence to the trainer. When the user advances to a new line,
save the current line index to ~/.lyrics-trainer.json, under the key
"line_index". On startup, read that file and resume from the saved
position if one exists. If the saved position is out of range for the
current text, fall back to line 0.

Success condition: quit after advancing a few lines, run it again, and
it resumes at the same line. Corrupt or out-of-range saved values fall
back safely to the first line.

Keep the current single-file structure. Add the storage logic where it
naturally fits, but don't extract modules or add a dependency.

Before you start: what is ambiguous here, what are you about to
assume that I have not told you, and is there an approach I have
not considered?
```

Four things are doing work there, and you should be able to name them: the
**location and key** (so the artifact is inspectable), the **success condition**
(so "done" is not its opinion), the **structural fence** — *keep the single-file
structure, don't extract modules* — and the **clarification pass** at the end,
which is the cheapest three lines in this whole lab set. It costs one turn and it
routinely surfaces a decision you did not know you were making.

> Kousen's *Claude Code: Up and Running* (ch. 3) runs this comparison in
> JavaScript with `localStorage`, and he has his own three-line clarification
> pass, which is worth reading. Both the prompt and the closing questions above
> are this lab set's.

**3. Then push back on one decision.** If it inlined the write:

```text
The implementation put the json.dump(...) call directly in the loop.
Why not create a save_state() function instead?
```

Notice you did not tell it to change anything. Ask why, and you get a defence or
a concession; either is information. Tell it to change, and you get a change.

## Done when

`python check.py lab02` passes: the app resumes after a restart, and a corrupt
file, a non-numeric index and an out-of-range index all fall back to line 1.

You should also be able to say, in one sentence, which clause of the second
prompt bought you each of those three fallbacks.
