# 00 · Introduction — LLMs with Hugging Face

A study workbook for the Hugging Face `transformers` API: **11 fill-in-the-blank exercises**
(plus reference solutions) with a `check.py` verifier, and a printable **study guide** and
**solutions**.

- **Study guide (read / print):** [`study-guide.pdf`](study-guide.pdf) — theory per section,
  then the exercises (task, what's happening behind the scenes, a hint).
- **Solutions:** [`study-guide-solutions.pdf`](study-guide-solutions.pdf).
- **Runnable workbook:** [`llm-exercises/`](llm-exercises/) — one self-contained file per
  exercise; see its [README](llm-exercises/README.md) to set up (`pip install -r
  requirements.txt`) and run (`python check.py`).

Covers: using pre-trained models with `pipeline()`, the three transformer shapes, tokenization
(`input_ids` / `attention_mask`), datasets & `.map`, `TrainingArguments`, the `Trainer`, and
inference from logits.

## Rebuilding the material

The exercise files and both PDFs are generated. From this folder:

```bash
python tools/gen.py        # -> llm-exercises/{exercises,solutions}/*.py
python tools/build_md.py   # -> study-guide.md + study-guide-solutions.md
python tools/render.py     # -> the two PDFs   (needs: markdown weasyprint pygments)
```
