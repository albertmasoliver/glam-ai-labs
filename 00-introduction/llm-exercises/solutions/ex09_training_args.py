"""
Reference solution 9 — Set up TrainingArguments (offline).

Complete, self-contained reference. Verify:  python check.py --solutions 9
"""

from transformers import TrainingArguments


def solve():
    return TrainingArguments(
        output_dir="./out", eval_strategy="epoch", num_train_epochs=3,
        learning_rate=2e-5, per_device_train_batch_size=8,
        per_device_eval_batch_size=8, weight_decay=0.01)


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve())
