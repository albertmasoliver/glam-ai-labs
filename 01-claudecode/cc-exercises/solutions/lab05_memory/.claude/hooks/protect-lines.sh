#!/usr/bin/env bash
# PreToolUse gate: refuse any edit to trainer/lines.py.
#
# Why this one is not a line in CLAUDE.md. lines.py is a transcription of a
# public-domain source text, and the suite cannot catch a corruption of it --
# every assertion compares LINES to itself, so a silently mangled sonnet is
# still green. An instruction whose violation nothing downstream would notice
# is exactly the instruction that should not be left to advice.
set -u

payload=$(cat)
path=$(printf '%s' "$payload" |
  sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')

case "$path" in
  */trainer/lines.py | trainer/lines.py)
    echo "Refused: trainer/lines.py is a transcription, not code. Correct the" >&2
    echo "source text and re-transcribe it, or ask a human to." >&2
    exit 2
    ;;
esac

exit 0
