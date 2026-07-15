#!/usr/bin/env python3
"""
check.py — verify the exercises actually work.

    python check.py                # check exercises/  (your workbook)
    python check.py --solutions    # check solutions/  (should be all PASS online)
    python check.py 4 9            # only these numbers (4 & 9 need NO internet)
    python check.py --show 4 11    # also print what each solve() returned
    python check.py --solutions --show    # see every reference output

Each exercise lives in its own file (exercises/exNN_*.py) and exposes solve(...).
Statuses:
    PASS  solve() returned the right thing
    TODO  not implemented yet (an ____ blank is still there)
    FAIL  it ran but returned something wrong
    SKIP  a model/dataset couldn't be downloaded (no internet) or deps missing
    ERR   unexpected error (see the message)

For a text exercise the check runs the file's own `SAMPLE`, so `--show` shows the result of
*your* input and `PASS` means the result is valid (e.g. a real POSITIVE/NEGATIVE label) — not
that some hidden sentence matched. Exercises 4 and 9 run fully offline; the rest download a
small model on first use.
"""
import sys
import pathlib
import importlib.util
from functools import lru_cache

HERE = pathlib.Path(__file__).resolve().parent

NAMES = {1: "ex01_summarize", 2: "ex02_generate", 3: "ex03_translate",
         4: "ex04_family", 5: "ex05_sentiment", 6: "ex06_load_model",
         7: "ex07_tokenize", 8: "ex08_tokenize_dataset", 9: "ex09_training_args",
         10: "ex10_build_trainer", 11: "ex11_predict"}
OFFLINE = {4, 9}  # family, training_args


def load(n, folder):
    """Import the exercise file and return the module (so checks can use its SAMPLE)."""
    path = HERE / folder / f"{NAMES[n]}.py"
    spec = importlib.util.spec_from_file_location(f"{folder}_{NAMES[n]}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---- fixtures the checks reuse (built here, not from the student's code) ----

@lru_cache(maxsize=None)
def fx_tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained("distilbert-base-uncased")

@lru_cache(maxsize=None)
def fx_model():
    from transformers import AutoModelForSequenceClassification
    return AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2)

@lru_cache(maxsize=None)
def fx_args():
    from transformers import TrainingArguments
    return TrainingArguments(output_dir="./out")

@lru_cache(maxsize=None)
def fx_dataset():
    from datasets import Dataset
    tok = fx_tokenizer()
    d = Dataset.from_dict({"text": ["a great day", "a terrible day"], "label": [1, 0]})
    return d.map(lambda b: tok(b["text"], padding=True, truncation=True, max_length=16),
                 batched=True)

@lru_cache(maxsize=None)
def fx_finetuned_dir():
    """Ensure exercise 10's saved model exists (so exercise 11 can load it), creating a tiny
    fine-tuned model here if it isn't there yet."""
    d = HERE / "finetuned-demo"
    if (d / "config.json").exists():
        return d
    from transformers import (AutoModelForSequenceClassification, Trainer, TrainingArguments)
    from datasets import Dataset
    tok = fx_tokenizer()
    model = AutoModelForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", num_labels=2,
        id2label={0: "NEGATIVE", 1: "POSITIVE"}, label2id={"NEGATIVE": 0, "POSITIVE": 1})
    data = Dataset.from_dict(
        {"text": ["a great day", "a terrible day", "loved it", "hated it"], "label": [1, 0, 1, 0]}
    ).map(lambda b: tok(b["text"], padding="max_length", truncation=True, max_length=16),
          batched=True)
    args = TrainingArguments(output_dir=str(HERE / "out"), max_steps=2,
                             per_device_train_batch_size=2, logging_steps=1, report_to=[])
    Trainer(model=model, args=args, train_dataset=data, eval_dataset=data, tokenizer=tok).train()
    model.save_pretrained(d); tok.save_pretrained(d)
    return d

# ---- one checker per exercise ----
# Each checker runs the exercise's OWN `SAMPLE` where it takes a text input, so what the
# verifier runs is exactly what `python <file>` prints. It then asserts a *property* of the
# result (model outputs aren't deterministic, so we check validity, not one exact answer).

def c1(m):  # summarize
    s = m.solve(m.SAMPLE)
    assert isinstance(s, str) and s.strip(), "expected a non-empty summary string"
    return s

def c2(m):  # generate
    s = m.solve(m.SAMPLE)
    assert isinstance(s, str) and m.SAMPLE.split()[-1] in s, "expected text continuing the prompt"
    return s

def c4(m):  # translate
    t = m.solve(m.SAMPLE)
    assert isinstance(t, str) and t.strip(), "expected a non-empty translation"
    assert t.strip().lower() != m.SAMPLE.strip().lower(), "text was not translated"
    return t

def c5(m):  # transformer family — task keys, no SAMPLE
    got = {k: m.solve(k) for k in ("sentiment", "poem", "translation", "extractive-qa")}
    assert got == {"sentiment": "encoder-only", "poem": "decoder-only",
                   "translation": "encoder-decoder", "extractive-qa": "encoder-only"}, got
    return got

def c6(m):  # sentiment
    label = m.solve(m.SAMPLE)
    assert isinstance(label, str) and label.upper() in {"POSITIVE", "NEGATIVE"}, \
        f"expected POSITIVE or NEGATIVE, got {label!r}"
    return label

def c7(m):  # load model + tokenizer — no SAMPLE
    tok, model = m.solve()
    assert model.config.num_labels == 2, "model should have 2 labels"
    assert hasattr(tok, "encode"), "first return value should be a tokenizer"
    return f"{type(model).__name__}, num_labels={model.config.num_labels}"

def c8(m):  # tokenize — SAMPLE is the list of texts
    enc = m.solve(fx_tokenizer(), m.SAMPLE)
    ids = enc["input_ids"]
    assert ids.shape[0] == len(m.SAMPLE) and ids.shape[1] <= 64, "expected an [N, <=64] tensor"
    return f"input_ids shape={tuple(ids.shape)}, keys={list(enc.keys())}"

def c9(m):  # tokenize a dataset — no SAMPLE
    ds = m.solve(fx_tokenizer())
    assert "input_ids" in ds.column_names, "dataset should gain an input_ids column"
    return f"rows={ds.num_rows}, columns={ds.column_names}"

def c10(m):  # TrainingArguments — no SAMPLE
    a = m.solve()
    assert a.num_train_epochs == 3, "num_train_epochs should be 3"
    assert abs(a.learning_rate - 2e-5) < 1e-12, "learning_rate should be 2e-5"
    assert a.per_device_train_batch_size == 8, "train batch size should be 8"
    assert abs(a.weight_decay - 0.01) < 1e-12, "weight_decay should be 0.01"
    return (f"epochs={a.num_train_epochs}, lr={a.learning_rate}, "
            f"batch={a.per_device_train_batch_size}, weight_decay={a.weight_decay}")

def c11(m):  # wire the Trainer — fixtures
    from transformers import Trainer
    args = fx_args()
    ds = fx_dataset()
    t = m.solve(fx_model(), args, ds, ds, fx_tokenizer())
    assert isinstance(t, Trainer) and t.args is args, "expected a Trainer wired to the args"
    return f"{type(t).__name__} (model + args + datasets wired)"

def c12(m):  # predict from logits (loads the model saved by exercise 10)
    fx_finetuned_dir()   # make sure exercise 10's saved model is there to load
    label = m.solve(m.SAMPLE)
    assert isinstance(label, str) and label.upper() in {"POSITIVE", "NEGATIVE"}, \
        f"expected POSITIVE or NEGATIVE, got {label!r}"
    return label

# New number -> checker (exercises 3 "reply_prompt" and 13 "oneshot" were removed).
CHECKS = {1: c1, 2: c2, 3: c4, 4: c5, 5: c6, 6: c7,
          7: c8, 8: c9, 9: c10, 10: c11, 11: c12}

_NET_HINTS = ("connection", "connect", "couldn't reach", "could not reach", "offline",
              "max retries", "resolve", "name resolution", "can't load", "cannot find",
              "not a valid model", "hfhuboffline", "getaddrinfo", "temporarily unavailable")


def classify(exc):
    txt = f"{type(exc).__name__}: {exc}".lower()
    if isinstance(exc, NotImplementedError):
        return "TODO", str(exc)
    if isinstance(exc, FileNotFoundError):
        return "ERR", f"missing file: {exc.filename} (is the folder complete?)"
    if (isinstance(exc, ImportError) or "no module named" in txt or "requires" in txt
            or "sentencepiece" in txt or "installed in order to use" in txt
            or "cannot be instantiated" in txt):
        return "SKIP", "missing deps — run: pip install -r requirements.txt"
    if any(h in txt for h in _NET_HINTS):
        return "SKIP", "needs internet (model/dataset download)"
    if isinstance(exc, AssertionError):
        return "FAIL", str(exc) or "wrong result"
    return "ERR", txt


def _show(value):
    """Print solve()'s return value, indented and length-capped."""
    text = str(value)
    if len(text) > 600:
        text = text[:600] + " …"
    for line in text.splitlines() or [""]:
        print("       │ " + line)


def main():
    flags = {"--solutions", "--show"}
    folder = "solutions" if "--solutions" in sys.argv else "exercises"
    show = "--show" in sys.argv
    argv = [a for a in sys.argv[1:] if a not in flags]
    nums = [int(a) for a in argv] if argv else sorted(CHECKS)

    print(f"Checking {folder}/  ({len(nums)} exercise(s))\n")
    tally = {}
    for n in nums:
        value = None
        try:
            lines = (HERE / folder / f"{NAMES[n]}.py").read_text(encoding="utf-8").splitlines()
            s = next(i for i, l in enumerate(lines) if l.startswith("def solve"))
            e = next((i for i, l in enumerate(lines) if l.startswith("if __name__")), len(lines))
            if "____" in "\n".join(lines[s:e]):     # blanks left in solve's body
                status, note = "TODO", "fill in the ____ blanks"
            else:
                value = CHECKS[n](load(n, folder))
                status, note = "PASS", ""
        except Exception as exc:  # noqa: BLE001 — classified below
            status, note = classify(exc)
        tally[status] = tally.get(status, 0) + 1
        off = " (offline)" if n in OFFLINE else ""
        icon = {"PASS": "✓", "TODO": "·", "FAIL": "✗", "SKIP": "~", "ERR": "!"}[status]
        print(f"  {icon} Ex {n:<2}{off:<10} {status}" + (f"  — {note}" if note else ""))
        if show and value is not None:
            _show(value)

    print("\n" + "  ".join(f"{k}:{v}" for k, v in sorted(tally.items())))
    if tally.get("FAIL") or tally.get("ERR"):
        sys.exit(1)


if __name__ == "__main__":
    main()
