#!/usr/bin/env python3
"""Verify the artifacts the Claude Code labs leave behind.

    python check.py                 # check your work under exercises/
    python check.py --solutions     # check the reference answers
    python check.py lab05 lab07     # check only these

What this can and cannot do: it verifies artifacts, not learning. It can tell
you that a settings.json denies what it should and that a trainer/ package
passes its tests with an injected storage. It cannot tell you whether you
understood why the seam matters, and the seam is the point. Labs whose result
is judgement report MANUAL and print their definition of done.

Statuses
  PASS     the artifact exists and is correct
  TODO     the artifact is not there yet -- you have not done this lab
  FAIL     the artifact is there and something about it is wrong
  MANUAL   nothing machine-checkable; the definition of done is printed
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parent
PASS, FAIL, TODO, MANUAL = "PASS", "FAIL", "TODO", "MANUAL"

LINE_COUNT = 14  # Sonnet 18


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def run(cmd, cwd=None, env=None, stdin="", timeout=120):
    full = dict(os.environ)
    full.update(env or {})
    return subprocess.run(
        cmd, cwd=cwd, env=full, input=stdin, capture_output=True,
        text=True, timeout=timeout,
    )


def frontmatter(path):
    """Return (metadata dict, body, raw frontmatter text). Raises on bad YAML."""
    text = path.read_text()
    if not text.startswith("---"):
        raise ValueError("no YAML frontmatter (the file must start with ---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("frontmatter is never closed by a second ---")
    raw = parts[1]
    if yaml is None:
        raise ValueError("pyyaml is not installed: pip install -r requirements.txt")
    meta = yaml.safe_load(raw)
    if not isinstance(meta, dict):
        raise ValueError("frontmatter did not parse to a mapping")
    return meta, parts[2], raw


# --------------------------------------------------------------------------
# lab 01 -- first contact                                          MANUAL
# --------------------------------------------------------------------------

def lab01(_d):
    return MANUAL, "Build something from nothing, in one session.", [
        "An app that runs exists that did not exist an hour ago.",
        "You can say what you asked for, and what it did that you did not ask for.",
    ]


# --------------------------------------------------------------------------
# lab 02 -- the five jobs
# --------------------------------------------------------------------------

FROZEN_REASON = {
    "notes/formatting.py": "presentation only -- no rule belongs here",
    "notes/legacy_export.py": "ugly on purpose; nothing asked you to fix it",
    "tests/test_web.py": "a red test goes green two ways, and only one is a fix",
}

JOB_PATTERNS = {
    "the symptom, in checkable terms":
        r"\b(400|200|test_create_rejects_empty_title)\b",
    "the desired behaviour, as its own sentence":
        r"\b(must|should|has to|is rejected|are rejected|rejects?|required|reject)\b",
    "the local convention, by pointing at it":
        r"(validation\.py|validator|pattern|convention|same way|style)",
    "the boundary":
        r"(don'?t|do not|never|only|leave|without|untouched|unrelated|keep .* as)",
}


def _prompt_jobs(text):
    """Which of the five jobs the prompt appears to do. A grep, not a judge."""
    low = text.lower()
    found, missing = [], []
    for job, pat in JOB_PATTERNS.items():
        (found if re.search(pat, low, re.I) else missing).append(job)
    return found, missing


def _real_paths(text, root):
    hits = set()
    for m in re.findall(r"[\w./-]+\.py", text):
        if (root / m.lstrip("./")).exists():
            hits.add(m.lstrip("./"))
    return hits


def lab02(d):
    if not (d / "notes").is_dir():
        return TODO, "The notes fixture is not here.", []

    notes, bad = [], []

    # ---- 1. the prompt ---------------------------------------------------
    pf = d / "PROMPT.md"
    if not pf.exists():
        return TODO, "No PROMPT.md yet.", [
            "Write the request before you send it. The lab is the prompt, not the fix.",
        ]
    ptext = pf.read_text()
    if "<the symptom" in ptext or "<the boundary" in ptext:
        return TODO, "PROMPT.md is still the template.", [
            "Replace the placeholders with the request you are actually going to send.",
        ]

    found, missing = _prompt_jobs(ptext)
    paths = _real_paths(ptext, d)
    if not paths:
        missing.append("the likely location (a real path in this repo)")
    else:
        found.append("the likely location")
        notes.append("points at " + ", ".join(sorted(paths)))
    if missing:
        bad.append("PROMPT.md is missing " + "; ".join(missing))
    else:
        notes.append(f"PROMPT.md carries all five jobs ({len(ptext.split())} words)")

    # ---- 2. the visible test ---------------------------------------------
    r = run([sys.executable, "-m", "pytest", "-q"], cwd=d)
    if r.returncode != 0:
        tail = (r.stdout or r.stderr).strip().splitlines()[-4:]
        if not bad and not any("passed" in l for l in tail):
            return TODO, "The failing test still fails -- nothing has been fixed yet.", tail
        bad.append("the visible tests do not pass")
        bad.extend(tail)
    else:
        m = re.search(r"(\d+) passed", r.stdout)
        notes.append(f"{m.group(1) if m else '?'} visible tests pass")

    # ---- 3. did the reason transfer? -------------------------------------
    sys.path.insert(0, str(d))
    for mod in [m for m in list(sys.modules) if m == "notes" or m.startswith("notes.")]:
        del sys.modules[mod]
    transferred = literal = None
    try:
        from notes.store import Store
        from notes.web import create_note, update_note
        s = Store()
        create_note(s, {"title": "Groceries", "body": "milk"})
        transferred = update_note(s, 1, {"title": ""})[0] == 400
        literal = create_note(s, {"title": "   ", "body": "x"})[0] == 400
        s2 = Store()
        create_note(s2, {"title": "Groceries", "body": "milk"})
        still_ok = (update_note(s2, 1, {"body": "eggs"})[0] == 200
                    and update_note(s2, 99, {"body": "x"})[0] == 404)
    except Exception as e:
        bad.append(f"the app no longer imports or runs: {type(e).__name__}: {e}")
        still_ok = False
    finally:
        sys.path.remove(str(d))

    if transferred:
        notes.append("transfer: update_note rejects a blank title too -- your reason carried")
    elif transferred is False:
        bad.append("transfer: update_note STILL accepts an empty title. It has the same "
                   "defect and nothing pointed at it -- your prompt gave an instruction "
                   "where it needed a reason. Try naming why: every path that accepts "
                   "user input is checked the same way")
    if literal is False:
        bad.append('literalism: a title of "   " is still accepted. You said empty and got '
                   "exactly empty. Scope is something you state, not something it infers")
    elif literal:
        notes.append('literalism: "   " is rejected too, not just ""')
    if transferred is not None and not still_ok:
        bad.append("a body-only update or a missing note no longer behaves -- "
                   "the fix reached further than the rule did")

    # ---- 4. did the fence hold? ------------------------------------------
    baseline = d / ".baseline.json"
    if not baseline.exists():
        notes.append("no .baseline.json -- cannot check the frozen files")
    else:
        try:
            frozen = json.loads(baseline.read_text())["frozen"]
        except Exception as e:
            bad.append(f".baseline.json is unreadable: {e}")
            frozen = {}
        moved = []
        for rel, want in frozen.items():
            f = d / rel
            if not f.exists():
                moved.append(f"{rel} was deleted")
            elif hashlib.sha256(f.read_bytes()).hexdigest() != want:
                moved.append(f"{rel} was modified -- {FROZEN_REASON.get(rel, 'frozen')}")
        if moved:
            bad.append("the fence did not hold: " + "; ".join(moved) +
                       ". Nothing asked you to touch those. Either your prompt had no "
                       "boundary clause, or it had one and it was too vague to hold")
        else:
            notes.append(f"{len(frozen)} frozen files unchanged")

    if bad:
        return FAIL, "The fix landed. Something else did not.", notes + bad
    return PASS, "Fixed, transferred, and stayed inside the fence.", notes


# --------------------------------------------------------------------------
# lab 03 -- the session                                            MANUAL
# --------------------------------------------------------------------------

def lab03(_d):
    return MANUAL, "Drive the session instead of letting it drift.", [
        "You ran /context before and after a piece of work and can say what grew.",
        "You cleared once, deliberately, and knew what you were throwing away.",
        "You know which of plan / accept-edits / auto you were in, and why.",
    ]


# --------------------------------------------------------------------------
# lab 04 -- auditing the evidence
# --------------------------------------------------------------------------

def _blank_url_assertion(path):
    """The assertion in the test written to catch the bug, as source text."""
    import ast
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError as e:
        return None, f"tests/test_web.py does not parse: {e}"
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and "blank_url" in node.name:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Assert):
                    return sub.test, None
    return None, None


def _is_strict_400(test):
    """True only for `something == 400`, not `in (200, 400)` and not `!= 500`."""
    import ast
    return (isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value == 400)


def _audit_findings(text):
    """Findings that carry evidence, and findings that are just a claim."""
    blocks = re.split(r"^##\s+Finding\b", text, flags=re.M)[1:]
    withev, bare = [], []
    for i, b in enumerate(blocks, 1):
        m = re.search(r"\*\*Evidence:?\*\*(.*?)(?=\n\*\*|\Z)", b, re.S | re.I)
        ev = (m.group(1) if m else "")
        ev = re.sub(r"<[^>]*>", "", ev).strip()
        claim = re.search(r"\*\*Claim:?\*\*(.*?)(?=\n\*\*|\Z)", b, re.S | re.I)
        claim = (claim.group(1).strip() if claim else "")
        (withev if (ev and claim) else bare).append((i, ev))
    return withev, bare


def lab04(d):
    if not (d / "shortener").is_dir():
        return TODO, "The shortener fixture is not here.", []

    notes, bad = [], []

    # ---- 1. the audit ----------------------------------------------------
    af = d / "AUDIT.md"
    if not af.exists():
        return TODO, "No AUDIT.md yet.", [
            "Read the diff before you change anything. The audit is the lab.",
        ]
    atext = af.read_text()
    if "<a file:line" in atext or re.search(r"\*\*Claim:\*\*\s*\n\s*\n", atext):
        return TODO, "AUDIT.md is still the template.", [
            "Three findings, each with a claim and evidence you could hand to someone else.",
        ]
    withev, bare = _audit_findings(atext)
    if len(withev) < 3:
        bad.append(f"AUDIT.md has {len(withev)} findings with evidence "
                   f"({len(bare)} claim-only). Three are findable, and a finding "
                   "without evidence is an opinion")
    else:
        cited = {m.lstrip("./") for ev in (e for _, e in withev)
                 for m in re.findall(r"[\w./-]+\.py", ev)}
        real = {c for c in cited if (d / c).exists()}
        if not real:
            bad.append("AUDIT.md cites no file that exists in this repo -- "
                       "evidence means a path, a command and its output, or a commit")
        else:
            notes.append(f"{len(withev)} findings with evidence, citing "
                         + ", ".join(sorted(real)))

    # ---- 2. is the verifier a verifier again? ----------------------------
    tf = d / "tests" / "test_web.py"
    assertion, err = _blank_url_assertion(tf) if tf.exists() else (None, "tests/test_web.py is gone")
    if err:
        bad.append(err)
    elif assertion is None:
        bad.append("no test for a blank url survives -- the one test written to catch "
                   "this bug should still be there, and should still be strict")
    elif not _is_strict_400(assertion):
        bad.append("the blank-url assertion still accepts more than one answer. "
                   "Behaviour is not the problem here -- evidence is: a test that "
                   "passes whether or not the bug is present will not catch the next "
                   "regression either")
    else:
        notes.append("the blank-url test asserts == 400 again")

    # ---- 3. behaviour, which cannot be argued with -----------------------
    sys.path.insert(0, str(d))
    for mod in [m for m in list(sys.modules) if m == "shortener" or m.startswith("shortener.")]:
        del sys.modules[mod]
    try:
        from shortener.store import Store
        from shortener.web import create_link
        from shortener.rendering import truncate

        blanks, nonstrings, crashed = [], [], []
        for v in ("", " ", "   ", "\t\n"):
            if create_link(Store(), {"url": v})[0] != 400:
                blanks.append(repr(v))
        for v in (123, None, [], {}, True):
            try:
                if create_link(Store(), {"url": v})[0] != 400:
                    nonstrings.append(repr(v))
            except Exception as e:
                crashed.append(f"{v!r} -> {type(e).__name__}")
        valid = create_link(Store(), {"url": "https://example.com/"})[0] == 200
        trunc = len(truncate("x" * 50, 40))
    except Exception as e:
        sys.path.remove(str(d))
        return FAIL, "The app no longer imports.", notes + [f"{type(e).__name__}: {e}"]
    sys.path.remove(str(d))

    if crashed:
        bad.append("create_link still crashes on " + ", ".join(crashed) +
                   ". A payload is untrusted input, and the guard reads as defensive "
                   "without being it")
    elif nonstrings:
        bad.append("create_link accepts a non-string url: " + ", ".join(nonstrings))
    else:
        notes.append("non-string urls are rejected with a 400, not a stack trace")
    if blanks:
        bad.append("blank urls still get through: " + ", ".join(blanks))
    if not valid:
        bad.append("a valid url is now rejected -- the fix reached past the rule")
    elif not blanks:
        notes.append("blank rejected, valid accepted")
    if trunc != 40:
        bad.append(f"truncate('x'*50, 40) returns {trunc} characters, and its docstring "
                   'says "at most `limit` characters, ellipsis included". The commit '
                   'called this "tidied up while I was in there"')
    else:
        notes.append("truncate honours its own docstring again")

    if bad:
        return FAIL, "The suite is green. The evidence still is not.", notes + bad
    return PASS, "Audited, and every broken link in the chain repaired.", notes


# --------------------------------------------------------------------------
# lab 05 -- project memory
# --------------------------------------------------------------------------

REQUIRED_TOPICS = {
    "architecture": ("architecture", "structure", "layout", "modules"),
    "commands": ("command", "how to run", "running"),
    "conventions": ("convention", "style", "rules", "constraints"),
    "workflow": ("workflow", "process", "before you", "when you"),
}


def lab05(d):
    claude_md = d / "CLAUDE.md"
    if not claude_md.exists():
        return TODO, "No CLAUDE.md yet.", [
            "Write it yourself first, then ask for a review. /init writes a summary "
            "of the code; the value is in the constraints only you know.",
        ]

    text = claude_md.read_text()
    lines = text.strip().splitlines()
    headings = [l for l in lines if l.startswith("##")]
    notes, bad = [f"{len(lines)} lines, {len(headings)} sections"], []

    if len(lines) > 100:
        bad.append(f"{len(lines)} lines -- this is loaded into every session's context. "
                   "Under 100. If it needs more, it needs a scoped rule instead")
    if len(headings) < 5:
        bad.append(f"{len(headings)} sections -- aim for five: what this is, architecture, "
                   "commands, conventions, workflow")
    low = text.lower()
    for topic, words in REQUIRED_TOPICS.items():
        if not any(w in low for w in words):
            bad.append(f"nothing about {topic}")

    rules = sorted((d / ".claude" / "rules").glob("*.md")) if (d / ".claude" / "rules").is_dir() else []
    if not rules:
        bad.append("no .claude/rules/*.md -- the second half of the lab is one scoped rule, "
                   "so the advice arrives only when the matching file is open")
    else:
        scoped = False
        for r in rules:
            try:
                meta, body, _ = frontmatter(r)
            except ValueError as e:
                bad.append(f"{r.name}: {e}")
                continue
            if "paths" not in meta:
                bad.append(f"{r.name}: frontmatter parses but has no paths: key -- "
                           "without it the rule is not scoped to anything")
            elif not body.strip():
                bad.append(f"{r.name}: frontmatter but no rule under it")
            else:
                scoped = True
                notes.append(f"{r.name} scoped to {meta['paths']}")
        if scoped:
            notes.append("scoped rule parses")

    if bad:
        return FAIL, "Project memory exists but is not doing its job.", bad
    return PASS, "CLAUDE.md is short and complete, and one rule is scoped.", notes


# --------------------------------------------------------------------------
# lab 06 -- permissions
# --------------------------------------------------------------------------

def lab06(d):
    settings = d / ".claude" / "settings.json"
    if not settings.exists():
        return TODO, "No .claude/settings.json yet.", [
            "Deny is the only list that is not a convenience. Start there.",
        ]
    try:
        data = json.loads(settings.read_text())
    except json.JSONDecodeError as e:
        return FAIL, "settings.json is not valid JSON.", [str(e)]

    perms = data.get("permissions")
    if not isinstance(perms, dict):
        return FAIL, "No permissions object.", [
            'Shape: {"permissions": {"deny": [...], "allow": [...]}}',
        ]
    deny = perms.get("deny")
    if not isinstance(deny, list) or not deny:
        return FAIL, "permissions.deny is missing or empty.", [
            "The lab is the deny list. allow only saves you clicks; deny is the fence.",
        ]

    bad, notes = [], [f"{len(deny)} deny rules"]
    for rule in deny:
        if not isinstance(rule, str):
            bad.append(f"{rule!r} is not a string")
        elif not re.match(r"^[A-Z][A-Za-z]*\(.+\)$", rule):
            bad.append(f'"{rule}" is not shaped like Tool(pattern) -- '
                       'e.g. Read(.env) or Bash(git push *)')

    joined = " ".join(r for r in deny if isinstance(r, str))
    if not re.search(r"Read\(\s*\.?/?\.env\s*\)", joined) and ".env" not in joined:
        bad.append("nothing denies .env")
    else:
        if not re.search(r"\.env[.*]", joined):
            bad.append("`.env` is denied but its variants are not -- "
                       "`.env.local`, `.env.production` are separate files and a bare "
                       "Read(.env) does not cover them")
        else:
            notes.append(".env and its variants are denied")

    if bad:
        return FAIL, "The deny list has holes.", bad
    return PASS, "settings.json parses and the deny list covers the secrets.", notes


# --------------------------------------------------------------------------
# lab 07 -- skills and hooks
# --------------------------------------------------------------------------

def lab07(d):
    skills = sorted((d / ".claude" / "skills").glob("*/SKILL.md")) if (d / ".claude" / "skills").is_dir() else []
    hooks = sorted((d / ".claude" / "hooks").glob("*.sh")) if (d / ".claude" / "hooks").is_dir() else []
    if not skills and not hooks:
        return TODO, "No .claude/skills/ and no .claude/hooks/ yet.", [
            "A skill is what to do when asked. A hook is what happens whether or not it is asked.",
        ]

    bad, notes = [], []

    for skill in skills:
        try:
            meta, body, raw = frontmatter(skill)
        except ValueError as e:
            bad.append(f"{skill.parent.name}/SKILL.md: {e}")
            continue
        name = skill.parent.name
        desc = meta.get("description")
        if not meta.get("name"):
            bad.append(f"{name}: no name: in frontmatter")
        if not isinstance(desc, str) or not desc.strip():
            bad.append(f"{name}: no description: -- this is the only thing read at startup; "
                       "without it the skill never fires")
            continue
        m = re.search(r"^description:[ \t]*(.+)$", raw, re.M)
        if m and ": " in m.group(1) and not m.group(1).strip()[0] in "\"'|>":
            bad.append(f"{name}: the description contains an unquoted colon, so YAML read it "
                       f"as a nested mapping and it truncates at {desc[:40]!r}. Quote it")
        elif len(desc) < 60:
            bad.append(f"{name}: the description is {len(desc)} characters. It has to carry "
                       "both what the skill does and when to use it")
        elif "when" not in desc.lower():
            bad.append(f"{name}: the description says what it does but never when to use it")
        else:
            notes.append(f"{name}: frontmatter parses, description carries its trigger")
        if len(body.strip()) < 200:
            bad.append(f"{name}: the body is almost empty -- the procedure is the skill")

    if not skills:
        bad.append("no .claude/skills/*/SKILL.md")

    for hook in hooks:
        with tempfile.TemporaryDirectory() as empty:
            r = run(["/bin/bash", str(hook)], cwd=d, env={"PATH": empty},
                    stdin=json.dumps({"tool_input": {"file_path": str(d / "trainer/cli.py")}}))
        if r.returncode != 0:
            bad.append(f"{hook.name}: exits {r.returncode} when its tool is not installed. "
                       "A hook that fails on a machine without the tool turns every edit into "
                       "an error for someone who never asked for the check")
        else:
            notes.append(f"{hook.name}: exits 0 when the tool is absent")
        if not os.access(hook, os.X_OK):
            bad.append(f"{hook.name} is not executable (chmod +x)")

    if not hooks:
        bad.append("no .claude/hooks/*.sh")

    if bad:
        return FAIL, "Skill or hook is there but not yet correct.", bad
    return PASS, "Skill frontmatter parses and the hook degrades quietly.", notes


# --------------------------------------------------------------------------
# lab 09 -- subagents
# --------------------------------------------------------------------------

def lab09(d):
    agents = sorted((d / ".claude" / "agents").glob("*.md")) if (d / ".claude" / "agents").is_dir() else []
    if not agents:
        return TODO, "No .claude/agents/*.md yet.", [
            "A subagent is a fresh context with a narrow job and a reporting contract.",
        ]

    bad, notes, good = [], [], False
    for agent in agents:
        try:
            meta, body, _ = frontmatter(agent)
        except ValueError as e:
            bad.append(f"{agent.name}: {e}")
            continue
        problems = []
        if not meta.get("name"):
            problems.append("no name:")
        if not isinstance(meta.get("description"), str) or len(meta.get("description", "")) < 30:
            problems.append("no usable description: -- this is what decides when it is delegated to")
        tools = meta.get("tools")
        if tools is None:
            problems.append("no tools: -- an unrestricted subagent is just another session; "
                            "the narrowing is the point")
        else:
            listed = tools if isinstance(tools, list) else [t.strip() for t in str(tools).split(",")]
            if not listed or not all(listed):
                problems.append("tools: is empty")
            elif any(t.strip().lower() in ("edit", "write") for t in listed):
                notes.append(f"{agent.name}: note, it can write -- fine if you meant it")
        low = body.lower()
        if len(body.strip()) < 200:
            problems.append("the body is too thin to be a contract")
        elif "report" not in low:
            problems.append("the body never says what to report back -- without a reporting "
                            "contract you get whatever the subagent felt like summarising")
        if problems:
            bad.extend(f"{agent.name}: {p}" for p in problems)
        else:
            good = True
            notes.append(f"{agent.name}: frontmatter, tool list and reporting contract")

    if not good:
        return FAIL, "A subagent file exists but is not yet a contract.", bad
    return (PASS if not bad else FAIL), (
        "A subagent with a tool list and a reporting contract." if not bad
        else "One subagent is good; others have problems."), notes + bad


# --------------------------------------------------------------------------
# lab 10 / 11 / 13                                                 MANUAL
# --------------------------------------------------------------------------

def lab10(_d):
    return MANUAL, "A spec an agent can be held to.", [
        "Your spec states postconditions and invariants, not steps.",
        "You can point at the one it violated, and say so without rewriting the task.",
    ]


def lab11(_d):
    return MANUAL, "Break something and see whether the review names the layer.", [
        "You introduced a real defect -- an off-by-one, a swapped argument, a dropped fallback.",
        "The review named the layer it lives in, not just the line.",
        "You can say what it missed, too.",
    ]


def lab13(_d):
    return MANUAL, "Know where you stop.", [
        "You have a written stop list: the things you will not delegate, and why.",
        "You have one metric you will actually watch to know whether this is working.",
    ]


# --------------------------------------------------------------------------
# lab 12 -- landing in a codebase
# --------------------------------------------------------------------------

def lab12(d):
    # The fixture lives once, under exercises/. A solution only has to add the
    # write-up, so fall back to the fixture for the code checks.
    code = d if (d / "invoicing").is_dir() else ROOT / "exercises" / "lab12_landing"
    if not (code / "invoicing").is_dir():
        return TODO, "The legacy-service fixture is not here.", []

    notes, bad = [], []
    d, fixture = d, code
    if not (fixture / ".git").exists():
        notes.append("history not replayed yet -- run `bash make-history.sh` "
                     "(the commits are half the lab)")
    else:
        r = run(["git", "log", "--oneline"], cwd=fixture)
        notes.append(f"{len(r.stdout.strip().splitlines())} commits of history")

    r = run([sys.executable, "-m", "pytest", "-q"], cwd=fixture)
    if r.returncode != 0:
        bad.append("the fixture's own tests do not pass -- "
                   "did an edit slip in? " + (r.stdout or r.stderr).strip().splitlines()[-1][:160])
    else:
        notes.append("the fixture's 4 tests pass")

    orientation = d / "ORIENTATION.md"
    if not orientation.exists():
        return TODO, "No ORIENTATION.md yet.", notes + [
            "Write down only what you verified. Deleting the merely plausible is the exercise.",
        ]
    text = orientation.read_text()
    if len(text.split()) < 80:
        bad.append("ORIENTATION.md is very short -- it needs what the service does, where "
                   "execution starts, and one thing the map got wrong")
    modules = {p.name for p in fixture.rglob("*.py")}
    named = [m for m in modules if m in text]
    if not named:
        bad.append("it names no source file -- 'where execution starts' means a file and a function")
    else:
        notes.append(f"names {len(named)} source files, including {named[0]}")
    doubt = r"wrong|guess|inferr|incorrect|actually|in fact|turned out|could not verify|" \
            r"not verified|unverified|misleading|does not|is a lie|folklore|assumed"
    if not re.search(doubt, text, re.I):
        bad.append("nothing in it records a correction or an unverified claim -- the map was "
                   "right about everything? Spot-check it against the territory, and write "
                   "down which parts you could not confirm")

    if bad:
        return FAIL, "Orientation written, but not yet verified against the code.", notes + bad
    return PASS, "Fixture intact, and the orientation is checked rather than accepted.", notes


# --------------------------------------------------------------------------

LABS = [
    ("lab01_first_contact", "first contact", lab01),
    ("lab02_five_jobs", "the five jobs", lab02),
    ("lab03_session", "driving the session", lab03),
    ("lab04_audit", "auditing the evidence", lab04),
    ("lab05_memory", "project memory", lab05),
    ("lab06_permissions", "permissions", lab06),
    ("lab07_skills", "skills and hooks", lab07),
    ("lab09_subagents", "subagents", lab09),
    ("lab10_spec", "prompt to pull request", lab10),
    ("lab11_review", "review", lab11),
    ("lab12_landing", "landing in a codebase", lab12),
    ("lab13_limits", "when not to", lab13),
]

COLOUR = {PASS: "\033[32m", FAIL: "\033[31m", TODO: "\033[33m", MANUAL: "\033[36m"}
RESET = "\033[0m"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("labs", nargs="*", help="lab prefixes to check, e.g. lab05")
    ap.add_argument("--solutions", action="store_true",
                    help="check the reference answers instead of your work")
    ap.add_argument("--no-colour", action="store_true")
    args = ap.parse_args()

    base = ROOT / ("solutions" if args.solutions else "exercises")
    tint = (lambda s, _: s) if args.no_colour or not sys.stdout.isatty() else \
        (lambda s, st: f"{COLOUR[st]}{s}{RESET}")

    selected = [l for l in LABS
                if not args.labs or any(l[0].startswith(p) for p in args.labs)]
    if not selected:
        print(f"No lab matches {args.labs}.")
        return 2

    print(f"\n  Claude Code labs -- {base.name}\n")
    counts = dict.fromkeys((PASS, FAIL, TODO, MANUAL), 0)

    for folder, title, fn in selected:
        d = base / folder
        if not d.is_dir() and fn.__name__ not in ("lab01", "lab03", "lab10", "lab11", "lab13"):
            status, summary, details = TODO, f"{folder}/ is not there.", []
        else:
            try:
                status, summary, details = fn(d)
            except Exception as e:
                status, summary, details = FAIL, f"the check itself blew up: {type(e).__name__}: {e}", []
        counts[status] += 1
        print(f"  {tint(status.ljust(6), status)} {folder[:5]}  {title}")
        print(f"         {summary}")
        for line in details:
            print(f"           - {line}")
        print()

    print("  " + "  ".join(f"{n} {s.lower()}" for s, n in counts.items() if n))
    print()
    return 1 if counts[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
