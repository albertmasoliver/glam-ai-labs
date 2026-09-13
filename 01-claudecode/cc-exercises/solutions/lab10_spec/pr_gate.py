#!/usr/bin/env python3
"""Check a contract against the repository, one line at a time.

    python3 pr_gate.py            # reads SPEC.md
    python3 pr_gate.py --spec other.md

Every postcondition and every invariant has to name the test that proves it,
as a pytest node id in backticks:

    - The review page lists one row per cart line.
      `tests/test_review.py::test_one_row_per_line`

The gate does not read your prose and does not care whether it is good. It
cares that each claim points at a test, that the test exists, that it runs,
and that it passes. A contract line with no test under it is a sentence, not
a check.

It asks pytest which nodes PASSED rather than reading the exit code, because
pytest exits 0 for a skipped test and for an expected failure, and a claim
proven by a test that never ran is the exact thing this gate exists to catch.
It also runs the whole suite, because a contract can only be proven by the
tests it names and cannot notice the ones it left out.

Run it:  python3 pr_gate.py
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROVEN_BY_TESTS = ("postconditions", "invariants")
PROSE_ONLY = ("preconditions", "negative criteria")
# file.py::test_name, file.py::Class::test_name, and the [param] pytest prints.
NODE = re.compile(
    r"`([^`\s]+\.py(?:::[A-Za-z_][A-Za-z0-9_]*)+(?:\[[^`\]]*\])?)`")


def sections(text):
    out, name = {}, None
    for line in text.splitlines():
        heading = re.match(r"^##+\s+(.*)", line)
        if heading:
            name = heading.group(1).strip().lower()
            out[name] = []
        elif name:
            out[name].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def claims(block):
    """Bullet lines, each with the node ids it names."""
    found, current = [], None
    for line in block.splitlines():
        bullet = re.match(r"^\s*[-*]\s+(.*)", line)
        if bullet:
            current = [bullet.group(1).strip(), []]
            found.append(current)
        if current is not None:
            current[1].extend(NODE.findall(line))
    return [(text, nodes) for text, nodes in found if text]


# -o addopts= so a pytest.ini in the repository cannot rewrite the gate's own
# invocation, and -p no:cacheprovider so running the gate leaves nothing behind.
PYTEST = ["-q", "--no-header", "--tb=no", "-o", "addopts=", "-p", "no:cacheprovider"]


def inside_repo(node):
    """Is the test file this node names actually in this repository?"""
    path = (HERE / node.split("::")[0]).resolve()
    try:
        path.relative_to(HERE)
    except ValueError:
        return False
    return path.exists()


def collect(node_ids):
    """Which of these node ids pytest can actually find."""
    if not node_ids:
        return set(), ""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *PYTEST, "--collect-only",
         *sorted(set(node_ids))],
        cwd=HERE, capture_output=True, text=True,
    )
    seen = {line.strip() for line in result.stdout.splitlines() if "::" in line}
    resolved = {n for n in node_ids if n in seen}
    return resolved, result.stdout + result.stderr


def run_tests(node_ids):
    """Node ids pytest reported as PASSED. Not 'did not fail' -- passed.

    The exit code will not do: pytest exits 0 for a skipped test and for an
    expected failure, so a claim can be 'proven' by a test whose body never
    ran. -rA prints one PASSED line per node that really passed, and that is
    the only thing counted here.
    """
    if not node_ids:
        return set(), ""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *PYTEST, "-rA", *sorted(set(node_ids))],
        cwd=HERE, capture_output=True, text=True,
    )
    output = result.stdout + result.stderr
    passed = set()
    for line in output.splitlines():
        if line.startswith("PASSED "):
            passed.add(line.split(None, 1)[1].strip())
    return passed, output


def whole_suite():
    """The suite, not just the nodes the contract happens to name."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *PYTEST], cwd=HERE,
        capture_output=True, text=True,
    )
    return result.returncode == 0, (result.stdout + result.stderr).strip().splitlines()[-1:]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", default="SPEC.md")
    args = ap.parse_args()

    spec = HERE / args.spec
    if not spec.exists():
        print(f"no {args.spec} to check", file=sys.stderr)
        return 2

    found = sections(spec.read_text())
    problems, checked = [], 0

    for name in PROSE_ONLY:
        if not claims(found.get(name, "")):
            problems.append(f"{name}: nothing written down")

    wanted = []
    for name in PROVEN_BY_TESTS:
        for _, nodes in claims(found.get(name, "")):
            wanted.extend(nodes)

    outside = [n for n in set(wanted) if not inside_repo(n)]
    for node in sorted(outside):
        problems.append(f"{node} is not a test file in this repository")
    wanted = [n for n in wanted if n not in outside]

    # Resolve first, so one typo does not black out every other line.
    resolved, _ = collect(wanted)
    missing = sorted(set(wanted) - resolved)
    passed, output = run_tests(sorted(resolved))

    for name in PROVEN_BY_TESTS:
        entries = claims(found.get(name, ""))
        if not entries:
            problems.append(f"{name}: nothing written down")
        for text, nodes in entries:
            checked += 1
            short = text if len(text) < 64 else text[:61] + "..."
            if not nodes:
                problems.append(f"{name}: no test names this -- {short}")
                continue
            gone = [n for n in nodes if n in missing]
            unproven = [n for n in nodes if n in resolved and n not in passed]
            if gone:
                problems.append(f"{name}: no such test -- {', '.join(gone)}")
            elif unproven:
                problems.append(f"{name}: {', '.join(unproven)} did not pass -- {short}")
            elif any(n in outside for n in nodes):
                problems.append(f"{name}: proven by a test outside the repository -- {short}")
            else:
                print(f"  proven   {short}")

    # A contract can only be proven by the tests it names. It cannot notice the
    # ones it left out, so the suite gets a say too.
    green, tail = whole_suite()
    if not green:
        problems.append("the suite is red outside your contract: " + " ".join(tail))

    print()
    if problems:
        for line in problems:
            print(f"  UNPROVEN {line}")
        if output and "no tests ran" not in output:
            print("\n" + "\n".join(output.strip().splitlines()[-3:]))
        print(f"\n  {len(problems)} of {checked} contract lines are not proven.\n")
        return 1
    print(f"  {checked} contract lines, all proven, and the suite is green.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
