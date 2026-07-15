#!/usr/bin/env python3
"""Generate one self-contained file per exercise (____ blanks) + one per solution.

Each file is complete on its own: module docstring, its imports at the top, an
optional SAMPLE input, the solve() function, and a runnable __main__ demo.
"""
import pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent / "llm-exercises"
EXD, SOD = ROOT / "exercises", ROOT / "solutions"
for d in (EXD, SOD):
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)

E = []
def add(**k): E.append(k)

# imports[] = top-level imports (shown in full — part of "contain everything")
# sample[]  = optional top-level SAMPLE constant used by the demo
# blank[]   = solve body with ____ blanks    sol[] = full solve body
# main[]    = demo statements (raw; write() wraps them under a blank-guard)

add(n=1, slug="summarize", title="Summarize with a pipeline",
    imports=['from transformers import pipeline'],
    sample=['SAMPLE = (',
            '    "The city council approved a plan on Tuesday to convert the abandoned rail "',
            '    "yard on the east side into a public park, ending nearly a decade of debate "',
            '    "over the twelve-acre site. The first phase will clear the derelict tracks "',
            '    "and add walking paths, a playground, and a small amphitheatre, with work "',
            '    "expected to begin next spring. Supporters argued that the neighbourhood has "',
            '    "the least green space in the city and that the park would raise nearby "',
            '    "property values and give families a safe place to gather. A local business "',
            '    "group had pushed instead for a mixed-use development of shops and flats, "',
            '    "warning that the council was passing up badly needed housing and tax "',
            '    "revenue. To address those concerns, the final plan reserves a strip along "',
            '    "the northern edge for future affordable housing and sets aside space for a "',
            '    "weekend market where local vendors can sell produce and crafts. Funding "',
            '    "will come from a mix of municipal bonds and a state grant for brownfield "',
            '    "redevelopment, though officials cautioned that the grant still depends on "',
            '    "an environmental review of soil left contaminated by decades of industrial "',
            '    "use. If that review clears, the council expects the first phase to open to "',
            '    "the public within two years."',
            ')'],
    sig="def solve(text):",
    blank=['    # Fill: the task name for summarization, and the output key.',
           '    summarizer = pipeline(task=____, model="sshleifer/distilbart-cnn-12-6")',
           '    out = summarizer(text, max_length=40)',
           '    return out[0][____]'],
    sol=['    summarizer = pipeline(task="summarization", model="sshleifer/distilbart-cnn-12-6")',
         '    out = summarizer(text, max_length=40)',
         '    return out[0]["summary_text"]'],
    main=['print(solve(SAMPLE))'])

add(n=2, slug="generate", title="Generate text (control length + padding)",
    imports=['from transformers import pipeline'],
    sample=['SAMPLE = "A good morning routine starts with"'],
    sig="def solve(prompt):",
    blank=['    gen = pipeline(task="text-generation", model="distilgpt2")',
           '    # Fill: how many NEW tokens to generate (30), and the end-of-sequence token id',
           '    # to pad with. (Use max_new_tokens, not max_length: the pipeline already',
           '    # defaults max_new_tokens, so mixing in max_length triggers a warning.)',
           '    out = gen(prompt, max_new_tokens=____,',
           '              pad_token_id=gen.tokenizer.____, truncation=True)',
           '    return out[0]["generated_text"]'],
    sol=['    gen = pipeline(task="text-generation", model="distilgpt2")',
         '    out = gen(prompt, max_new_tokens=30,',
         '              pad_token_id=gen.tokenizer.eos_token_id, truncation=True)',
         '    return out[0]["generated_text"]'],
    main=['print(solve(SAMPLE))'])

add(n=4, slug="translate", title="Translate with a pipeline",
    imports=['from transformers import pipeline'],
    sample=['SAMPLE = "Where is the nearest train station?"'],
    sig="def solve(text):",
    blank=['    # Fill: the task name for English -> Spanish translation.',
           '    translator = pipeline(task=____,',
           '                          model="Helsinki-NLP/opus-mt-en-es")',
           '    return translator(text)[0]["translation_text"]'],
    sol=['    translator = pipeline(task="translation_en_to_es",',
         '                          model="Helsinki-NLP/opus-mt-en-es")',
         '    return translator(text)[0]["translation_text"]'],
    main=['print(solve(SAMPLE))'])

add(n=5, slug="family", title="Pick the right transformer family (offline)",
    imports=[],
    sample=[],
    sig="def solve(task):",
    blank=['    # Fill each family: understanding -> "encoder-only";',
           '    # free generation -> "decoder-only"; seq-to-seq -> "encoder-decoder".',
           '    families = {',
           '        "sentiment": ____,',
           '        "poem": ____,',
           '        "translation": ____,',
           '        "extractive-qa": ____,',
           '    }',
           '    return families[task]'],
    sol=['    families = {"sentiment": "encoder-only", "poem": "decoder-only",',
         '                "translation": "encoder-decoder", "extractive-qa": "encoder-only"}',
         '    return families[task]'],
    main=['for t in ("sentiment", "poem", "translation", "extractive-qa"):',
          '    print(f"{t:>14} -> {solve(t)}")'])

add(n=6, slug="sentiment", title="Classify sentiment",
    imports=['from transformers import pipeline'],
    sample=["SAMPLE = \"Honestly the best coffee I've ever had.\""],
    sig="def solve(text):",
    blank=['    # Fill: the task name for sentiment, and the output key holding the label.',
           '    clf = pipeline(task=____,',
           '                   model="distilbert-base-uncased-finetuned-sst-2-english")',
           '    return clf(text)[0][____]'],
    sol=['    clf = pipeline(task="sentiment-analysis",',
         '                   model="distilbert-base-uncased-finetuned-sst-2-english")',
         '    return clf(text)[0]["label"]'],
    main=['print(solve(SAMPLE))'])

add(n=7, slug="load_model", title="Load an Auto model + tokenizer",
    imports=['from transformers import AutoTokenizer, AutoModelForSequenceClassification'],
    sample=[],
    sig="def solve():",
    blank=['    name = "distilbert-base-uncased"',
           '    tokenizer = AutoTokenizer.from_pretrained(name)',
           '    # Fill: which imported class loads a classification head, and how many labels.',
           '    model = ____.from_pretrained(name, num_labels=____)',
           '    return tokenizer, model'],
    sol=['    name = "distilbert-base-uncased"',
         '    tokenizer = AutoTokenizer.from_pretrained(name)',
         '    model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=2)',
         '    return tokenizer, model'],
    main=['tok, model = solve()',
          'print(type(model).__name__, "num_labels =", model.config.num_labels)'])

add(n=8, slug="tokenize", title="Tokenize texts (padding, truncation, tensors)",
    imports=['from transformers import AutoTokenizer'],
    sample=['SAMPLE = [',
            '    "The parcel arrived a day early and everything inside was wrapped carefully, "',
            '    "so I am really happy with how this order turned out.",',
            '    "Delivery ran late, the box was badly crushed on one corner, and one of the "',
            '    "mugs inside had a small chip, which was honestly a bit disappointing.",',
            '    "Good value.",',
            ']'],
    sig="def solve(tokenizer, texts):",
    blank=['    # Fill: return PyTorch tensors ("pt"), and cap the length at 64 tokens.',
           '    return tokenizer(texts, return_tensors=____, padding=True,',
           '                     truncation=True, max_length=____)'],
    sol=['    return tokenizer(texts, return_tensors="pt", padding=True,',
         '                     truncation=True, max_length=64)'],
    main=['tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")',
          'enc = solve(tok, SAMPLE)',
          'print("shape:", tuple(enc["input_ids"].shape),',
          '      " (rows = sentences, cols = padded length)")',
          'print("\\ninput_ids (0 = [PAD]; sentences padded to the longest one):")',
          'print(enc["input_ids"])',
          'print("\\nattention_mask (1 = real token, 0 = padding the model ignores):")',
          'print(enc["attention_mask"])'])

add(n=9, slug="tokenize_dataset", title="Tokenize a whole dataset with .map",
    imports=['from transformers import AutoTokenizer',
             'from datasets import load_dataset'],
    sample=[],
    sig="def solve(tokenizer):",
    blank=['    data = load_dataset("imdb", split="train[:1%]")',
           '',
           '    def tok(batch):',
           '        return tokenizer(batch["text"], padding=True, truncation=True, max_length=128)',
           '',
           '    # Fill: apply tok across the dataset in batches.',
           '    return data.map(tok, batched=____)'],
    sol=['    data = load_dataset("imdb", split="train[:1%]")',
         '',
         '    def tok(batch):',
         '        return tokenizer(batch["text"], padding=True, truncation=True, max_length=128)',
         '',
         '    return data.map(tok, batched=True)'],
    main=['tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")',
          'ds = solve(tok)',
          'print("columns:", ds.column_names, " (input_ids + attention_mask are new)")',
          'print("rows:   ", ds.num_rows)',
          'row = ds[0]',
          'print("\\n--- one tokenized example ---")',
          'print("label         :", row["label"])',
          'print("text          :", row["text"][:90].replace(chr(10), " "), "...")',
          'ids = row["input_ids"]',
          'print("input_ids     :", ids[:16], "...  (length", len(ids), ")")',
          'print("attention_mask:", row["attention_mask"][:16], "...")',
          'print("decoded back  :", tok.decode(ids[:16]))'])

add(n=10, slug="training_args", title="Set up TrainingArguments (offline)",
    imports=['from transformers import TrainingArguments'],
    sample=[],
    sig="def solve():",
    blank=['    # Fill the values described in the task.',
           '    return TrainingArguments(',
           '        output_dir="./out",',
           '        eval_strategy=____,               # evaluate at the end of each epoch',
           '        num_train_epochs=____,            # 3',
           '        learning_rate=____,               # 2e-5',
           '        per_device_train_batch_size=____, # 8',
           '        per_device_eval_batch_size=8,',
           '        weight_decay=____,                # 0.01',
           '    )'],
    sol=['    return TrainingArguments(',
         '        output_dir="./out", eval_strategy="epoch", num_train_epochs=3,',
         '        learning_rate=2e-5, per_device_train_batch_size=8,',
         '        per_device_eval_batch_size=8, weight_decay=0.01)'],
    main=['print(solve())'])

add(n=11, slug="build_trainer", title="Wire up the Trainer",
    imports=['from transformers import (AutoTokenizer, AutoModelForSequenceClassification,',
             '                          Trainer, TrainingArguments)',
             'from datasets import Dataset'],
    sample=[],
    sig="def solve(model, args, train_ds, eval_ds, tokenizer):",
    blank=['    # Fill: pass the model, the args, and the two datasets into the Trainer.',
           '    return Trainer(',
           '        model=____,',
           '        args=____,',
           '        train_dataset=____,',
           '        eval_dataset=____,',
           '        tokenizer=tokenizer,',
           '    )'],
    sol=['    return Trainer(model=model, args=args, train_dataset=train_ds,',
         '                   eval_dataset=eval_ds, tokenizer=tokenizer)'],
    main=['# Assemble the Trainer, fine-tune 2 steps on a tiny dataset, and SAVE the model.',
          'import pathlib',
          'tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")',
          'model = AutoModelForSequenceClassification.from_pretrained(',
          '    "distilbert-base-uncased", num_labels=2,',
          '    id2label={0: "NEGATIVE", 1: "POSITIVE"}, label2id={"NEGATIVE": 0, "POSITIVE": 1})',
          'data = Dataset.from_dict(',
          '    {"text": ["a great day", "a terrible day", "loved it", "hated it"],',
          '     "label": [1, 0, 1, 0]}).map(',
          '    lambda b: tok(b["text"], padding="max_length", truncation=True, max_length=16),',
          '    batched=True)',
          'args = TrainingArguments(output_dir="./out", max_steps=2,',
          '                         per_device_train_batch_size=2, logging_steps=1, report_to=[])',
          'trainer = solve(model, args, data, data, tok)',
          'result = trainer.train()   # real training loop — a couple of gradient steps',
          'print("trained — final loss:", round(result.training_loss, 4))',
          'save_dir = pathlib.Path(__file__).resolve().parent.parent / "finetuned-demo"',
          'model.save_pretrained(save_dir); tok.save_pretrained(save_dir)',
          'print("saved fine-tuned model to", save_dir.name, "/  (exercise 11 loads it)")'])

add(n=12, slug="predict", title="Use the fine-tuned model (from logits)",
    imports=['import pathlib',
             'import torch',
             'from transformers import AutoTokenizer, AutoModelForSequenceClassification'],
    sample=["SAMPLE = \"This is the worst service I've ever had.\""],
    sig="def solve(text):",
    blank=['    # Load the model YOU fine-tuned and saved in exercise 10:',
           '    model_dir = pathlib.Path(__file__).resolve().parent.parent / "finetuned-demo"',
           '    tok = AutoTokenizer.from_pretrained(model_dir)',
           '    model = AutoModelForSequenceClassification.from_pretrained(model_dir)',
           '    inp = tok(text, return_tensors="pt", padding=True, truncation=True)',
           '    with torch.no_grad():',
           '        logits = model(**inp).logits',
           '    # Fill: the axis to argmax over (1), and the string method to upper-case.',
           '    pred = int(torch.argmax(logits, dim=____))',
           '    return model.config.id2label[pred].____()'],
    sol=['    model_dir = pathlib.Path(__file__).resolve().parent.parent / "finetuned-demo"',
         '    tok = AutoTokenizer.from_pretrained(model_dir)',
         '    model = AutoModelForSequenceClassification.from_pretrained(model_dir)',
         '    inp = tok(text, return_tensors="pt", padding=True, truncation=True)',
         '    with torch.no_grad():',
         '        logits = model(**inp).logits',
         '    pred = int(torch.argmax(logits, dim=1))',
         '    return model.config.id2label[pred].upper()'],
    main=['model_dir = pathlib.Path(__file__).resolve().parent.parent / "finetuned-demo"',
          'if not model_dir.exists():',
          '    print("No fine-tuned model yet — run exercise 10 first (its demo saves it).")',
          'else:',
          '    print(solve(SAMPLE))'])

def fname(e): return f"ex{e['n']:02d}_{e['slug']}.py"

def write(e, is_sol):
    L = ['"""']
    tag = "Reference solution" if is_sol else "Exercise"
    L.append(f"{tag} {e['n']} — {e['title']}.")
    L.append("")
    if is_sol:
        L.append(f"Complete, self-contained reference. Verify:  python check.py --solutions {e['n']}")
    else:
        L.append("Self-contained: imports at the top, then complete solve() by replacing every")
        L.append(f"____ blank (see the comments). Verify:  python check.py {e['n']}")
        L.append(f"Reference: solutions/{fname(e)}")
    L.append('"""')
    if e["imports"]:
        L += [""] + e["imports"]
    if e["sample"]:
        L += [""] + e["sample"]
    L += ["", "", e["sig"]]
    L += e["sol"] if is_sol else e["blank"]
    L += ["", "", 'if __name__ == "__main__":',
          '    import inspect',
          '    if "____" in inspect.getsource(solve):',
          '        print("Fill in the ____ blanks, then run again  (or: python check.py).")',
          '    else:']
    L += ["        " + m for m in e["main"]]
    L.append("")
    (SOD if is_sol else EXD).joinpath(fname(e)).write_text("\n".join(L), encoding="utf-8")

# Renumber sequentially (an exercise may have been removed, leaving a gap).
for new, e in enumerate(sorted(E, key=lambda x: x["n"]), 1):
    e["n"] = new

for e in E:
    write(e, False)
    write(e, True)

print("wrote", len(E), "exercises +", len(E), "solutions")
