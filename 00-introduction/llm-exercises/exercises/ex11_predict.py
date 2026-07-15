"""
Exercise 11 — Use the fine-tuned model (from logits).

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 11
Reference: solutions/ex11_predict.py
"""

import pathlib
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

SAMPLE = "This is the worst service I've ever had."


def solve(text):
    # Load the model YOU fine-tuned and saved in exercise 10:
    model_dir = pathlib.Path(__file__).resolve().parent.parent / "finetuned-demo"
    tok = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    inp = tok(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        logits = model(**inp).logits
    # Fill: the axis to argmax over (1), and the string method to upper-case.
    pred = int(torch.argmax(logits, dim=____))
    return model.config.id2label[pred].____()


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        model_dir = pathlib.Path(__file__).resolve().parent.parent / "finetuned-demo"
        if not model_dir.exists():
            print("No fine-tuned model yet — run exercise 10 first (its demo saves it).")
        else:
            print(solve(SAMPLE))
