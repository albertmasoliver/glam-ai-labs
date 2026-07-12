"""
Reference solution 4 — Pick the right transformer family (offline).

Complete, self-contained reference. Verify:  python check.py --solutions 4
"""


def solve(task):
    families = {"sentiment": "encoder-only", "poem": "decoder-only",
                "translation": "encoder-decoder", "extractive-qa": "encoder-only"}
    return families[task]


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        for t in ("sentiment", "poem", "translation", "extractive-qa"):
            print(f"{t:>14} -> {solve(t)}")
