"""
Exercise 7 — Tokenize texts (padding, truncation, tensors).

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 7
Reference: solutions/ex07_tokenize.py
"""

from transformers import AutoTokenizer

SAMPLE = [
    "The parcel arrived a day early and everything inside was wrapped carefully, "
    "so I am really happy with how this order turned out.",
    "Delivery ran late, the box was badly crushed on one corner, and one of the "
    "mugs inside had a small chip, which was honestly a bit disappointing.",
    "Good value.",
]


def solve(tokenizer, texts):
    # Fill: return PyTorch tensors ("pt"), and cap the length at 64 tokens.
    return tokenizer(texts, return_tensors=____, padding=True,
                     truncation=True, max_length=____)


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        enc = solve(tok, SAMPLE)
        print("shape:", tuple(enc["input_ids"].shape),
              " (rows = sentences, cols = padded length)")
        print("\ninput_ids (0 = [PAD]; sentences padded to the longest one):")
        print(enc["input_ids"])
        print("\nattention_mask (1 = real token, 0 = padding the model ignores):")
        print(enc["attention_mask"])
