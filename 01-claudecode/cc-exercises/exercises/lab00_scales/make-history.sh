#!/usr/bin/env bash
# Give the two fixtures the history they would really have. Run once, before
# the lab. The history is not decoration -- it is where the signal lives.
set -euo pipefail
cd "$(dirname "$0")/fixtures"

# Caches are machine-specific; without this, two students commit different trees
# into what is supposed to be the same fixture history.
find . -name __pycache__ -o -name .pytest_cache | xargs rm -rf 2>/dev/null || true

commit() {  # commit <date> <author> <email> <subject>
  GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" \
  GIT_AUTHOR_NAME="$2" GIT_COMMITTER_NAME="$2" \
  GIT_AUTHOR_EMAIL="$3" GIT_COMMITTER_EMAIL="$3" \
    git commit -q --allow-empty -m "$4"
}

# alpha -- one person, one sitting.
rm -rf alpha/.git && git init -q -b main alpha
( cd alpha
  git add -A
  commit "2026-01-04T11:20:00" "Sam Ortiz" "sam@example.invalid" \
    "Total the quarterly receipts" )

# beta -- three people, two years, one breaking change that had to be planned.
rm -rf beta/.git && git init -q -b main beta
( cd beta
  git add -A
  commit "2024-06-30T09:10:00" "Rita Moreau" "rita@example.invalid" \
    "Raise SlugError on an empty result instead of returning empty string"
  commit "2024-11-04T16:02:00" "Rita Moreau" "rita@example.invalid" \
    "Fold before the ASCII drop (BREAKING: slug output changes)

Coordinated with the content-api permalink backfill. Search-index reindexed
on the 5th. Do not revert without both teams."
  commit "2024-11-05T08:44:00" "Dan Whittle" "dan@example.invalid" \
    "Reindex runbook for the slug change"
  commit "2025-02-18T14:31:00" "Priya Nair" "priya@example.invalid" \
    "Add max_length to slugify, default unchanged"
  commit "2025-03-02T10:05:00" "Dan Whittle" "dan@example.invalid" \
    "Run the suite on pull requests" )

echo "alpha: $(git -C alpha rev-list --count HEAD) commit(s)"
echo "beta:  $(git -C beta rev-list --count HEAD) commits"
