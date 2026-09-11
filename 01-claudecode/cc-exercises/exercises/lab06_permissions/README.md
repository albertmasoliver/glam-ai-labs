# Lab 06 — permissions

A small Flask weather app. `main.py` calls `requests.get` inline in the handler,
there is an `.env` with an API key in it, and there is no `.claude/` at all.

This lab is about the fence, not the feature.

## The thing to internalise first

Three ingredients together are what make an agent dangerous, and any two are fine:

1. access to **private data**,
2. exposure to **untrusted content**,
3. the ability to **communicate outward**.

Your editor session usually has all three — your repo, a web page or a
dependency's README, and `curl` or `git push`. Deny rules are how you break the
set. Everything else in permissions is about saving yourself clicks.

## What to do

**1. Write `.claude/settings.json` with a deny list.** Deny is the only list that
is not a convenience — an allow list you get wrong costs you a prompt, a deny
list you get wrong costs you a secret.

```json
{
  "permissions": {
    "deny": ["Read(.env)", "..."],
    "allow": ["..."]
  }
}
```

**Cover the variants.** `Read(.env)` does not match `.env.local`, `.env.production`
or `.env.staging`. Those are separate files with the same secrets in them.

**2. Then say the boundary out loud in the session too.** Settings are the fence;
the sentence in the conversation is what stops it proposing work you will have to
decline five times. Both, not either.

**3. Compare modes on the same task.** Run a small change in plan mode, then in
accept-edits, then in auto. Notice what changes — not just how fast it goes, but
how much of the diff you actually looked at.

> Kousen's ch. 5 has his own versions of all of this: the same feature written at
> three levels of trust, a prompt for aligning branch and boundary before editing,
> a prompt for stating the boundary in conversation, and one for making the model
> classify the work before doing it. None of them is reproduced here.

## Done when

`python check.py lab06` passes: `settings.json` parses, every deny rule is shaped
`Tool(pattern)`, and `.env` **and its variants** are covered.
