"""
Reference solution 8 — Tokenize a whole dataset with .map.

Complete, self-contained reference. Verify:  python check.py --solutions 8
"""

from transformers import AutoTokenizer
from datasets import load_dataset


def solve(tokenizer):
    data = load_dataset("imdb", split="train[:1%]")

    def tok(batch):
        return tokenizer(batch["text"], padding=True, truncation=True, max_length=128)

    return data.map(tok, batched=True)


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        ds = solve(tok)
        print("columns:", ds.column_names, " (input_ids + attention_mask are new)")
        print("rows:   ", ds.num_rows)
        row = ds[0]
        print("\n--- one tokenized example ---")
        print("label         :", row["label"])
        print("text          :", row["text"][:90].replace(chr(10), " "), "...")
        ids = row["input_ids"]
        print("input_ids     :", ids[:16], "...  (length", len(ids), ")")
        print("attention_mask:", row["attention_mask"][:16], "...")
        print("decoded back  :", tok.decode(ids[:16]))
