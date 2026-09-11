#!/usr/bin/env bash
# Give this fixture the git history the lab reads.
#
# The outer repository cannot contain a nested .git, so the history ships as this script
# instead of as a checked-in repo. Run it once, here:
#
#     ./make-history.sh
#
# You get six commits between 2019 and 2024, in the order the service actually grew. Reading
# them is half the lab: the code tells you what the system does, the messages tell you why.

set -euo pipefail
cd "$(dirname "$0")"

if [ -d .git ]; then
  echo "Already a git repository. Delete .git first if you want to rebuild the history."
  exit 0
fi

git init -q -b main
git config user.name  "Invoicing Team"
git config user.email "invoicing@example.invalid"

commit () {                       # commit <date> <subject> <paths...>
  local date="$1" subject="$2"; shift 2
  git add -- "$@"
  GIT_AUTHOR_DATE="$date 10:00:00 +0100" GIT_COMMITTER_DATE="$date 10:00:00 +0100" \
    git commit -q -m "$subject"
}

commit 2019-03-14 "Initial invoicing core" \
    .gitignore invoicing/__init__.py invoicing/models.py invoicing/rates.py invoicing/totals.py
commit 2019-06-02 "Import the 2019 billing archive (positional columns, header optional)" \
    invoicing/adapters/__init__.py invoicing/adapters/legacy_csv.py
commit 2020-01-20 "Post confirmed invoices to the internal ledger" \
    invoicing/adapters/ledger.py
commit 2021-11-08 "Per-issuer, per-year numbering with no gaps (audit requirement)" \
    invoicing/config.py invoicing/numbering.py
commit 2024-02-19 "Move posting to the shared finance API" \
    invoicing/service.py
commit 2024-05-30 "HTTP surface and a couple of tests" \
    invoicing/api.py pytest.ini requirements-dev.txt \
    scripts/reconcile.py scripts/serve.py tests/test_api.py tests/test_totals.py

# The README and this script are lab scaffolding, not part of the service's story.
# Hide them from git rather than committing them, so the history stays six commits.
printf '%s\n' 'README.md' 'make-history.sh' >> .git/info/exclude

echo "Six commits, 2019-2024:"
git log --format="  %ad  %s" --date=short | tac
echo
echo "Working tree:"
git status --short --untracked-files=all | sed 's/^/  /' || true
