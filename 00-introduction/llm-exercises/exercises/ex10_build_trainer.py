"""
Exercise 10 — Wire up the Trainer.

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 10
Reference: solutions/ex10_build_trainer.py
"""

from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          Trainer, TrainingArguments)
from datasets import Dataset


def solve(model, args, train_ds, eval_ds, tokenizer):
    # Fill: pass the model, the args, and the two datasets into the Trainer.
    return Trainer(
        model=____,
        args=____,
        train_dataset=____,
        eval_dataset=____,
        tokenizer=tokenizer,
    )


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        # Assemble the Trainer, fine-tune 2 steps on a tiny dataset, and SAVE the model.
        import pathlib
        tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        model = AutoModelForSequenceClassification.from_pretrained(
            "distilbert-base-uncased", num_labels=2,
            id2label={0: "NEGATIVE", 1: "POSITIVE"}, label2id={"NEGATIVE": 0, "POSITIVE": 1})
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
        save_dir = pathlib.Path(__file__).resolve().parent.parent / "finetuned-demo"
        model.save_pretrained(save_dir); tok.save_pretrained(save_dir)
        print("saved fine-tuned model to", save_dir.name, "/  (exercise 11 loads it)")
