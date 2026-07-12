"""
Reference solution 7 — Tokenize texts (padding, truncation, tensors).

Complete, self-contained reference. Verify:  python check.py --solutions 7
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
    return tokenizer(texts, return_tensors="pt", padding=True,
                     truncation=True, max_length=64)


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
