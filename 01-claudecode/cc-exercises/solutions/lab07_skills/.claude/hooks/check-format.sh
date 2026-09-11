#!/usr/bin/env bash
# PostToolUse hook: format and lint Python after Claude Code edits it.
#
# Exits 0 when ruff is absent -- a hook that fails on a machine without the tool
# turns every edit into an error for someone who never asked for the check.
set -uo pipefail

command -v ruff >/dev/null 2>&1 || exit 0

FILE=$(jq -r '.tool_input.file_path // empty' 2>/dev/null)
[ -z "$FILE" ] && exit 0
case "$FILE" in *.py) ;; *) exit 0 ;; esac
[ -f "$FILE" ] || exit 0

ruff format --quiet "$FILE" || true
ruff check --fix --quiet "$FILE" || true
exit 0
