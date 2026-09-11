# legacy-service — what I verified

A reference answer, not the only one. What makes it an answer is that every claim
below was checked by opening a file; the things I could not check are marked.

## What it does

Turns invoice payloads into money. Three responsibilities, in this order:
arithmetic (`totals.py` over `rates.py`), validation and posting (`service.py`),
and an HTTP surface (`api.py`). A separate path imports a 2019 CSV archive
(`adapters/legacy_csv.py`), and a cron script reconciles it (`scripts/reconcile.py`).

## Where execution starts

`scripts/serve.py`, in `main()` — it constructs the `HTTPServer` and hands it
`invoicing.api.Handler`. **Not `api.py`**, which only defines the handler class,
and not `invoicing/__init__.py`, which is empty. Two routes exist, both POST:
`/invoices/preview` → `service.render`, `/invoices/confirm` → `service.confirm`.

`scripts/reconcile.py` is a second entry point with no relation to the first.
Nothing imports it; cron runs it. That is asserted in its docstring and I could
not verify it — there is no crontab in the repo.

## Read these first, in this order

1. `invoicing/models.py` — three plain classes, no behaviour worth arguing with.
2. `invoicing/rates.py` — every number the service produces comes from here.
3. `invoicing/totals.py` — the arithmetic, and the only module allowed to do it.
4. `invoicing/service.py` — validation, posting, and the status transition.
5. `scripts/serve.py` then `invoicing/api.py` — the surface, once you know what
   it is a surface over.

## Three things the code says that turned out to need checking

**`rates.py` does not hold only rates.** It also owns `round_half_up` (the
rounding policy) and `CURRENCIES` (the minor-units table `service.render` uses to
scale cents). The module docstring admits this; a file listing does not. If you
went looking for rounding you would look anywhere but here.

**`ledger.py` is not dead, only half dead.** Its own docstring says "DEAD SINCE
2024-02". `service.confirm` does bypass it — posting goes to
`post_to_finance_api`. But `grep format_entry` finds a live import in
`scripts/reconcile.py`, so deleting the module breaks the nightly job. "Dead
code" was true of one function, not of the file.

**`api.py` claims "the 2019 rewrite removed [the framework]".** `git log` has no
rewrite: the first commit, 2019-03-14, is already framework-free. Either the
rewrite predates the repository or the comment is folklore. I did not resolve it —
flagging it because it is the kind of sentence that gets repeated as fact.

## Deliberate, do not "fix"

- `numbering.reserve()` never rolls back. Gaps in a per-issuer, per-year sequence
  are an audit finding; a cancelled invoice keeps its number. Stated in the
  docstring and in the 2021-11-08 commit message.
- Exempt (`E`) and zero-rated (`Z`) both produce zero tax and must stay in
  separate buckets — `totals.tax_summary` keys on `is_exempt`, not on the amount.
- Positional columns in `legacy_csv.py`: a third of the archive has no header row.

## The one that will bite you

`config.py` reads its file and its environment **at import time**. Setting
`INVOICING_ENV` after the first import does nothing, so `dry_run` stays whatever
it was when the process started. That is why a confirm can silently no-op.
