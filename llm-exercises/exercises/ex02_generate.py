"""
Exercise 2 — Generate text (control length + padding).

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 2
Reference: solutions/ex02_generate.py
"""

from transformers import pipeline

SAMPLE = "A good morning routine starts with"


def solve(prompt):
    gen = pipeline(task="text-generation", model="distilgpt2")
    # Fill: how many NEW tokens to generate (30), and the end-of-sequence token id
    # to pad with. (Use max_new_tokens, not max_length: the pipeline already
    # defaults max_new_tokens, so mixing in max_length triggers a warning.)
    out = gen(prompt, max_new_tokens=____,
              pad_token_id=gen.tokenizer.____, truncation=True)
    return out[0]["generated_text"]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve(SAMPLE))
