"""
Reference solution 6 — Load an Auto model + tokenizer.

Complete, self-contained reference. Verify:  python check.py --solutions 6
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification


def solve():
    name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=2)
    return tokenizer, model


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        tok, model = solve()
        print(type(model).__name__, "num_labels =", model.config.num_labels)
