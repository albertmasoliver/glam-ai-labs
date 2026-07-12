"""
Exercise 4 — Pick the right transformer family (offline).

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 4
Reference: solutions/ex04_family.py
"""


def solve(task):
    # Fill each family: understanding -> "encoder-only";
    # free generation -> "decoder-only"; seq-to-seq -> "encoder-decoder".
    families = {
        "sentiment": ____,
        "poem": ____,
        "translation": ____,
        "extractive-qa": ____,
    }
    return families[task]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        for t in ("sentiment", "poem", "translation", "extractive-qa"):
            print(f"{t:>14} -> {solve(t)}")
