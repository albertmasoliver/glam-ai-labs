# LLM exercises — runnable workbook

Personal practice for the Hugging Face skills in *Introduction to LLMs in Python*.
The theory + printable before/after version live in [`../study-guide.md`](../study-guide.md);
this folder is the **executable** part. Exercises start **incomplete** — you fill them in and
verify.

## Layout — one file per exercise

```
exercises/    exNN_*.py   ← YOUR workbook: each solve() is incomplete
solutions/    exNN_*.py   ← reference answers (same filenames)
check.py                  ← verifier
requirements.txt
```

Each file is **self-contained** — its own imports at the top, a `solve(...)` to complete,
and a runnable demo — so you can read and run any one on its own:

```bash
python exercises/ex01_summarize.py     # runs your version on a sample input
python solutions/ex01_summarize.py     # runs the reference answer
```

## Setup

```bash
cd llm-exercises
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Check it works before you start

```bash
python check.py 4 9         # exercises 4 & 9 need NO internet
```
You should see two `TODO` lines — the harness runs, the functions just aren't done yet.
Now confirm the *reference* solutions pass:
```bash
python check.py --solutions 4 9      # expect: PASS PASS
```
If those work, your environment is good. (Exercises other than 4 and 9 download a small
model from the Hugging Face Hub the first time — internet + a few hundred MB of disk.)

## Workflow

1. Open `exercises/exNN_*.py`. Most of `solve` is already written — replace each `____`
   blank with the right value (the comment above each line tells you what goes there).
2. Verify:
   ```bash
   python check.py            # all 11
   python check.py 1 2 6      # just some
   python check.py --show 4   # also print what solve() returned
   ```
   `check.py` shows only the status by default; add `--show` to print each `solve()`'s output,
   or run a file directly (`python solutions/ex01_summarize.py`) to see it.
3. Read the status:

   | Status | Meaning |
   |---|---|
   | `PASS` | Your `solve()` returned the right thing. |
   | `TODO` | Not implemented yet. |
   | `FAIL` | It ran but the result was wrong (message says why). |
   | `SKIP` | A model/dataset couldn't download (no internet) or deps missing. |
   | `ERR`  | Unexpected error (message shown). |

4. Stuck? Compare with the matching file in `solutions/`. Confirm the reference anytime with
   `python check.py --solutions`.

Start with **4** and **9** (offline), then the pipeline ones (1, 2, 3, 5), then the
fine-tuning path (6, 7, 8, 10, 11).
