#!/usr/bin/env python3
"""PreToolUse hook: refuse an edit that puts type annotations into fixture code.

PostToolUse cannot do this job. It runs after the write has already landed, so
the most it can manage is a complaint about a file that is already on disk.
Only PreToolUse can exit 2, which makes Claude Code drop the tool call and hand
whatever went to stderr back to the model as the reason it was refused.

NOTE(rm, 2024-11): this was a review comment for a year and annotations kept
landing anyway, because everyone's editor adds them on save. A rule nobody can
forget beats a rule everybody agrees with. Anything that will not parse is let
through -- a hook that treats a half-written file as a violation blocks every
intermediate save, and then people turn hooks off.
"""

import ast
import json
import sys
import textwrap

ANNOTATED = (ast.FunctionDef, ast.AsyncFunctionDef)


def proposed_source(event):
    """The text the tool wants to put on disk, whichever tool is asking.

    Write carries the whole file in `content`; Edit carries only the replacement
    in `new_string`. A replacement is usually indented, so dedent before parsing:
    an unmodified fragment raises IndentationError and would sail straight past.
    """
    tool_input = event.get("tool_input") or {}
    for key in ("content", "new_string"):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return textwrap.dedent(value)
    return ""


def every_argument(arguments):
    """Flatten an ast.arguments into the args that can carry an annotation."""
    args = list(getattr(arguments, "posonlyargs", []))
    args += list(arguments.args) + list(arguments.kwonlyargs)
    args += [a for a in (arguments.vararg, arguments.kwarg) if a is not None]
    return args


def violations(source):
    """(line, description) for every annotation in the proposed source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            found.append((node.lineno, "annotated assignment"))
        elif isinstance(node, ANNOTATED):
            if node.returns is not None:
                found.append((node.lineno, f"return annotation on {node.name}()"))
            for arg in every_argument(node.args):
                if arg.annotation is not None:
                    found.append(
                        (arg.lineno, f"annotated argument {arg.arg} of {node.name}()")
                    )
    return sorted(set(found))


def main():
    try:
        event = json.load(sys.stdin)
    except (ValueError, UnicodeDecodeError):
        return 0
    if not isinstance(event, dict):
        return 0

    path = str((event.get("tool_input") or {}).get("file_path") or "")
    if not path.endswith(".py"):
        return 0

    found = violations(proposed_source(event))
    if not found:
        return 0

    print(f"Refused: {path} would gain type annotations, and this project has "
          f"none anywhere.", file=sys.stderr)
    for line, what in found[:5]:
        print(f"  line {line}: {what}", file=sys.stderr)
    print("Rewrite the edit without annotations, or say why this file is the "
          "exception.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
