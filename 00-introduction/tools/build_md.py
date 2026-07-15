#!/usr/bin/env python3
"""Assemble two docs from the exercise files:
  - study-guide.md          : setup + per-section theory + exercises
                              (task, what the scaffold does, a hint, the code to complete)
  - study-guide-solutions.md : the answers only, grouped the same way.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXD = ROOT / "llm-exercises" / "exercises"
SOD = ROOT / "llm-exercises" / "solutions"

_SLUGS = ["summarize", "generate", "translate", "family", "sentiment", "load_model",
          "tokenize", "tokenize_dataset", "training_args", "build_trainer", "predict"]
NAMES = {i: f"ex{i:02d}_{s}" for i, s in enumerate(_SLUGS, 1)}

TITLE = {1: "Summarize with a pipeline", 2: "Generate text (control length + padding)",
         3: "Guide generation with a prompt", 4: "Translate with a pipeline",
         5: "Pick the right transformer family", 6: "Classify sentiment",
         7: "Load an Auto model + tokenizer", 8: "Tokenize texts (padding, truncation, tensors)",
         9: "Tokenize a whole dataset with .map", 10: "Set up TrainingArguments",
         11: "Wire up the Trainer", 12: "Use the fine-tuned model (from logits)",
         13: "One-shot prompting"}

TASK = {
 1: "Return a ≤ 40-word summary of `text` using a `summarization` pipeline.",
 2: "Return ~30 **new** tokens of continuation from `distilgpt2`, with **no** warnings.",
 3: "Return the *prompt string* that turns a review into a short apologetic reply.",
 4: "Return the English→Spanish translation of `text`.",
 5: "Map a task key (`\"sentiment\"`, `\"poem\"`, `\"translation\"`, `\"extractive-qa\"`) to `\"encoder-only\"` / `\"decoder-only\"` / `\"encoder-decoder\"`. *Offline.*",
 6: "Return `\"POSITIVE\"` / `\"NEGATIVE\"` for `text` using a fine-tuned sentiment pipeline.",
 7: "Return `(tokenizer, model)`, where the model is an `AutoModelForSequenceClassification` with 2 labels.",
 8: "Return padded, truncated (max 64) PyTorch tensors for a list of `texts`.",
 9: "Tokenize a dataset row-by-row with `.map`, processing it in batches.",
 10: "Return `TrainingArguments`: output `./out`, evaluate each epoch, 3 epochs, lr 2e-5, train/eval batch 8, weight decay 0.01. *Offline.*",
 11: "Return a `Trainer` built from the pieces (don't call `.train()`).",
 12: "Return `\"POSITIVE\"`/`\"NEGATIVE\"` for `text`, computed **from raw logits**.",
 13: "Return a prompt with **one** worked example, then the review, ending in `Sentiment:`.",
}

# Detailed walk-through of the scaffold code the learner sees.
EXPLAIN = {
 1: "The file imports `pipeline`, the one-line entry point to a pretrained model. "
    "`pipeline(task=…, model=…)` builds a ready-to-use summarizer around the DistilBART model; "
    "calling `summarizer(text, max_length=40)` runs it and returns a **list with one dict**, "
    "where `max_length=40` caps the summary length. The two blanks are the **task string** that "
    "tells `pipeline` which job to do, and the **dict key** that holds the produced summary.",
 2: "`pipeline(\"text-generation\", \"distilgpt2\")` wraps distilGPT-2; calling `gen(prompt, …)` "
    "continues your prompt, and `truncation=True` trims an over-long prompt. The two blanks are "
    "`max_new_tokens` (how many **new** tokens to generate — the modern length control; "
    "`max_length` is the older one that counts the prompt too, and mixing both triggers a "
    "warning) and `pad_token_id` (which token id the model pads with — GPT-2 has no dedicated "
    "pad token, so you reuse the tokenizer's end-of-sequence token).",
 3: "There is **no model** here — this is pure prompting. The function assembles a prompt string: "
    "it labels the review, then adds an instruction line, joined by newlines. The blank is the "
    "**instruction text** — the words that steer what the model will do.",
 4: "`pipeline(task=…, model=\"Helsinki-NLP/opus-mt-en-es\")` builds a Marian EN→ES translator; "
    "calling it returns `[{\"translation_text\": …}]`, which the code reads. The blank is the "
    "**task name**, which for translation encodes the direction.",
 5: "Pure Python, no model. `solve(task)` looks a task up in a dictionary and returns which "
    "Transformer family fits it. The four blanks are the **family strings** for each task.",
 6: "`pipeline(task=…, model=\"distilbert-base-uncased-finetuned-sst-2-english\")` wraps a "
    "DistilBERT model fine-tuned on movie-review sentiment; calling it returns "
    "`[{\"label\": …, \"score\": …}]`. The blanks are the **task name** and the **key** holding "
    "the predicted label.",
 7: "This is the control path (no pipeline). `AutoTokenizer.from_pretrained(name)` downloads the "
    "tokenizer that matches the model. The blanks are **which Auto class** loads the model (it "
    "must add a classification head) and **how many labels** that head has.",
 8: "The code calls the tokenizer on a list of texts. `padding=True` pads sequences to equal "
    "length so they form a rectangular batch; `truncation=True` cuts overly long ones. The blanks "
    "are the **tensor format** to return and the **max length** cap.",
 9: "`load_dataset(\"imdb\", split=\"train[:1%]\")` loads 1% of the train split; the inner `tok` "
    "function tokenizes the `text` column; `.map` applies it to every row. The blank controls "
    "whether `.map` passes rows **one at a time or in batches**.",
 10: "This constructs the hyperparameter bundle for training. `output_dir` is where checkpoints go; "
     "each blank is one hyperparameter — when to evaluate, how many epochs, the learning rate, the "
     "train batch size, and weight decay — with its **target value written in the comment beside "
     "it**.",
 11: "In a single call you build the `Trainer` — the object that will run the fine-tuning loop — "
     "handing it the pieces from the previous exercises. `solve()` only *constructs* it; no "
     "training happens here.",
 12: "This does by hand what the pipeline hid: it tokenizes the text into a PyTorch batch, runs the "
     "model **without tracking gradients** (`torch.no_grad()`), and reads the raw `logits` (one "
     "score per class). The blanks are the **axis** to take the argmax over (to pick the winning "
     "class) and the **string method** that upper-cases the label.",
 13: "This builds a one-shot prompt: a single worked example (a review plus its known sentiment), "
     "then the real review with a trailing `Sentiment:` for the model to complete. The blank is "
     "that **worked-example line**.",
}

# Optional per-exercise line-by-line walk-through (code line -> what it does).
LINEBYLINE = {
 1: [
  ("from transformers import pipeline",
   "imports `pipeline`, the one-line helper that wraps a pretrained model into a "
   "ready-to-call object."),
  ("def solve(text):",
   "defines the function; `text` is the long passage you want to summarize."),
  ('summarizer = pipeline(task=____, model="sshleifer/distilbart-cnn-12-6")',
   "builds a **summarization** pipeline around the DistilBART model — this downloads the "
   "model from the Hugging Face Hub the first time. The blank is the *task name*."),
  ("out = summarizer(text, max_length=40)",
   "runs the model on `text`; `max_length=40` caps the summary length. It returns a "
   "**list with a single dict**, e.g. `[{\"summary_text\": \"…\"}]`."),
  ("return out[0][____]",
   "takes the first (only) element and reads the summary string out of its dict. The blank "
   "is the *key* that holds it."),
 ],
 2: [
  ("from transformers import pipeline",
   "imports `pipeline`, the one-line helper that wraps a pretrained model."),
  ("def solve(prompt):",
   "defines the function; `prompt` is the starting text the model will continue."),
  ('gen = pipeline(task="text-generation", model="distilgpt2")',
   "builds a **text-generation** pipeline around distilGPT-2 — downloaded from the Hub the "
   "first time."),
  ("out = gen(prompt, max_new_tokens=____, pad_token_id=gen.tokenizer.____, truncation=True)",
   "runs the model on `prompt`. `max_new_tokens` (blank) caps how many **new** tokens are "
   "generated — use this rather than `max_length` (the pipeline defaults `max_new_tokens`, so "
   "setting `max_length` too would warn). `pad_token_id` (blank) sets which token pads short "
   "outputs — GPT-2 has no pad token, so you reuse its end-of-sequence token, exposed on "
   "`gen.tokenizer`; `truncation=True` trims an over-long prompt. Returns a **list with one "
   "dict**."),
  ('return out[0]["generated_text"]',
   "reads the generated string (prompt + continuation) from the first result's dict, under "
   "the `generated_text` key."),
 ],
 4: [
  ("from transformers import pipeline",
   "imports `pipeline`, the one-line helper that wraps a pretrained model."),
  ("def solve(text):",
   "defines the function; `text` is the English sentence to translate."),
  ('translator = pipeline(task=____, model="Helsinki-NLP/opus-mt-en-es")',
   "builds a **translation** pipeline around the Marian OPUS-MT English→Spanish model — "
   "downloaded from the Hub the first time. The blank is the *task name*."),
  ('return translator(text)[0]["translation_text"]',
   "runs it; the pipeline returns `[{\"translation_text\": …}]`, and this reads the translated "
   "string from the first (only) dict."),
 ],
 6: [
  ("from transformers import pipeline",
   "imports the pipeline helper."),
  ("def solve(text):",
   "defines the function; `text` is the sentence to classify."),
  ('clf = pipeline(task=____, model="distilbert-base-uncased-finetuned-sst-2-english")',
   "builds a classification pipeline around a DistilBERT model fine-tuned for sentiment "
   "(downloaded the first time). The blank is the *task name*."),
  ("return clf(text)[0][____]",
   "runs it; the pipeline returns `[{\"label\": …, \"score\": …}]`, and this reads the "
   "predicted label. The blank is the *key*."),
 ],
 7: [
  ("from transformers import AutoTokenizer, AutoModelForSequenceClassification",
   "imports the tokenizer and model **Auto classes** — the control path used to fine-tune."),
  ("def solve():",
   "no input; it returns the two objects you need."),
  ('name = "distilbert-base-uncased"',
   "the base model id — plain DistilBERT, *not* fine-tuned for any task."),
  ("tokenizer = AutoTokenizer.from_pretrained(name)",
   "downloads the tokenizer that matches that model."),
  ("model = ____.from_pretrained(name, num_labels=____)",
   "loads the model with a fresh classification head. Blanks = which Auto class to use and how "
   "many output labels."),
  ("return tokenizer, model",
   "hands both back — you need the pair to tokenize *and* to run/fine-tune the model."),
 ],
 8: [
  ("from transformers import AutoTokenizer",
   "imports the tokenizer class (used by the demo)."),
  ("def solve(tokenizer, texts):",
   "receives a ready tokenizer and a list of texts."),
  ("return tokenizer(texts, return_tensors=____, padding=True, truncation=True, max_length=____)",
   "tokenizes the batch: `padding=True` pads all to equal length (a rectangular batch), "
   "`truncation=True` cuts long ones. Blanks = the tensor format and the length cap."),
 ],
 9: [
  ("from transformers import AutoTokenizer",
   "the tokenizer class (used by the demo)."),
  ("from datasets import load_dataset",
   "the loader for ready-made datasets."),
  ("def solve(tokenizer):",
   "receives a tokenizer to apply."),
  ('data = load_dataset("imdb", split="train[:1%]")',
   "loads 1% of IMDB's train split — a small set of labelled movie reviews."),
  ("def tok(batch): ...",
   "a helper that tokenizes the `text` column of a batch of rows."),
  ("return data.map(tok, batched=____)",
   "applies `tok` across the whole dataset. Blank = process rows **in batches** (much faster)."),
 ],
 10: [
  ("from transformers import TrainingArguments",
   "imports the hyperparameter container."),
  ("def solve():",
   "returns the configuration object (no training happens here)."),
  ("return TrainingArguments(output_dir=\"./out\", eval_strategy=____, num_train_epochs=____, …)",
   "builds the training config; `output_dir` is where checkpoints go and each blank is one "
   "hyperparameter (eval schedule, epochs, learning rate, train batch size, weight decay) — "
   "the target value is written in the comment beside each blank."),
 ],
 12: [
  ("import torch",
   "PyTorch — needed to read tensors and take the argmax."),
  ("from transformers import AutoTokenizer, AutoModelForSequenceClassification",
   "the Auto classes to load the model + tokenizer directly (no pipeline)."),
  ("def solve(text):",
   "`text` is the sentence to classify."),
  ('name = "distilbert-base-uncased-finetuned-sst-2-english"',
   "the sentiment-fine-tuned model (same one ex5's pipeline used)."),
  ("tok = ...; model = ...",
   "load the matching tokenizer and model."),
  ('inp = tok(text, return_tensors="pt", padding=True, truncation=True)',
   "tokenizes the text into a PyTorch batch."),
  ("with torch.no_grad(): logits = model(**inp).logits",
   "runs the model **without tracking gradients** (inference); `logits` = one raw score per "
   "class."),
  ("pred = int(torch.argmax(logits, dim=____))",
   "picks the highest-scoring class. Blank = the class axis to reduce over."),
  ("return model.config.id2label[pred].____()",
   "maps the class id to its label name and normalises the case. Blank = the string method."),
 ],
 13: [
  ("def solve(review):",
   "no model — it builds a *prompt* string."),
  ('example = ____   # "Review: \'…\' Sentiment: positive"',
   "one complete worked example: a review followed by its known sentiment. Blank = that line."),
  ("return f\"{example}\\nReview: '{review}' Sentiment:\"",
   "puts the example first, then the real review ending in `Sentiment:` for the model to "
   "complete — the essence of *one-shot* prompting."),
 ],
}

# Optional per-exercise note on why that specific model fits the task.
MODEL_NOTE = {
 1: "Summarization is a *sequence-to-sequence* task — read a whole document, then write a "
    "shorter one — so it needs an **encoder-decoder** Transformer (see §3). "
    "`sshleifer/distilbart-cnn-12-6` is a **distilled BART** (a smaller, faster BART) fine-tuned "
    "on the CNN/DailyMail *news* dataset; the `12-6` are its 12 encoder and 6 decoder layers. "
    "That fine-tuning is exactly why it condenses text into fluent, news-style summaries out of "
    "the box — a plain GPT-style model would just keep writing, not summarize.",
 2: "Text generation means predicting the next token over and over — which is what a "
    "**decoder-only** Transformer does (see §3). `distilgpt2` is a **distilled GPT-2** "
    "(~82M parameters, a lighter/faster GPT-2) small enough to download and run on a CPU. It is "
    "*not* fine-tuned for any task, so it simply **continues** whatever text you give it — which "
    "is precisely what lets you see raw next-token generation.",
 4: "Translation is a *sequence-to-sequence* task — read a full sentence in one language, then "
    "write it in another — so, like summarization, it uses an **encoder-decoder** Transformer "
    "(see §3). `Helsinki-NLP/opus-mt-en-es` is a **MarianMT** model from the OPUS project, "
    "trained specifically on English→Spanish parallel text; its name encodes exactly that "
    "(`opus-mt-en-es` = OPUS machine translation, en→es). Being a small model dedicated to one "
    "language pair, it translates accurately and cheaply — a big general LLM could translate too, "
    "but this is the focused, efficient choice.",
 6: "`distilbert-base-uncased-finetuned-sst-2-english` is an **encoder-only** DistilBERT (§3) "
    "that has **already been fine-tuned** on SST-2 (a movie-review sentiment dataset) to output "
    "POSITIVE/NEGATIVE. Because the fine-tuning is done, the pipeline classifies out of the box; "
    "DistilBERT itself is a distilled (smaller, faster) BERT.",
 7: "`distilbert-base-uncased` is the **plain**, *not*-fine-tuned DistilBERT (encoder-only). "
    "`AutoModelForSequenceClassification` bolts a **fresh, untrained** classification head on "
    "top — so its predictions are random until you fine-tune it. That's the whole point: this is "
    "the *starting point for training*, in contrast to ex5, which loaded the already-fine-tuned "
    "version.",
 12: "Same model as ex5 — the SST-2 fine-tuned DistilBERT — but loaded via **Auto classes** "
     "instead of a pipeline, so you read the raw logits yourself. Because it's fine-tuned, the "
     "`argmax` of its logits is a meaningful POSITIVE/NEGATIVE (a plain base model would give "
     "noise).",
}

# Optional per-exercise note on how the model turns text into a prediction.
HOWITWORKS = {
 7: "DistilBERT turns the text into **contextual embeddings** — one vector per token. The vector "
    "of the special `[CLS]` token (the first one) is used as the **summary of the whole "
    "sentence**. The **classification head** (a small linear layer — in DistilBERT preceded by a "
    "pre-classifier + ReLU) maps that summary vector to one **logit** per class: raw, unbounded "
    "scores. To read them as probabilities you apply **softmax**; but to simply pick the "
    "predicted class you take the `argmax` of the logits directly — no softmax needed (that's "
    "what ex11 does). One caveat specific to this exercise: the head is **freshly added and "
    "untrained**, so its logits are essentially random until you fine-tune the model (contrast "
    "with ex5, whose head is already trained).",
}

# Optional per-exercise note explaining the tokenizer's output.
IONOTE = {
 8: "The tokenizer returns a small dictionary of tensors:\n\n"
    "- **`input_ids`** — the text turned into numbers: each token maps to an integer id from "
    "the model's vocabulary. For DistilBERT, `101` and `102` are the special `[CLS]`/`[SEP]` "
    "markers that wrap every sentence, and `0` is `[PAD]`.\n"
    "- **`attention_mask`** — a parallel array, same shape, with **1 = real token** and "
    "**0 = padding**. *How it protects the result:* inside the Transformer, attention makes each "
    "token look at the others through weights produced by a **softmax**. At every position where "
    "the mask is 0, the attention score is set to **−∞ before the softmax**, and since "
    "`e^(−∞) = 0` those slots get weight **0** — so padding contributes nothing and real tokens "
    "attend only to real tokens. That's why you can pad as much as you like without changing the "
    "output.\n"
    "- **Not the same as the causal mask** (§3): `attention_mask` says *which tokens are real*; "
    "the causal mask (decoders only) says *each token may see only earlier ones*. The model adds "
    "the causal one itself — the tokenizer gives you the padding one.\n"
    "- You always pass both to the model together: `model(**enc)` (i.e. "
    "`model(input_ids=…, attention_mask=…)`).",
}

# Optional per-exercise explanation of the demo output (shown in the SOLUTIONS doc).
SOL_OUTPUT = {
 9: '''Running `python solutions/ex08_tokenize_dataset.py` prints something like:

```
columns: ['text', 'label', 'input_ids', 'attention_mask']  (input_ids + attention_mask are new)
rows:    250
--- one tokenized example ---
label         : 0
text          : I rented I AM CURIOUS-YELLOW from my video store because of all the controversy that surro ...
input_ids     : [101, 1045, 12524, 1045, 2572, 8025, 1011, 3756, ...] ...  (length 128 )
attention_mask: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] ...
decoded back  : [CLS] i rented i am curious - yellow from my video store because of all the
```

Line by line:

- **columns** — the dataset kept `text` and `label` and gained `input_ids` + `attention_mask` (what `.map` added).
- **rows: 250** — 1% of IMDB's 25,000-example train split.
- **label: 0** — IMDB uses `0` = negative, `1` = positive. **Heads-up:** all 250 rows here are `0`, because the train split is **ordered by label** (its first half is negative); `train[:1%]` therefore gives an all-negative subset — fine for demoing tokenization, but you'd have to **shuffle** before actually training on it.
- **text** — the raw review: the human-readable input.
- **input_ids … (length 128)** — the review as vocabulary ids; `101` is `[CLS]` (the start marker). The length is **128** because that's the `max_length` cap: this review was long, so it was truncated/filled to 128 tokens.
- **attention_mask** — all `1`s here: each of those positions is a **real token** (no padding, because the review reached the 128 cap). A shorter review would show trailing `0`s.
- **decoded back** — the first 16 ids turned back into text: `[CLS] i rented i am curious - yellow …`. Notice the special `[CLS]` marker, everything **lower-cased** (DistilBERT is *uncased*), and `CURIOUS-YELLOW` becoming `curious - yellow` (the tokenizer splits on punctuation/subwords). This round-trip confirms `input_ids` really encode the text.''',
}

# Full bespoke write-up for an exercise (replaces the generic blocks when present).
FULLNOTE = {
 12: '''**The key idea.** The goal isn't to learn `torch.argmax()` — it's to understand that a
classification model **doesn't return a label**; it returns **logits** (raw numeric scores), and
*you* have to turn those into the final class. This exercise does by hand what `pipeline()` was
doing for you automatically.

**Where we are.** This is the last step of *inference*:

```
Text  ->  Tokenizer  ->  Model  ->  Logits  ->  pick the best class  ->  "POSITIVE"
```

**What are logits?** The model doesn't hand back `POSITIVE`; it returns a vector of scores, e.g.

```
tensor([[-1.25, 3.82]])
```

one score per class (index `0` -> NEGATIVE, index `1` -> POSITIVE). These are **not** probabilities
— they're raw scores. (You'd apply *softmax* to turn them into probabilities, but you don't need
to just to pick the winner.)

**How we get the prediction.** `torch.argmax(logits, dim=1)` returns the *position* of the
largest value. For `[-1.25, 3.82]` that is `1`, because `3.82` is the highest.

**Why `dim=1`?** Logits have shape `[batch, classes]` — one row per sentence, one column per
class. Reducing over `dim=1` (the class axis) picks the top class **for each sentence** in the
batch.

**How we get the label.** The model carries a dictionary `model.config.id2label`, e.g.
`{0: "NEGATIVE", 1: "POSITIVE"}`, so `model.config.id2label[pred]` turns the class id into a
human-readable label.

**Why `torch.no_grad()`?** At inference we don't want to compute gradients or update weights — we
only read a prediction. Wrapping the forward pass in `with torch.no_grad():` makes it faster and
use less memory.

**Why the model matters.** This is the same SST-2 fine-tuned DistilBERT as ex5. *Because* it's
fine-tuned, its logits are meaningful and `argmax` gives a real POSITIVE/NEGATIVE; the untrained
head from ex6 would give noise.

**The full flow:**

```
Text
  |
  v
Tokenizer  ->  input_ids
  |
  v
fine-tuned Model
  |
  v
Logits            e.g. [-1.25, 3.82]
  |
  v   argmax()  ->  1
id2label[1]
  |
  v
"POSITIVE"
```

**What you really learn.** This exercise reveals what was hidden inside `pipeline()`: a
classification model returns a vector of **logits**, and making a prediction means selecting the
highest-scoring class (`argmax`) and mapping its id to a label (`id2label`). That is what actually
happens during inference with a Transformer.''',
}

# Optional per-exercise "big picture" note (what the exercise is really for).
GOALNOTE = {
 9: "The goal of this exercise isn't to train the model — it's to **prepare the data**. The raw "
    "dataset held only `text` and its `label`; running it through `.map` with the tokenizer "
    "produces a new dataset that keeps those and adds `input_ids` and `attention_mask` — the "
    "format Transformers expect for fine-tuning. In effect you've turned a **human-readable** "
    "dataset into one a **neural network can process**: `input_ids` and `attention_mask` are the "
    "model's **inputs**, `label` is the **target** it must learn to predict, and `text` just "
    "rides along. (One technicality: right after `.map` the ids are still Python lists; the "
    "Trainer / data collator turns them into tensors at training time.)",
 10: "This exercise doesn't train anything — it **defines the rules of training**. "
     "`TrainingArguments` is a configuration object the `Trainer` reads later to know how many "
     "passes to make over the data (**epochs**), how big each weight update is (**learning "
     "rate**), how many examples to process at once (**batch size**), how much to regularise "
     "(**weight decay**), when to **evaluate**, and where to **save checkpoints** "
     "(`output_dir`). It's the *flight plan* the fine-tuning run will follow — it has dozens of "
     "options, and here you set the essential ones.",
 11: "This is the moment **every piece you built connects into one pipeline**. There's no need "
     "to wire the arguments one by one to learn them — `model` (ex6), `TrainingArguments` (ex9), "
     "the train/eval datasets (ex8) and the `tokenizer` (ex6/7) were each covered already. The "
     "new idea is that the **`Trainer` orchestrates the whole fine-tuning**: hand it those pieces "
     "and it knows how to run the training loop.\n\n"
     "**Is the model being trained in this exercise? It depends what you run:**\n\n"
     "- **`solve()`** — the part you complete — only **builds** the `Trainer` object. **No "
     "training.**\n"
     "- **Running the file** (`python exercises/ex10_build_trainer.py`) builds it *and* then "
     "calls `trainer.train()` on a tiny dataset for two steps — **yes, a real mini-train** you "
     "can watch (a loss is printed).\n"
     "- **`python check.py 10`** only verifies the wiring. **No training.**\n\n"
     "So the *exercise itself* just assembles the Trainer; the bundled *demo* adds a two-step "
     "train so the loop isn't abstract. And what `trainer.train()` actually does, each step, is: "
     "pull a **batch** from the `train_dataset` → run it **through the model** → compute the "
     "**loss** (how wrong it is) → **backpropagate** to get the gradients (which way each weight "
     "should move) → **update the weights** a little (step size = the learning rate) → "
     "**evaluate** when `eval_strategy` says to → **save checkpoints** to `output_dir`.",
}

# Optional per-exercise deep-dive on key hyperparameters.
HYPERPARAMS = {
 10: "Three settings are worth understanding, not just filling in:\n\n"
     "- **`num_train_epochs` (epochs)** — one epoch is one full pass over the whole training "
     "set, so `3` means the model sees every example three times. Too few and it *underfits* "
     "(hasn't learned enough); too many and it starts to *memorise* the training data "
     "(**overfits**).\n"
     "- **`learning_rate`** — the **size of each step** when the weights are updated. Big steps "
     "learn fast but can overshoot and diverge; tiny steps are stable but slow. `2e-5` "
     "(0.00002) is a deliberately small value typical of fine-tuning: the pretrained weights are "
     "already good, so you only want to *nudge* them, not overwrite them.\n"
     "- **`weight_decay`** — a **regularisation** term that, each step, gently pulls every weight "
     "toward zero (it penalises large weights). The penalty grows with the **square** of each "
     "weight (L2), so a few big weights cost far more than many small ones — e.g. two weights of "
     "1 cost `1+1 = 2`, but one weight of 2 costs `2×2 = 4`. The model therefore prefers to "
     "**spread** the signal across many features rather than lean hard on one, which **reduces "
     "overfitting**. It's a lever, though: too strong and the model is over-constrained and "
     "*underfits*. `0.01` is a mild, standard value. (Technical note: this is L2 regularisation; "
     "the `Trainer`'s AdamW optimiser applies it as *decoupled* weight decay — directly on the "
     "weights — but the intuition is the same.)",
}

# Optional per-exercise note on batched dataset tokenization.
MAPNOTE = {
 9: "`data.map(tok, …)` applies the tokenizer across the **whole dataset** instead of one "
    "sentence at a time, and returns a **new dataset** that keeps the original columns "
    "(`text`, `label`) and **adds** `input_ids` and `attention_mask` — the columns the model "
    "consumes during fine-tuning. Three details worth knowing:\n\n"
    "- **Batch size:** processing *in batches* doesn't mean *all at once* — by default `tok` "
    "receives **1,000 rows** per call.\n"
    "- **Where the speed comes from:** the big win is that **fast (Rust) tokenizers** process a "
    "whole batch in parallel; with a slow (pure-Python) tokenizer the gain is much smaller.\n"
    "- **A padding gotcha:** `padding=True` here pads **within each batch**, so different batches "
    "can end up with different lengths. For training you often defer padding to a *data "
    "collator* (dynamic per-batch padding) or use `padding=\"max_length\"` for a uniform size.",
}

# Per-exercise explanation of each blank that was filled (shown in the SOLUTIONS doc).
BLANKS = {
 1: [
  ('task="summarization"',
   "the pipeline **task name**. `pipeline` looks this up in its task registry to know which "
   "kind of model and pre/post-processing to set up; `\"summarization\"` selects the "
   "summarization pipeline (a sequence-to-sequence job)."),
  ('out[0]["summary_text"]',
   "the **output key**. A summarization pipeline returns a one-element list of dicts, e.g. "
   "`[{\"summary_text\": \"…\"}]`; `out[0]` is that dict and `[\"summary_text\"]` reads the "
   "summary string out of it."),
 ],
 2: [
  ("max_new_tokens=30",
   "how many **new** tokens to generate (~30). We use `max_new_tokens`, **not** `max_length`, "
   "because the text-generation pipeline already sets a default `max_new_tokens`; also passing "
   "`max_length` makes the two conflict (a warning) and the length cap is ignored. "
   "`max_new_tokens` counts only the generated tokens, not the prompt."),
  ("pad_token_id=gen.tokenizer.eos_token_id",
   "the **padding token id** — worth unpacking:\n"
   "    - **What padding is.** The model often processes several sequences at once (a *batch*), "
   "but they have different lengths. To line them up in one rectangular array, the short ones "
   "are filled up to the longest with a *filler* token — the **pad token**. The model ignores "
   "those filler positions via the *attention mask*, so `pad_token_id` just says *which id to "
   "use as filler*.\n"
   "    - **GPT-2's problem.** GPT-2 was trained on continuous text with no dedicated pad token, "
   "so `tokenizer.pad_token_id` is `None`. When generation needs a pad id and finds none, it "
   "prints the “no padding token is set” warning.\n"
   "    - **The fix.** GPT-2 *does* have an *end-of-sequence* token, `<|endoftext|>` (id "
   "`50256`), exposed as `eos_token_id`. Setting `pad_token_id=gen.tokenizer.eos_token_id` "
   "reuses that id as the filler. It's safe because padding always comes **after** the real "
   "text (where “end of text” fits) and is masked out anyway — so it changes nothing in the "
   "output and simply silences the warning.\n"
   "    - **Reading the expression:** `gen` = the pipeline, `gen.tokenizer` = its tokenizer, "
   "`.eos_token_id` = the integer `50256`. So the line means “use 50256 as the pad id.”"),
 ],
 4: [
  ('task="translation_en_to_es"',
   "the pipeline **task name**. Translation tasks are named `translation_<src>_to_<tgt>`, so "
   "English→Spanish is `translation_en_to_es`. It tells `pipeline` this is a translation job "
   "and in which direction; it agrees with the EN→ES model already given, and the result comes "
   "back under the `translation_text` key."),
 ],
 5: [
  ('"sentiment": "encoder-only"',
   "sentiment analysis reads the whole text and returns **one label** — pure *understanding*, "
   "nothing generated — so a bidirectional **encoder** (BERT-style) is the fit."),
  ('"poem": "decoder-only"',
   "writing a poem is open-ended *generation*, produced one token after another, which is "
   "exactly what an autoregressive **decoder** (GPT-style) does."),
  ('"translation": "encoder-decoder"',
   "translation is *sequence-to-sequence*: read the full source sentence, then write the "
   "target. The **encoder** understands the input and the **decoder** generates the output "
   "(attending back to the input via cross-attention) — e.g. Marian or T5."),
  ('"extractive-qa": "encoder-only"',
   "extractive QA picks the answer **span** out of a given context (it predicts the start and "
   "end positions), so it *understands* rather than generates — again a bidirectional "
   "**encoder** (e.g. BERT fine-tuned on SQuAD)."),
 ],
 6: [
  ('task="sentiment-analysis"',
   "the **task name** — an alias of text-classification specialised for sentiment; it tells "
   "`pipeline` to build a classification pipeline."),
  ('clf(text)[0]["label"]',
   "the pipeline returns `[{\"label\": …, \"score\": …}]`; `[0][\"label\"]` reads the predicted "
   "class (POSITIVE/NEGATIVE)."),
 ],
 7: [
  ("____ = AutoModelForSequenceClassification",
   "of the two imported classes, this is the one that adds a **classification head**; plain "
   "`AutoModel` would output only embeddings, with no way to predict a label."),
  ("num_labels=2",
   "two output classes (POSITIVE/NEGATIVE) — this sizes the classification head."),
 ],
 8: [
  ('return_tensors="pt"',
   "return **PyTorch** tensors (`\"pt\"`); `\"tf\"`/`\"np\"` would give TensorFlow/NumPy instead."),
  ("max_length=64",
   "cap each sequence at 64 tokens; combined with `truncation=True`, longer inputs are cut."),
 ],
 9: [
  ("batched=True",
   "hand many rows to `tok` at once instead of one at a time — far faster, and what a fast "
   "tokenizer is built for."),
 ],
 10: [
  ('eval_strategy="epoch"',
   "run evaluation at the end of **each epoch**."),
  ("num_train_epochs=3",
   "three full passes over the training data."),
  ("learning_rate=2e-5",
   "the step size — `2e-5` is a typical value for fine-tuning Transformers."),
  ("per_device_train_batch_size=8",
   "8 training examples per step (per device)."),
  ("weight_decay=0.01",
   "light regularisation that discourages large weights, curbing overfitting."),
 ],
 11: [
  ("model=model, args=args, train_dataset=train_ds, eval_dataset=eval_ds",
   "each `Trainer` parameter takes the same-named argument that `solve` received; the Trainer "
   "bundles the model, the config, the two datasets and the tokenizer, and its `.train()` runs "
   "the loop (the file's demo actually fires two steps)."),
 ],
 12: [
  ("dim=1",
   "logits have shape `[batch, num_labels]`, so taking the argmax over **axis 1** picks the "
   "winning class for each example."),
  (".upper()",
   "`id2label[pred]` gives the label name; `.upper()` normalises it to POSITIVE/NEGATIVE to "
   "match what the task expects."),
 ],
 13: [
  ('example = "Review: \'The delivery was quick.\' Sentiment: positive"',
   "one complete worked example — a review followed by its known sentiment — that shows the "
   "model the exact format. Placed before the real review, it is the single \"shot\" the model "
   "imitates (zero-shot would give none; few-shot several)."),
 ],
}

HINT = {
 1: "The task is named after what it does. The result is a one-element list of dicts, and the "
    "field name tells you which one holds the summary.",
 2: "The task says how many *new* tokens. For padding, remember GPT-2 has no pad token, so it "
    "reuses its *end-of-sequence* token — look for that id on the tokenizer.",
 3: "It just has to be a string that tells the model to reply — phrase it as you would instruct a "
    "person.",
 4: "Translation task names encode the direction as `translation_<src>_to_<tgt>`; fill in the two "
    "language codes.",
 5: "Sort each task by what it needs: to *understand* the input, to *generate* free text, or to "
    "*transform* one sequence into another.",
 6: "The task name is the common two-word phrase for judging sentiment; the result dict reports "
    "its prediction under an obvious key.",
 7: "Of the two imported classes, one adds a classification head — its name says so. How many "
    "classes does POSITIVE-vs-NEGATIVE have?",
 8: "PyTorch tensors have a two-letter code; the length cap is the number named in the task.",
 9: "You want `.map` to process rows in batches rather than one at a time.",
 10: "Each value you need is written in the comment next to its blank.",
 11: "Each `Trainer` parameter takes the argument of the same name that `solve` received.",
 12: "Logits are shaped `[batch, classes]`, so reduce over the class axis; then match the "
     "capitalisation the task expects.",
 13: "Put one complete example — a review followed by its sentiment — before the real one.",
}

# (number, title, theory-prose, [exercise numbers])
SECTIONS = [
 (2, "Using pre-trained models with pipelines", '''A **large language model (LLM)** is a deep-learning model — almost always a
**Transformer** — with a huge number of parameters, trained on massive amounts of text.
You rarely build one; you *use* one that already exists. Hugging Face's `transformers`
library makes that a one-liner through the **`pipeline()`** function: you name a *task* and
(optionally) a *model*, and it hands back a callable that does the whole job — tokenizing the
input, running the model, and decoding the output.

Tasks fall into two broad families. **Understanding** tasks read text and return a structured
result — a label or a span: sentiment analysis, classification, extractive question-answering.
**Generation** tasks produce new text: text generation, summarization, translation.

For generation you usually set a few knobs. `max_length` caps how long the output can be;
`truncation=True` trims over-long inputs; and `pad_token_id` tells the model which token to
pad with — setting it to `tokenizer.eos_token_id` (the end-of-sequence token) silences the
common padding warning. Beyond parameters, the strongest lever is the **prompt** itself: the
words you feed in steer what comes out. **Translation** is just another task — either name it
explicitly (`translation_en_to_es`) or pick a dedicated model such as the
`Helsinki-NLP/opus-mt-*` family.''', [1, 2, 3, 4]),

 (3, "The Transformer, in three shapes", '''Every modern language model is a **Transformer**, built from two kinds of block: an
**encoder** (bidirectional attention — each token sees the whole input, so it *understands*) and
a **decoder** (causal attention — each token sees only what came before, which is what lets it
*generate*). Keeping one or both gives three model shapes, each suited to different tasks. The
figure below is the whole picture at a glance.

![The Transformer in three shapes — encoder vs decoder attention and the encoder-only, decoder-only and encoder-decoder families](assets/transformer-three-shapes.png)''', [5, 6]),

 (4, "From pipelines to Auto classes: datasets & tokenization", '''`pipeline()` is convenient but hides everything. To fine-tune — or simply to control the
pieces — you drop down to the **Auto classes**: `AutoTokenizer` for the tokenizer and
`AutoModelForSequenceClassification` (or `AutoModel`, …) for the model, each loaded with
`.from_pretrained(name)`.

It helps to picture the **LLM lifecycle**: **pre-training** on broad data teaches general
language patterns; then optional **fine-tuning** on your own domain-specific data adapts the
model to a task. That data usually comes from a dataset — `datasets.load_dataset(...)` — which
you must turn into numbers.

That conversion is **tokenization**. A tokenizer splits text into tokens and maps them to
`input_ids` (plus an `attention_mask`). The knobs you'll use constantly: `padding` (pad short
sequences so a batch is rectangular), `truncation` + `max_length` (cap long ones), and
`return_tensors="pt"` (return PyTorch tensors). Modern tokenizers are **subword**: rare words
split into meaningful pieces, so nothing is ever truly "out of vocabulary". To tokenize a
whole dataset efficiently, wrap the tokenizer in a function and apply it across the whole
dataset, in batches, with `dataset.map(fn, ...)`.''', [7, 8, 9]),

 (5, "Fine-tuning through training", '''With a model and a tokenized dataset in hand, fine-tuning comes down to three objects.
**`TrainingArguments`** holds the hyperparameters — where to save (`output_dir`), when to
evaluate (`eval_strategy="epoch"`), how long (`num_train_epochs`), how fast
(`learning_rate`), the batch sizes, and regularization (`weight_decay`). **`Trainer`** ties
everything together — the model, those args, the train and eval datasets, and the tokenizer —
and `trainer.train()` runs the loop.

Once trained, using the model directly means doing by hand what the pipeline did for you:
tokenize the text, run it under `torch.no_grad()` (no gradients needed for inference), read the
raw **logits**, take the `argmax` for the predicted class id, and map that id to a label via
`model.config.id2label`. Finally, `model.save_pretrained(dir)` and
`tokenizer.save_pretrained(dir)` persist your work; `from_pretrained(dir)` loads it back.

> **Heads-up:** in recent `transformers`, `TrainingArguments` and `Trainer` need the
> **`accelerate`** package (it's in `requirements.txt`). If you see *"the Trainer ... requires
> accelerate"*, run `pip install -r requirements.txt` (or `pip install "accelerate>=1.1.0"`).''',
  [10, 11, 12]),

 (6, "Fine-tuning approaches & N-shot prompting", '''Full training isn't the only option. **Full fine-tuning** updates every weight — most
powerful, most expensive. **Partial fine-tuning** freezes most layers and trains only a few —
cheaper and less prone to overfitting. **Transfer learning** is the umbrella idea: take a
model trained on one task and adapt it to a related one.

Often you don't need to train at all. **N-shot prompting** teaches the model *inside the
prompt*, by example: **zero-shot** gives no example (just the instruction), **one-shot** gives
a single worked example, and **few-shot** gives several. More examples generally sharpen the
output format and accuracy — at the cost of a longer prompt.''', [13]),
]


# --- renumber: exercises 3 (reply_prompt) and 13 (oneshot) were removed; close the gaps ---
_REMAP = {1: 1, 2: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 12: 11}

def _renum(d):
    return {_REMAP[o]: v for o, v in d.items() if o in _REMAP}

TITLE, TASK, EXPLAIN, HINT = _renum(TITLE), _renum(TASK), _renum(EXPLAIN), _renum(HINT)
LINEBYLINE, MODEL_NOTE, BLANKS = _renum(LINEBYLINE), _renum(MODEL_NOTE), _renum(BLANKS)
HOWITWORKS = _renum(HOWITWORKS)
IONOTE = _renum(IONOTE)
MAPNOTE = _renum(MAPNOTE)
GOALNOTE = _renum(GOALNOTE)
HYPERPARAMS = _renum(HYPERPARAMS)
FULLNOTE = _renum(FULLNOTE)
SOL_OUTPUT = _renum(SOL_OUTPUT)
SECTIONS = [(num, title, theory, [_REMAP[o] for o in exs if o in _REMAP])
            for (num, title, theory, exs) in SECTIONS]
OFFLINE = {4, 9}  # family, training_args (post-renumber)


def solve_block(path):
    """Top-level imports + the solve() function (drop docstring, SAMPLE, __main__)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    imp, starts = [], [i for i, l in enumerate(lines) if l.startswith(("import ", "from "))]
    if starts:
        i = starts[0]
        while i < len(lines) and lines[i].strip():
            imp.append(lines[i]); i += 1
    s = next(i for i, l in enumerate(lines) if l.startswith("def solve"))
    e = next((i for i, l in enumerate(lines) if l.startswith("if __name__")), len(lines))
    body = lines[s:e]
    while body and body[-1].strip() == "":
        body.pop()
    return ("\n".join(imp) + "\n\n\n" if imp else "") + "\n".join(body)


GUIDE_HEADER = '''# Introduction to LLMs in Python — Personal Study Guide

> **What this is.** A study companion for your own learning, built from the *skills* in the
> DataCamp course you downloaded. Each section **explains the theory**, then gives you
> **original exercises**: for each one you get the task, a walk-through of the code you're
> handed, a hint, and the file to complete. **Solutions are in a separate document**
> (`study-guide-solutions.pdf`) — try each exercise first. Personal use only.

The runnable workbook is in [`llm-exercises/`](llm-exercises/): **one self-contained file per
exercise** under `exercises/` (imports at the top, `solve` to complete), answers under
`solutions/`, and `check.py` (verifier).

---

## 1 · Setup & how to verify it works

```bash
cd llm-exercises
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

**Confirm your environment before starting** (exercises 4 and 9 need no internet):

```bash
python check.py 4 9                 # expect two TODO lines — harness runs, work not done
python check.py --solutions 4 9     # expect: PASS  PASS  — reference solutions run
```

Then work through `exercises/` and re-run the verifier:

```bash
python check.py                     # checks all 11
python check.py 1 2 6               # only some
python check.py --show 4 11         # also PRINT what each solve() returned
python exercises/ex01_summarize.py  # or run a single file standalone (prints its output)
```

Tip: `check.py` shows only PASS/FAIL by default. Add **`--show`** to also print each
`solve()`'s return value, or run a file directly (`python solutions/ex01_summarize.py`) to
see its output.

Each exercise reports one status:

| Status | Meaning |
|---|---|
| **PASS** | Your `solve()` returned the right thing. |
| **TODO** | Not implemented yet (an `____` blank is still there). |
| **FAIL** | It ran but returned something wrong (the message says why). |
| **SKIP** | A model/dataset couldn't download (no internet), or deps missing. |
| **ERR**  | Unexpected error (message shown). |

Exercises other than 4 and 9 download a **small** model from the Hugging Face Hub on first
use (internet + a few hundred MB). Everything runs on CPU except real training.

To complete an exercise, open its file, replace each `____` blank (the comment above each line
says what goes there), and re-run the verifier.

For a text exercise the verifier runs the file's own `SAMPLE`, so editing `SAMPLE` changes what
you see (and `--show` prints *your* input's result); `PASS` means the result is **valid** — a
real POSITIVE/NEGATIVE label, a non-empty translation, and so on — not that some fixed sentence
matched.
'''

REFERENCES = '''
---

## 7 · Where to look things up

**Start here (official, free):**

- **Hugging Face LLM/NLP Course** — the best structured, hands-on intro: <https://huggingface.co/learn>
- **Transformers docs (home)** — <https://huggingface.co/docs/transformers>

**API reference for what you used in these exercises:**

- `pipeline()` and the full task list — <https://huggingface.co/docs/transformers/main_classes/pipelines>
- **Auto classes** (`AutoTokenizer`, `AutoModelFor…`) — <https://huggingface.co/docs/transformers/model_doc/auto>
- **Tokenizer** (padding / truncation / `return_tensors`) — <https://huggingface.co/docs/transformers/main_classes/tokenizer>
- **Trainer & TrainingArguments** — <https://huggingface.co/docs/transformers/main_classes/trainer>
- **Datasets** (`load_dataset`, `.map`) — <https://huggingface.co/docs/datasets>
- **Task guides** (summarization, translation, classification, QA…) — <https://huggingface.co/docs/transformers/tasks/summarization>

**Finding a model:**

- **The Model Hub** — filter by task on the left: <https://huggingface.co/models>
- **Read the model card** — what architecture it is, its intended task and languages, and the
  exact `model=` id to copy.

**Background / the "why":**

- PyTorch docs — <https://pytorch.org/docs/stable/index.html>
- Papers: *Attention Is All You Need* (Transformer, 2017), *BERT* (2018), *GPT-2* (2019) —
  searchable on <https://arxiv.org>

**A skill worth practising, not just bookmarking:**

- In Python, `help(pipeline)` (or `TrainingArguments?` in a notebook) prints the docstring for
  any object — the fastest reference of all.
- Every argument you pass (`max_length`, `eval_strategy`, …) has a one-line explanation in the
  class's docstring / API page — look it up there instead of guessing.
'''

GUIDE_FOOTER = '''
---

## 8 · Self-check

You can now: run a task with `pipeline()`; control generation length/padding; translate;
tell encoder-only / decoder-only / encoder-decoder apart and verify in code; move from
`pipeline` to Auto classes; tokenize (with padding/truncation) and `.map` a dataset; set up
`TrainingArguments` + `Trainer`; run inference from logits; and prompt zero/one/few-shot.
That's the whole arc of the two chapters.
'''

SOL_HEADER = '''# Introduction to LLMs in Python — Solutions

> Reference answers for the exercises in `study-guide.pdf`. **Try each exercise first** — the
> learning is in the attempt. These are also in `llm-exercises/solutions/`, verified by
> `python check.py --solutions`.
'''

# ---- build the study guide ----
guide = [GUIDE_HEADER]
for num, title, theory, exs in SECTIONS:
    guide.append(f"\n---\n\n## {num} · {title}\n")
    guide.append(theory + "\n")
    if exs:
        guide.append("### Exercises\n")
    for n in exs:
        off = "  ·  *offline*" if n in OFFLINE else ""
        guide.append(f"#### Exercise {n} · {TITLE[n]}{off}\n")
        guide.append(f"**Task.** {TASK[n]}\n")
        if n in FULLNOTE:
            guide.append(FULLNOTE[n] + "\n")
        else:
            guide.append(f"**What the code does.** {EXPLAIN[n]}\n")
            if n in GOALNOTE:
                guide.append(f"**The point.** {GOALNOTE[n]}\n")
            if n in LINEBYLINE:
                guide.append("**Line by line:**\n")
                for code, why in LINEBYLINE[n]:
                    guide.append(f"- `{code}` — {why}")
                guide.append("")
            if n in MODEL_NOTE:
                guide.append(f"**Why this model.** {MODEL_NOTE[n]}\n")
            if n in HOWITWORKS:
                guide.append(f"**How it classifies.** {HOWITWORKS[n]}\n")
            if n in IONOTE:
                guide.append(f"**`input_ids` & `attention_mask`.** {IONOTE[n]}\n")
            if n in MAPNOTE:
                guide.append(f"**Batched tokenization with `.map`.** {MAPNOTE[n]}\n")
            if n in HYPERPARAMS:
                guide.append(f"**Key hyperparameters.** {HYPERPARAMS[n]}\n")
        guide.append(f"**Hint.** {HINT[n]}\n")
        guide.append(f"Complete this in `exercises/{NAMES[n]}.py`:\n")
        guide.append("```python\n" + solve_block(EXD / f"{NAMES[n]}.py") + "\n```\n")
guide.append(REFERENCES)
guide.append(GUIDE_FOOTER)
(ROOT / "study-guide.md").write_text("\n".join(guide), encoding="utf-8")

# ---- build the solutions doc ----
sol = [SOL_HEADER]
for num, title, theory, exs in SECTIONS:
    if not exs:            # theory-only section (no exercises) — skip in the answers doc
        continue
    sol.append(f"\n---\n\n## {num} · {title}\n")
    for n in exs:
        sol.append(f"#### Exercise {n} · {TITLE[n]}\n")
        sol.append(f"**Task.** {TASK[n]}\n")
        sol.append(f"**Answer** — `solutions/{NAMES[n]}.py`:\n")
        sol.append("```python\n" + solve_block(SOD / f"{NAMES[n]}.py") + "\n```\n")
        if n in BLANKS:
            sol.append("**Blanks filled — what and why:**\n")
            for code, why in BLANKS[n]:
                sol.append(f"- `{code}` — {why}")
            sol.append("")
        if n in SOL_OUTPUT:
            sol.append("**What the output shows:**\n")
            sol.append(SOL_OUTPUT[n] + "\n")
(ROOT / "study-guide-solutions.md").write_text("\n".join(sol), encoding="utf-8")

print("wrote study-guide.md and study-guide-solutions.md")
