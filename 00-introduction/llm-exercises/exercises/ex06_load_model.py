"""
Exercise 6 — Load an Auto model + tokenizer.

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 6
Reference: solutions/ex06_load_model.py
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification


def solve():
    name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(name)
    # Fill: which imported class loads a classification head, and how many labels.
    model = ____.from_pretrained(name, num_labels=____)
    return tokenizer, model


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        tok, model = solve()
        print(type(model).__name__, "num_labels =", model.config.num_labels)
