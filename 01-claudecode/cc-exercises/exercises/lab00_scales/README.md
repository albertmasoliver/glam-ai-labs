# Lab 00 — the three scales

Two small Python projects, in `fixtures/`. Fifteen minutes, and you will not write
any application code: the work is measuring, classifying, and then finding out what
your measurements could not see.

`scales.py` reports on either of them. Run it on both before you read any further.

```bash
./make-history.sh                 # once; the history is part of the fixture
python3 scales.py fixtures/alpha
python3 scales.py fixtures/beta
```

Four of the five numbers come out within a rounding error of each other. The fifth,
the file count, is twice as high for one of them — and if you let that decide, you
would be reading a difference of two files as a difference of scale.

**That is the exercise.** One of these is a doghouse and the other is not, and nothing
`scales.py` prints will tell you which, because the thing that separates them is not a
quantity of anything.

## Setting it up

`make-history.sh` replays a real commit history into each fixture. It is not
decoration — in one of the two projects, the history is where the answer is.

## What to do

**1. Classify each project, and commit to it in writing.** Open `SCALES.md` and fill
in the two verdicts. Doghouse, cabin or skyscraper, one line of reasoning each. Do
this before you go looking for evidence, so you find out whether your first instinct
was right.

**2. Find three signals `scales.py` cannot see.** Read the fixtures — all of them,
including the files that are not Python. Somewhere in `fixtures/beta` there is
evidence that other people work inside this project and that its output is load
bearing for someone else. Find three separate pieces of it and write them down.

If two of your three are the same fact in different clothes, you have two. Keep
looking.

**3. Teach the tool one of them.** Pick the signal you think is strongest and ask
Claude Code to add it to `scales.py` as one more measured line. Keep the request
small and say what the number means, not how to compute it.

You should be in manual mode for this — `Shift+Tab` until the mode line stops
saying auto. When the request reaches the point of editing `scales.py`, it will
stop and ask. **Notice that it stopped.** Reading the fixtures did not need
permission and writing to a file does; that gate is the whole shape of the
request loop, and this is the cheapest place in the course to watch it happen.

**4. Run it again on both.** If your new metric reports the same value for `alpha`
and `beta`, it is another size metric wearing a disguise. Go back to step 3.

> The doghouse / cabin / skyscraper framing is Kousen's, from chapter 1 of
> *Claude Code: Up and Running*, and his text for it is not reproduced here.
> What this lab adds is the measurement, and the demonstration that the framing
> does not reduce to one.

## The sentence this lab is actually about

The line between a cabin and a skyscraper is **coordination, not size**. What moves
a project up is other people working inside it: a rewrite that has to be scheduled,
a consumer whose data you would break, a pipeline someone else reads when it goes
red.

Size is easy to measure and it is the wrong measurement. That is an uncomfortable
combination, and it is why people build doghouses like skyscrapers and never ship,
or skyscrapers like doghouses and find out later.

## Done when

`python check.py lab00` passes: `SCALES.md` classifies both fixtures with a reason
for each and lists three distinct coordination signals, and `scales.py` measures at
least one thing that is not a size — something that reads the history, the
consumers, or the pipeline, and that reports different values for the two fixtures.

## One honest caveat

A coordination signal is a judgement, and the checker cannot make it. It can see
that your new metric separates the two projects and that you wrote three signals
down; it cannot see whether the three are any good. Read them back after a day.
