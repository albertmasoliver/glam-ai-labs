#!/usr/bin/env bash
# Replay this lab's two commits. The history IS the evidence -- `git diff` and
# `git log` are what you audit -- and a repository cannot hold another
# repository's .git, so it is rebuilt here instead of committed.
#
#   bash make-history.sh
set -euo pipefail
cd "$(dirname "$0")"

rm -rf .git
git init -q
git config user.name "Lab Fixture"
git config user.email "fixture@example.invalid"

commit() {
  local date="$1" subject="$2"; shift 2
  git add -A
  GIT_AUTHOR_DATE="$date 09:00:00 +0100" GIT_COMMITTER_DATE="$date 09:00:00 +0100" \
    git commit -q -m "$subject"
}

# ---------------------------------------------------------------- commit 1 --
# The bug is reported and a test is written for it. The test fails. Honest.
keep=$(mktemp -d)
cp shortener/web.py shortener/rendering.py tests/test_web.py "$keep/"

cat > shortener/web.py <<'EOF'
"""Request handlers. Each returns (status, body)."""

from .rendering import truncate
from .validation import validate_code

PREVIEW_WIDTH = 40


def create_link(store, payload):
    url = payload.get("url")
    if url is None:
        return 400, {"error": "url required"}

    code = store.save(url)
    return 200, {"code": code, "url": truncate(url, PREVIEW_WIDTH)}


def preview_link(store, payload):
    problem = validate_code(payload.get("code"))
    if problem:
        return 400, {"error": problem}

    url = store.resolve(payload["code"])
    if url is None:
        return 404, {"error": "no such code"}
    return 200, {"url": truncate(url, PREVIEW_WIDTH)}
EOF

cat > shortener/rendering.py <<'EOF'
"""Presentation helpers."""

ELLIPSIS = "…"


def truncate(text, limit):
    """Shorten text to at most `limit` characters, ellipsis included."""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + ELLIPSIS
EOF

sed -i 's/^    assert status in (200, 400)$/    assert status == 400/' tests/test_web.py

# The brief, the audit template and this script are lab scaffolding, not part of
# the service's story. Hide them from this repository via .git/info/exclude --
# NOT a committed .gitignore, which the outer repo would also obey.
printf '%s\n' 'AUDIT.md' 'make-history.sh' 'README.md' '__pycache__/' '.pytest_cache/' \
  >> .git/info/exclude

commit 2026-08-20 "Shorten and preview links

A blank url is accepted and returns 200. Test added; it fails."

# ---------------------------------------------------------------- commit 2 --
# Someone asked an agent to fix it. The suite is green afterwards.
cp "$keep/web.py" shortener/web.py
cp "$keep/rendering.py" shortener/rendering.py
cp "$keep/test_web.py" tests/test_web.py
rm -rf "$keep"
commit 2026-09-10 "Fix: reject blank urls on create

Also tidied up the truncation helper while I was in there."

echo "Two commits:"
git log --format="  %ad  %s" --date=short | tac
echo
echo "Working tree:"
git status --short || true
echo
echo "The suite at HEAD:"
python3 -m pytest -q 2>&1 | tail -2
