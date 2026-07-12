"""
Reference solution 2 — Generate text (control length + padding).

Complete, self-contained reference. Verify:  python check.py --solutions 2
"""

from transformers import pipeline

SAMPLE = "A good morning routine starts with"


def solve(prompt):
    gen = pipeline(task="text-generation", model="distilgpt2")
    out = gen(prompt, max_new_tokens=30,
              pad_token_id=gen.tokenizer.eos_token_id, truncation=True)
    return out[0]["generated_text"]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve(SAMPLE))
