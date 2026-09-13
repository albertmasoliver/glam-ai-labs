# Changelog

## 2.3.0 -- 2025-02-18
- `slugify` accepts `max_length`. Default unchanged at 80.

## 2.0.0 -- 2024-11-04
- **Breaking.** Folding table applied before the ASCII drop, so `Straße`
  now slugs to `strasse` rather than `strae`. Coordinated with the permalink
  backfill in the content service; do not revert without talking to them.

## 1.4.2 -- 2024-06-30
- Empty results raise `SlugError` instead of returning `""`.
