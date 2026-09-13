#!/usr/bin/env bash
# Harmless on purpose: one line into .claude/runs.log when a session ends, and
# exit 0 whatever happens, because a hook that fails turns somebody else's clone
# into a broken checkout.
#
# It is here so step 5 has something to observe. A headless run without --bare
# loads this file and runs it; with --bare it does not. Stop fires whenever the
# session ends, so a -p run always triggers it -- there is no "maybe the prompt
# did not edit anything" to explain away.
set -u
log="${CLAUDE_PROJECT_DIR:-.}/.claude/runs.log"
mkdir -p "$(dirname "$log")" 2>/dev/null || exit 0
printf 'a session ended in this project\n' >> "$log" 2>/dev/null || true
exit 0
