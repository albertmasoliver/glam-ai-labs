"""
Reference solution 3 — Translate with a pipeline.

Complete, self-contained reference. Verify:  python check.py --solutions 3
"""

from transformers import pipeline

SAMPLE = "Where is the nearest train station?"


def solve(text):
    translator = pipeline(task="translation_en_to_es",
                          model="Helsinki-NLP/opus-mt-en-es")
    return translator(text)[0]["translation_text"]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve(SAMPLE))
