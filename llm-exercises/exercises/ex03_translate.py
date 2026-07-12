"""
Exercise 3 — Translate with a pipeline.

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 3
Reference: solutions/ex03_translate.py
"""

from transformers import pipeline

SAMPLE = "Where is the nearest train station?"


def solve(text):
    # Fill: the task name for English -> Spanish translation.
    translator = pipeline(task=____,
                          model="Helsinki-NLP/opus-mt-en-es")
    return translator(text)[0]["translation_text"]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve(SAMPLE))
