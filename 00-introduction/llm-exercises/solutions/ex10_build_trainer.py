"""
Reference solution 10 — Wire up the Trainer.

Complete, self-contained reference. Verify:  python check.py --solutions 10
"""

from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          Trainer, TrainingArguments)
from datasets import Dataset


def solve(model, args, train_ds, eval_ds, tokenizer):
    return Trainer(model=model, args=args, train_dataset=train_ds,
                   eval_dataset=eval_ds, tokenizer=tokenizer)


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        # Assemble the Trainer and actually fine-tune for 2 steps on a tiny dataset (CPU-ok).
        tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert-base-uncased", num_labels=2)
        data = Dataset.from_dict(
            {"text": ["a great day", "a terrible day", "loved it", "hated it"],
             "label": [1, 0, 1, 0]}).map(
            lambda b: tok(b["text"], padding="max_length", truncation=True, max_length=16),
            batched=True)
        args = TrainingArguments(output_dir="./out", max_steps=2,
                                 per_device_train_batch_size=2, logging_steps=1, report_to=[])
        trainer = solve(model, args, data, data, tok)
        result = trainer.train()   # real training loop — a couple of gradient steps
        print("trained — final loss:", round(result.training_loss, 4))
