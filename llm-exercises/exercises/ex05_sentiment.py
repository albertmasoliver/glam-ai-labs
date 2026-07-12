"""
Exercise 5 — Classify sentiment.

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 5
Reference: solutions/ex05_sentiment.py
"""

from transformers import pipeline

SAMPLE = "Honestly the best coffee I've ever had."


def solve(text):
    # Fill: the task name for sentiment, and the output key holding the label.
    clf = pipeline(task=____,
                   model="distilbert-base-uncased-finetuned-sst-2-english")
    return clf(text)[0][____]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve(SAMPLE))
