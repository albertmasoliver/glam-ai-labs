"""
Exercise 9 — Set up TrainingArguments (offline).

Self-contained: imports at the top, then complete solve() by replacing every
____ blank (see the comments). Verify:  python check.py 9
Reference: solutions/ex09_training_args.py
"""

from transformers import TrainingArguments


def solve():
    # Fill the values described in the task.
    return TrainingArguments(
        output_dir="./out",
        eval_strategy=____,               # evaluate at the end of each epoch
        num_train_epochs=____,            # 3
        learning_rate=____,               # 2e-5
        per_device_train_batch_size=____, # 8
        per_device_eval_batch_size=8,
        weight_decay=____,                # 0.01
    )


if __name__ == "__main__":
    import inspect
    if "____" in inspect.getsource(solve):
        print("Fill in the ____ blanks, then run again  (or: python check.py).")
    else:
        print(solve())
