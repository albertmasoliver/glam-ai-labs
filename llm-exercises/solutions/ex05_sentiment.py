"""
Reference solution 5 — Classify sentiment.

Complete, self-contained reference. Verify:  python check.py --solutions 5
"""

from transformers import pipeline

SAMPLE = "Honestly the best coffee I've ever had."


def solve(text):
    clf = pipeline(task="sentiment-analysis",
                   model="distilbert-base-uncased-finetuned-sst-2-english")
    return clf(text)[0]["label"]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve(SAMPLE))
