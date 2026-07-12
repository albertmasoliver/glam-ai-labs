"""
Reference solution 11 — Use the fine-tuned model (from logits).

Complete, self-contained reference. Verify:  python check.py --solutions 11
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

SAMPLE = "This is the worst service I've ever had."


def solve(text):
    name = "distilbert-base-uncased-finetuned-sst-2-english"
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForSequenceClassification.from_pretrained(name)
    inp = tok(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        logits = model(**inp).logits
    pred = int(torch.argmax(logits, dim=1))
    return model.config.id2label[pred].upper()


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve(SAMPLE))
