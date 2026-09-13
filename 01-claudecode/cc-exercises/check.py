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


def template_left(text):
    """A placeholder from the shipped template that nobody replaced.

    Guarding on two hand-picked strings meant a student could fill the fields
    the checker names and leave the rest as literal angle brackets. Anything
    shaped like <several words> counts, but an autolink or an HTML tag does not.
    """
    for m in re.finditer(r"<([^<>\n]{3,})>", text):
        inner = m.group(1).strip()
        if inner.lower().startswith(("http", "www.", "mailto:", "/")):
            continue
        if " " in inner or "|" in inner:
            return m.group(0)
    return None


# --------------------------------------------------------------------------
# lab 00 -- the three scales
# --------------------------------------------------------------------------

def _replay(fixtures):
    """Put the fixture histories back if they are not there.

    They are generated, never committed: a .git directory inside this repository
    would reach a clone as an empty folder, so the script is the thing that ships
    and the history is built on arrival. Running it here means a fresh clone
    checks out and works, instead of failing on a setup step nobody read.
    """
    script = fixtures.parent / "make-history.sh"
    if not script.exists():
        return False
    run(["/bin/sh", str(script)], cwd=script.parent, timeout=60)
    return (fixtures / "alpha" / ".git").is_dir()


SIZE_METRICS = {
    "python files", "lines of code", "test files", "test functions", "directories",
}

SCALE_WORDS = ("doghouse", "cabin", "skyscraper")


DRIVER = """
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("_lab00_scales", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(json.dumps([module.measure(Path(p)) for p in sys.argv[2:]], default=str))
"""


def _measure(script, paths):
    """Run the student's measure() over these paths, out of process.

    Out of process because an import is arbitrary code: a sys.exit outside the
    __main__ guard is a BaseException that escapes every except in this file and
    aborts the whole run silently, and a loop at import hangs it with no output.
    A subprocess with a deadline turns both into an ordinary FAIL.
    """
    result = run([sys.executable, "-c", DRIVER, str(script), *[str(p) for p in paths]],
                 cwd=script.parent, timeout=25)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "no output")
                           .strip().splitlines()[-1][:160])
    return json.loads(result.stdout)


def _verdicts(text):
    """The scale word claimed under each fixture heading, in order."""
    out = []
    for block in re.split(r"^##\s+", text, flags=re.M)[1:]:
        m = re.search(r"\*\*Scale:\*\*\s*(.+)", block)
        if not m:
            continue
        said = m.group(1).strip().lower()
        named = [w for w in SCALE_WORDS if w in said]
        because = re.search(r"\*\*Because:\*\*\s*(.+)", block)
        out.append((named, (because.group(1).strip() if because else "")))
    return out


def lab00(d):
    notes_file = d / "SCALES.md"
    if not notes_file.exists():
        return TODO, "No SCALES.md yet.", [
            "Classify both fixtures before you go looking for evidence. Finding out "
            "your first instinct was wrong is most of the lab.",
        ]

    text = notes_file.read_text()
    left = template_left(text)
    if left:
        return TODO, f"SCALES.md still has {left} in it.", [
            "Run scales.py on both fixtures first. The reports being nearly identical "
            "is the thing you are explaining.",
        ]

    notes, bad = [], []

    # ---- 1. did they commit to two verdicts, with reasons? ----------------
    verdicts = _verdicts(text)
    placed = [(named, why) for named, why in verdicts if named]
    if len(placed) < 2:
        bad.append(f"{len(placed)} fixture(s) classified -- both alpha and beta need a "
                   "scale word under **Scale:**")
    for named, why in placed:
        if len(named) > 1:
            bad.append(f"one verdict names {' and '.join(named)} -- pick one")
        if len(why.split()) < 6:
            bad.append("a verdict has no reason under it, or a reason of a few words. "
                       "Say what would happen if you changed the behaviour tomorrow")
    if len(placed) == 2 and all(not b.startswith("one verdict") for b in bad):
        notes.append(" and ".join(n[0] for n, _ in placed) + ", with reasons")

    # ---- 2. three signals, and three distinct ones ------------------------
    section = text.split("cannot see", 1)
    listed = []
    if len(section) > 1:
        for line in section[1].splitlines():
            m = re.match(r"\s*\d+\.\s+(.*)", line)
            if m and m.group(1).strip():
                listed.append(m.group(1).strip())
            elif listed and line.startswith("##"):
                break
    if len(listed) < 3:
        bad.append(f"{len(listed)} coordination signal(s) written down, not 3")
    else:
        fingerprints = {re.sub(r"[^a-z ]", "", s.lower())[:40] for s in listed[:3]}
        if len(fingerprints) < 3:
            bad.append("two of the three signals are the same sentence twice")
        else:
            notes.append(f"{len(listed)} signals listed")

    # ---- 3. does scales.py now measure something that is not a size? ------
    script = d / "scales.py"
    fixtures = d / "fixtures"
    if not fixtures.is_dir():
        fixtures = ROOT / "exercises" / "lab00_scales" / "fixtures"
    if not script.exists():
        bad.append("scales.py is not in this folder")
    elif not (fixtures / "alpha" / ".git").is_dir() and not _replay(fixtures):
        bad.append("the fixtures have no history and make-history.sh did not put one "
                   "there -- the lab depends on it, and half the signal is in the log")
    else:
        import shutil

        try:
            alpha, beta, again = _measure(script, [fixtures / "alpha",
                                                   fixtures / "beta",
                                                   fixtures / "alpha"])
            # Copy the fixtures under different names. A metric that reads the
            # repository gives the same answer; one derived from the path does not.
            with tempfile.TemporaryDirectory() as tmp:
                elsewhere = Path(tmp) / "renamed-doghouse"
                shutil.copytree(fixtures / "alpha", elsewhere)
                moved = _measure(script, [elsewhere])[0]
        except Exception as e:
            bad.append(f"scales.py no longer runs: {type(e).__name__}: {e}")
        else:
            added = [k for k in beta if k not in SIZE_METRICS]
            if not added:
                bad.append("scales.py still measures only the five sizes it shipped with. "
                           "Teach it one of your signals")
            for k in added:
                notes.append(f"added: {k} (alpha {alpha.get(k)}, beta {beta.get(k)})")

            def steady(k):
                return alpha.get(k) == again.get(k) == moved.get(k)

            def real(k):
                a, b = alpha.get(k), beta.get(k)
                return not (a != a or b != b)          # nan separates from itself

            base = {(alpha.get(m), beta.get(m)) for m in SIZE_METRICS}
            separating = [k for k in added
                          if real(k) and steady(k)
                          and alpha.get(k) != beta.get(k)
                          and (alpha.get(k), beta.get(k)) not in base]

            if added and not separating:
                for k in added:
                    if not real(k):
                        bad.append(f"{k} is not a number that compares -- nan is unequal "
                                   "to itself, so it separates nothing")
                    elif alpha.get(k) != again.get(k):
                        bad.append(f"{k} gives a different answer each run, so it is not "
                                   "measuring the project")
                    elif alpha.get(k) != moved.get(k):
                        bad.append(f"{k} changes when the same project is copied under "
                                   "another name, so it is measuring the path")
                    elif (alpha.get(k), beta.get(k)) in base:
                        bad.append(f"{k} reports exactly what one of the five size "
                                   "metrics reports -- renaming a size is not a signal")
                    else:
                        bad.append(f"{k} gives alpha and beta the same value, so it "
                                   "cannot be what tells them apart. Pick a signal that "
                                   "is present in one and absent in the other")

    if bad:
        return FAIL, "Measured, but the coordination line is not drawn yet.", notes + bad
    return PASS, "Both placed with reasons, and the tool can now see past size.", notes


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

def _tokens(value):
    """Read a token count a human typed. Accepts 12,480 / 12480 / 12.5k / ~12k."""
    text = value.strip().lower().replace(",", "").replace("~", "").replace(" ", "")
    m = re.match(r"^(\d+(?:\.\d+)?)(k)?$", text)
    if not m:
        return None
    number = float(m.group(1))
    return int(number * 1000) if m.group(2) else int(number)


def _row(text, label):
    """The number in the table row whose left cell mentions `label`."""
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().strip("*") for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and label in cells[0].lower():
            return _tokens(cells[-1])
    return None


def lab03(d):
    notes_file = d / "WINDOW.md"
    if not notes_file.exists():
        return TODO, "No WINDOW.md yet.", [
            "Read /context before you ask anything. Once you have asked, the baseline "
            "is gone and the lab starts with a guess.",
        ]

    text = notes_file.read_text()
    left = template_left(text)
    if left:
        return TODO, f"WINDOW.md still has {left} in it.", [
            "python3 window.py sample gives you the estimate. The rest are readings "
            "you take yourself.",
        ]

    notes, bad = [], []

    baseline = _row(text, "baseline")
    estimate = _row(text, "estimate for")
    after = _row(text, "after reading")
    cost = _row(text, "cost")

    missing = [name for name, value in
               (("baseline", baseline), ("estimate", estimate),
                ("after", after), ("cost", cost)) if value is None]
    if missing:
        bad.append("no number read for: " + ", ".join(missing)
                   + " -- put a plain token count in the right-hand cell")
    else:
        notes.append(f"baseline {baseline:,}, after {after:,}, cost {cost:,}")

        # ---- the arithmetic has to agree, or a number was copied not measured
        if abs((after - baseline) - cost) > max(50, 0.02 * max(cost, 1)):
            bad.append(f"cost is written as {cost:,} but after - baseline is "
                       f"{after - baseline:,}. One of the three was not measured")
        if after <= baseline:
            bad.append("after is not larger than baseline -- reading three files cannot "
                       "cost nothing")

        # ---- and the error has to be the error
        m = re.search(r"\*\*Estimate error:\*\*\s*([-\d.,]+)\s*%", text)
        if not m:
            bad.append("no estimate error as a percentage")
        elif cost:
            claimed = float(m.group(1).replace(",", ""))
            real = abs(estimate - cost) / cost * 100
            if abs(claimed - real) > 5:
                bad.append(f"the error is written as {claimed:.0f}% but "
                           f"|{estimate:,} - {cost:,}| / {cost:,} is {real:.0f}%")
            else:
                notes.append(f"estimate off by {real:.0f}%")

    # ---- the second failure mode, which is the half people skip -----------
    tail = text.split("no error message", 1)
    if len(tail) < 2:
        bad.append("the pollution half of the lab is missing from WINDOW.md")
    else:
        section = tail[1]
        # The whole paragraph, not the first line of it: people wrap their prose.
        sentence = re.search(
            r"\*\*Full is not the same as polluted, because:\*\*\s*(.+?)(?:\n\s*\n|\Z)",
            section, re.S)
        if not sentence or len(sentence.group(1).split()) < 8:
            bad.append("no sentence separating a full window from a polluted one")
        else:
            said = sentence.group(1).lower()
            if "full" not in said or "pollut" not in said.replace("polluted", "pollut"):
                bad.append("the sentence never contrasts the two states it is about")
            else:
                notes.append("both failure modes named")
        if not re.search(r"\*\*Was the answer worse:\*\*\s*\S", section):
            bad.append("you did not record whether the polluted answer got worse -- "
                       "no is a finding too, and worth writing down")

    if bad:
        return FAIL, "Readings taken, but they do not hold together yet.", notes + bad
    return PASS, "Measured, checked against the estimate, and polluted on purpose.", notes


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

# --------------------------------------------------------------------------
# lab 05 -- project memory
#
# Replaces the existing block in check.py from `# SPLICE NOTE, delete this paragraph once applied: replace check.py from line
# 600, the first of the two duplicated lab 05 banner comments, down to the end
# of def lab05(d), with this whole file. Both banners go and the one below
# replaces them. Unchanged from the shipped version: the topics table and
# sections 1 and 2 of lab05(). New module-level names, none of which collide
# with anything already in check.py: INNOCENT, _yes, _region, _fields, _field,
# _sessions, _stems, _echoes, _hook_cmd, _hooks_in.

# --------------------------------------------------------------------------
# lab 05 -- project memory
# --------------------------------------------------------------------------
REQUIRED_TOPICS = {
    "architecture": ("architecture", "structure", "layout", "modules"),
    "commands": ("command", "how to run", "running"),
    "conventions": ("convention", "style", "rules", "constraints"),
    "workflow": ("workflow", "process", "before you", "when you"),
}

# Paths the gate has no business refusing. The two-path probe the first draft
# used was passed by `case $payload in *navigation*) exit 0 ;; esac; exit 2`,
# which refuses every other file in the project.
INNOCENT = (
    "trainer/navigation.py",
    "trainer/cli.py",
    "trainer/storage.py",
    "tests/test_storage.py",
)

_NO_WORDS = (r"did not|didn't|does not|doesn't|never|unchanged|untouched|"
             r"no change|prevented|blocked|refused|still reads|is empty|"
             r"was not|wasn't")
_YES_WORDS = r"it did|it was|landed|went through|happened|was made|did happen"


def _yes(value):
    """Read a yes/no answer a human typed. None when it is neither.

    Humans type backticks, quote the reading, and answer in sentences. The
    label is the question; anything that clearly answers it counts.
    """
    text = re.sub(r"^[\s*`\"'(]+", "", value.strip().lower())
    text = re.sub(r"^(it\s+)?(was|is|did|does|has|had|were)\s+", "", text)
    if re.match(r"^(yes|y\b|true|obeyed|present|loaded|listed|there|shown)", text):
        return True
    if re.match(r"^(no\b|not\b|n\b|nope|false|never|absent|missing|gone|none|"
                r"unchanged|prevented|blocked|refused|nothing)", text):
        return False
    if re.search(_NO_WORDS, text):
        return False
    if re.search(_YES_WORDS, text):
        return True
    return None


def _region(text, pattern):
    """The slice under the first heading matching pattern. None if there is none."""
    heads = list(re.finditer(r"^#{2,}[^\n]*$", text, re.M))
    for i, h in enumerate(heads):
        if re.search(pattern, h.group(0), re.I):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            return text[h.end():end]
    return None


def _fields(text):
    """(label, value) for every `**Label:** value` line. Bold is optional."""
    out = []
    for m in re.finditer(r"^[ \t>]*\**\s*([^:\n|*]{2,80}?)\s*:\**[ \t]*(\S.*)$",
                         text, re.M):
        out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def _field(text, pattern):
    """The value of the first labelled line whose label matches pattern."""
    for label, value in _fields(text):
        if re.search(pattern, label, re.I):
            return value
    return None


def _sessions(text):
    """Rows of the compliance table: (label, obeyed, what it did instead).

    Scoped by the caller to the Proof 1 region: any other table with a numeric
    first column -- the /context readings step 6 asks for, for instance -- is
    not a session and must not be counted as one.
    """
    out = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        label = re.match(r"^\**\s*(?:session|run|try)?\s*(\d+)\s*\**$",
                         cells[0], re.I)
        if not label:
            continue
        out.append((label.group(1), _yes(cells[1]), " ".join(cells[2:]).strip()))
    return out


def _stems(text):
    """Four-letter stems, so `edits` and `editing` are the same instruction."""
    return {w[:4] for w in re.findall(r"[a-z]{4,}", text.lower())}


def _echoes(claim, source):
    """Does the instruction in the table appear in the file it claims to live in?"""
    stems = _stems(claim)
    if len(stems) < 2:
        return True  # too short to judge; the length check already says so
    return len(stems & _stems(source)) >= 2


def _hook_cmd(hook):
    """How to run a student's hook. Their shebang first, then the suffix."""
    try:
        first = hook.read_text(errors="replace").splitlines()[0]
    except (OSError, IndexError, UnicodeError):
        first = ""
    if first.startswith("#!"):
        words = first[2:].strip().split()
        if words:
            return words + [str(hook.resolve())]
    if hook.suffix == ".py":
        return [sys.executable, str(hook.resolve())]
    return ["/bin/bash", str(hook.resolve())]


def _hooks_in(hook_dir):
    """Every hook script, whatever language it is written in."""
    if not hook_dir.is_dir():
        return []
    skip = {".md", ".json", ".txt", ".yaml", ".yml", ".log"}
    return sorted(h for h in hook_dir.glob("*")
                  if h.is_file() and h.suffix not in skip
                  and not h.name.startswith("."))


def lab05(d):
    claude_md = d / "CLAUDE.md"
    if not claude_md.exists():
        return TODO, "No CLAUDE.md yet.", [
            "Write it yourself first, then ask for a review. /init writes a summary "
            "of the code; the value is in the constraints only you know.",
        ]

    # ---- 1. is the always-loaded file short and complete? ----------------
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

    # ---- 2. is one rule scoped to the files it is about? -----------------
    rules = sorted((d / ".claude" / "rules").glob("*.md")) if (d / ".claude" / "rules").is_dir() else []
    rule_text = "\n".join(r.read_text() for r in rules)
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

    # ---- 3. three homes, and evidence for each ---------------------------
    # The fixture lives once, under exercises/. A solution only adds the hook and
    # the write-up, so fall back to the fixture for the paths the hook is fed.
    code = d if (d / "trainer").is_dir() else ROOT / "exercises" / "lab05_memory"
    hooks = _hooks_in(d / ".claude" / "hooks")
    homes_file = d / "HOMES.md"
    if not homes_file.exists():
        return TODO, "Placed, but nothing has measured the placement yet.", notes + [
            "Three homes, three proofs: the CLAUDE.md one is obeyed most of the time, "
            "the scoped one is not always loaded, the hook one does not ask.",
        ]
    homes = homes_file.read_text()
    if "<yes/no>" in homes or "<the sentence you" in homes:
        return TODO, "HOMES.md is still the template.", notes + [
            "Take the readings while they are on the screen. The ones reconstructed "
            "afterwards are the argument you already believed.",
        ]

    # ---- 4. the placement table: three instructions, three destinations ---
    # Read the Kind column as well as the Home column, and match a bare filename
    # against the rules and hooks actually on disk, so the columns can be in any
    # order and `testing.md` still reads as a rule.
    rule_names = {n for r in rules for n in (r.name.lower(), r.stem.lower())}
    hook_names = {n for h in hooks for n in (h.name.lower(), h.stem.lower())}
    KINDS = {"advisory": "CLAUDE.md", "scoped": "rule", "enforced": "hook"}

    def home_of(cell):
        c = cell.lower()
        if "claude.md" in c:
            return "CLAUDE.md"
        if "rules" in c or c in rule_names:
            return "rule"
        if ("hook" in c or "settings" in c or "permission" in c or c in hook_names
                or re.fullmatch(r"[\w./-]+\.(sh|py|js|ts)", c)):
            return "hook"
        return None

    placed = {}
    table = _region(homes, r"placement|the homes|where") or homes
    for line in table.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().strip("*`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or all(set(c) <= set("-: ") for c in cells):
            continue
        kinds = [KINDS[c.lower()] for c in cells if c.lower() in KINDS]
        homes_hit = [h for h in (home_of(c) for c in cells) if h]
        where = homes_hit[0] if homes_hit else (kinds[0] if kinds else None)
        if not where:
            continue
        rest = [c for c in cells
                if home_of(c) is None and c.lower() not in KINDS]
        claim = max(rest, key=lambda c: len(c.split())) if rest else ""
        placed.setdefault(where, claim)

    missing = [h for h in ("CLAUDE.md", "rule", "hook") if h not in placed]
    if missing:
        bad.append(f"the placement table names no {', no '.join(missing)} row -- three "
                   "instructions in three homes, and the third one is the exercise")
    if len(set(placed.values())) < len(placed):
        bad.append("two rows carry the same instruction -- placing one sentence twice "
                   "does not compare anything")
    for home, claim in placed.items():
        if len(claim.split()) < 3:
            bad.append(f"the {home} row does not say what the instruction is")
    if "CLAUDE.md" in placed and not _echoes(placed["CLAUDE.md"], text):
        bad.append("nothing in CLAUDE.md looks like the instruction the CLAUDE.md row "
                   "names -- the table is a record of where things are, not where they "
                   "should be")
    if "rule" in placed and rules and not _echoes(placed["rule"], rule_text):
        bad.append("nothing in your .claude/rules/ files looks like the instruction the "
                   "scoped row names")
    if not missing and not bad:
        notes.append("three instructions, three homes")

    # ---- 5. proof one: advisory means most of the time --------------------
    p1 = _region(homes, r"proof\s*1|advis|complian")
    rows = _sessions(p1 if p1 is not None else homes)
    if p1 is None:
        rows = [r for r in rows if r[1] is not None]
    claim = (re.search(r"complian[^:\n]*:?\**\s*\**\s*(\d+)\s*(?:of|/|out of)\s*(\d+)",
                       p1 if p1 is not None else homes, re.I)
             or re.search(r"complian[^:\n]*:?\**\s*\**\s*(\d+)\s*(?:of|/|out of)\s*(\d+)",
                          homes, re.I))
    if len(rows) < 3:
        bad.append(f"{len(rows)} session rows under Proof 1, not 3 -- one run tells you "
                   "the instruction can be followed, which you already assumed")
    elif any(obeyed is None for _, obeyed, _ in rows):
        bad.append("a session row does not say yes or no -- 'partly' is the answer "
                   "you get when the request was not the same request")
    else:
        obeyed = [r for r in rows if r[1]]
        notes.append(f"{len(obeyed)} of {len(rows)} sessions obeyed the CLAUDE.md rule")
        if not claim:
            bad.append("no compliance line under the table -- n of 3, in your own hand, "
                       "so the count and the rows can disagree out loud")
        elif int(claim.group(1)) != len(obeyed) or int(claim.group(2)) != len(rows):
            bad.append(f"the table shows {len(obeyed)} of {len(rows)} but the line under "
                       f"it claims {claim.group(1)} of {claim.group(2)}")
        for label, was, instead in rows:
            if not was and len(instead.split()) < 3:
                bad.append(f"session {label} says no and stops there -- what it did "
                           "instead is the part that tells you whether the instruction "
                           "was ignored or was never relevant")
    request = _field(p1 if p1 is not None else homes, r"request|prompt|asked|repeat")
    if not request or len(request.split()) < 4:
        bad.append("the repeated request is not written down, so nobody can tell "
                   "whether the three sessions were given the same thing")

    # ---- 6. proof two: scoped means sometimes ----------------------------
    p2 = _region(homes, r"proof\s*2|scoped")
    readings = [(lbl, _yes(v)) for lbl, v in _fields(p2 if p2 is not None else homes)
                if _yes(v) is not None]
    if p2 is None or len(readings) < 2:
        bad.append("the two /context readings for the scoped rule are not both there -- "
                   "one with no matching file in play, one with")
    elif readings[0][1] == readings[1][1]:
        bad.append("the rule reads the same both times, so nothing was demonstrated. "
                   "If it really is loaded with no tests/ file in play, its paths: key "
                   "is matching more than you think -- check the glob")
    else:
        notes.append("the scoped rule appears and disappears with its path")
    trigger = _field(p2 if p2 is not None else homes, r"appear|made it|trigger|loaded it")
    if not trigger or len(trigger.split()) < 3:
        bad.append("nothing says what made the rule load -- name the file")

    # ---- 7. proof three: enforcement is not a matter of opinion ----------
    # The claim under test is that the gate refuses one path and nothing else,
    # and that it says the same thing every time it is asked. Two payloads
    # cannot tell an allow-list from a deny-list, so send several, and send the
    # protected one twice.
    protected = code / "trainer" / "lines.py"
    outside = Path(tempfile.gettempdir()) / "lab05-scratch" / "notes.md"
    observed = []
    diagnosed = False   # the hook's behaviour already has a better name than 'silent'

    def probe(hook, path):
        payload = {"session_id": "lab05", "cwd": str(code),
                   "hook_event_name": "PreToolUse", "tool_name": "Edit",
                   "tool_input": {"file_path": str(path),
                                  "old_string": "a", "new_string": "b"}}
        return run(_hook_cmd(hook), cwd=code,
                   env={"CLAUDE_PROJECT_DIR": str(code)},
                   stdin=json.dumps(payload), timeout=30)

    if not hooks:
        bad.append("no .claude/hooks/ script -- without a mechanism the third proof is "
                   "an assertion, which is what the other two homes already were")
    for hook in hooks:
        if not os.access(hook, os.X_OK):
            bad.append(f"{hook.name} is not executable (chmod +x) -- a hook the shell "
                       "will not run is a file, not a guarantee")
        try:
            first = probe(hook, protected)
            innocent = [(p, probe(hook, code / p)) for p in INNOCENT]
            innocent.append((str(outside), probe(hook, outside)))
            again = probe(hook, protected)
        except subprocess.TimeoutExpired:
            bad.append(f"{hook.name} hung on a PreToolUse payload -- it runs before "
                       "every matching edit, so a hook that waits is a hook that stops "
                       "the session")
            continue

        codes = [first.returncode] + [r.returncode for _, r in innocent]
        if set(codes) == {127}:
            diagnosed = True
            bad.append(f"{hook.name} exits 127 on every path -- something it shells "
                       "out to is not installed here. The prompt asks for a hook that "
                       "depends on nothing that is not already on the machine")
            continue

        refused = [f"{p} ({r.returncode})" for p, r in innocent if r.returncode != 0]
        if refused:
            bad.append(f"{hook.name} refuses {refused[0]} too -- a gate that refuses "
                       "everything gets switched off in a week, and then it protects "
                       "nothing. All of: " + ", ".join(p for p, _ in innocent))
        if again.returncode != first.returncode:
            bad.append(f"{hook.name} answers {first.returncode} and then "
                       f"{again.returncode} for the same payload -- the decision is "
                       "coming from state somewhere, not from the path it was handed")

        if first.returncode == 0:
            deny = "permissiondecision" in (first.stdout or "").lower()
            if deny:
                diagnosed = True
                bad.append(f"{hook.name} denies through the JSON permissionDecision "
                           "route and exits 0. That is a real refusal; this lab asks "
                           "for the other one, because exit 2 and stderr are what you "
                           "can read without a running session")
            continue
        observed.append(first.returncode)
        if first.returncode == 127:
            bad.append(f"{hook.name} exits 127 -- something it shells out to is not "
                       "installed here. The prompt asks for a hook that depends on "
                       "nothing that is not already on the machine")
        elif first.returncode != 2:
            bad.append(f"{hook.name} exits {first.returncode} on trainer/lines.py, so "
                       "the edit goes through anyway. Exit 2 is the code a PreToolUse "
                       "hook stops a tool call with")
        elif not first.stderr.strip():
            bad.append(f"{hook.name} exits 2 but says nothing on stderr -- stderr is what "
                       "comes back into the session, so a silent block looks like a bug")
        elif not refused and again.returncode == first.returncode:
            notes.append(f"{hook.name} exits 2 on trainer/lines.py, 0 on "
                         f"{len(innocent)} other paths, and twice the same")
    if hooks and not observed and not diagnosed:
        bad.append("no hook exits non-zero on an edit to trainer/lines.py -- that file "
                   "is a transcription and the suite cannot catch a corruption of it, "
                   "since every navigation test compares LINES to itself")

    # settings.json is where a script becomes a mechanism. Walk it: a note
    # mentioning PreToolUse is not a registration.
    settings = d / ".claude" / "settings.json"
    if hooks and not settings.exists():
        bad.append("nothing registers the hook -- .claude/settings.json is where a "
                   "script becomes a mechanism, and without a PreToolUse entry it runs "
                   "only when you run it yourself")
    elif hooks:
        try:
            config = json.loads(settings.read_text())
        except json.JSONDecodeError as e:
            config = {}
            bad.append(f"settings.json is not valid JSON, so no hook is registered: {e}")
        if not isinstance(config, dict):
            config = {}
        entries = [e for e in ((config.get("hooks") or {}).get("PreToolUse") or [])
                   if isinstance(e, dict)]
        commands = [str(h.get("command", "")) for e in entries
                    for h in (e.get("hooks") or []) if isinstance(h, dict)]
        matchers = " ".join(str(e.get("matcher", "")) for e in entries)
        wired = []
        for cmd in commands:
            cmd = cmd.replace("${CLAUDE_PROJECT_DIR}", str(d))
            cmd = cmd.replace("$CLAUDE_PROJECT_DIR", str(d))
            for token in cmd.split():
                p = Path(token.strip("\"'"))
                p = p if p.is_absolute() else d / p
                if p.is_file() and p.resolve() in {h.resolve() for h in hooks}:
                    wired.append(p.name)
        if not entries and settings.exists():
            bad.append("settings.json has no hooks.PreToolUse array, so nothing runs "
                       "the script -- a note saying you will wire it up is the advisory "
                       "home again, which is the one you were moving away from")
        elif entries and not wired:
            bad.append("the PreToolUse entry does not name a hook file that exists -- "
                       "commands: " + (", ".join(commands) or "(none)"))
        elif entries and matchers.strip() and not re.search(r"Edit|Write|\*", matchers):
            bad.append(f"the PreToolUse matcher ({matchers.strip()}) selects no tool "
                       "that writes a file, so the gate watches calls that cannot "
                       "reach trainer/lines.py")
        elif entries:
            notes.append(f"PreToolUse runs {wired[0]} on {matchers.strip() or 'every tool'}")

    p3 = _region(homes, r"proof\s*3|enforc") or homes
    written = _field(p3, r"exit code|exit status|the code")
    happened = _field(p3, r"did the edit|edit happen|did it happen|outcome")
    digits = re.search(r"-?\d+", written) if written else None
    if not digits:
        bad.append("no exit code recorded for the blocked edit -- the number the hook "
                   "answered with, copied off your own screen")
    elif int(digits.group(0)) == 0:
        bad.append("HOMES.md records exit 0 for the edit you wanted refused -- exit 0 is "
                   "the hook allowing it")
    elif observed and int(digits.group(0)) not in observed:
        bad.append(f"HOMES.md records exit {digits.group(0)}, but the hook exits "
                   f"{observed[0]} here")
    if happened is None or _yes(happened) is not False:
        bad.append("the write-up does not say the edit was prevented -- open the file and "
                   "look, rather than taking the transcript's word for it")
    asked = _field(p3, r"edit i asked|request|asked for|prompt")
    if not asked or len(asked.split()) < 4:
        bad.append("the refused request is not written down")

    # ---- 8. did the reason transfer? -------------------------------------
    heads = list(re.finditer(r"^##+[^\n]*$", homes, re.M))
    named = [h for h in heads
             if re.search(r"measur|taught|learn|conclu|what i", h.group(0), re.I)]
    anchor = named[-1] if named else (heads[-1] if heads else None)
    tail = homes[anchor.end():].strip() if anchor else ""
    vocabulary = {w for w in re.findall(r"[a-z']{3,}", tail.lower())}
    if len(tail.split()) < 40:
        bad.append("the closing paragraph is missing or a sentence long -- say which of "
                   "the three outcomes could have gone the other way, and what that "
                   "costs the instruction you care about most")
    elif len(vocabulary) < 20:
        bad.append(f"the closing paragraph is {len(tail.split())} words of "
                   f"{len(vocabulary)} distinct ones -- that is a shape, not a reading")
    elif not re.search(r"guarantee|enforc|mechanism|block|refus|impossible|cannot|"
                       r"advice|advisor|influenc", tail, re.I):
        bad.append("the closing paragraph never reaches the distinction it measured: "
                   "context influences, mechanisms enforce")

    if bad:
        return FAIL, "Three homes, but the evidence does not hold up.", notes + bad
    return PASS, "Short memory, a scoped rule, and a third instruction that refuses.", notes


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
    hook_dir = d / ".claude" / "hooks"
    skills = sorted((d / ".claude" / "skills").glob("*/SKILL.md")) \
        if (d / ".claude" / "skills").is_dir() else []
    scripts = sorted(p for p in hook_dir.glob("*")
                     if p.is_file() and p.name != "__init__.py") if hook_dir.is_dir() else []
    if not skills and not scripts:
        return TODO, "No .claude/skills/ and no .claude/hooks/ yet.", [
            "A skill is what to do when asked. A hook is what happens whether or not it is asked.",
            "ROUTING.md is waiting for the three states, and the middle one has to be negative.",
        ]

    # The trainer package lives once, under exercises/. A solution only adds
    # .claude/ and the write-up, so fall back to the fixture for the source the
    # hooks are fed.
    code = d if (d / "trainer").is_dir() else ROOT / "exercises" / "lab07_skills"

    notes, bad = [], []
    descriptions = []

    STOP = {
        "the", "and", "for", "with", "when", "this", "that", "from", "into", "are",
        "was", "were", "user", "users", "use", "used", "uses", "using", "ask",
        "asks", "asked", "asking", "its", "you", "your", "yours", "not", "but",
        "any", "all", "has", "have", "had", "been", "being", "which", "what",
        "where", "whether", "their", "there", "them", "they", "then", "than",
        "will", "would", "can", "could", "should", "about", "only", "also",
        "more", "most", "other", "some", "such", "each", "just", "very", "over",
        "under", "out", "off", "one", "two", "get", "gets", "give", "gives",
        "make", "makes", "want", "wants", "need", "needs", "say", "says", "said",
        "how", "why", "who", "whom", "here", "does", "did", "doing", "these",
        "those", "still", "even", "ever", "every", "both", "own", "same",
    }

    def content_words(text):
        return {w for w in re.findall(r"[a-z]{3,}", text.lower()) if w not in STOP}

    # ---- 1. does the description survive YAML, and does it route? --------
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
        descriptions.append(desc)
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
        # The body is the procedure. It is read only after the skill is chosen,
        # so nothing above this tells you whether there is one.
        if len(body.strip()) < 200:
            bad.append(f"{name}: the body is almost empty -- the procedure is the skill")
        elif not re.search(r"coverage|untested|test|pytest|branch|line", body, re.I):
            bad.append(f"{name}: the body never mentions tests, coverage or branches. "
                       "Whatever else it is, it is not the procedure the description "
                       "promises")
        elif not (re.search(r"^[ \t]*\d+[.)]", body, re.M) or "`" in body):
            bad.append(f"{name}: the body has no steps and no commands in it. A skill is "
                       "a procedure someone can follow, not a description of one")

    if not skills:
        bad.append("no .claude/skills/*/SKILL.md")

    # ---- 2. was the routing tested by breaking it? ----------------------
    routing = d / "ROUTING.md"
    if not routing.exists():
        bad.append("no ROUTING.md -- a description you never broke on purpose is a "
                   "description you are only assuming works")
    else:
        text = routing.read_text()
        if "<fired /" in text or "<the sentence you typed" in text:
            bad.append("ROUTING.md is still the template. Three states of one description, "
                       "and the middle one has to be a negative result you actually saw")
        else:
            def said(*labels):
                """The value written against a bold label, however it is punctuated.

                The colon may sit inside or outside the bold markers, the label may
                be a heading instead, the value may start on the next line, and the
                capture stops at the next label -- a file written without blank
                lines must not let the first state swallow the rest of the document.
                """
                for label in labels:
                    m = re.search(r"^[ \t]*(?:[-*+][ \t]*)?(?:\*\*|\#{1,6}[ \t]*)[^*\n]*?"
                                  + label + r"[^*\n]*(?:\*\*)?[ \t]*:?[ \t]*(.*)$",
                                  text, re.M | re.I)
                    if not m:
                        continue
                    tail = re.split(r"\n[ \t]*\n|\n[ \t]*\*\*|\n[ \t]*#",
                                    text[m.end():], maxsplit=1)[0]
                    return " ".join((m.group(1) + " " + tail).split())
                return ""

            def state(number, *phrases):
                return said(r"(?:state[ \t]*)?" + str(number) + r"[ \t]*[.):–—-]",
                            *phrases)

            NEG = r"(?:\bnot\b|n't\b|\bnever\b|\bnothing\b|\bno\b|\bfailed to\b|\bwithout\b)"
            ACT = (r"(?:fire[sd]?|firing|trigger(?:ed|s|ing)?|select(?:ed|s)?|selection|"
                   r"cho(?:se|sen|oses)?|pick(?:ed|s)?|ran|runs|invoke[sd]?|invoked|"
                   r"activat(?:ed|es)?|dispatch(?:ed)?|rout(?:ed|es)?)")

            def score(clause):
                if re.search(NEG + r"[^.]{0,40}?" + ACT, clause, re.I):
                    return "no"
                if re.search(r"^\W*no\b|^\W*nope\b", clause, re.I):
                    return "no"
                if re.search(ACT, clause, re.I) or re.search(r"^\W*yes\b", clause, re.I):
                    return "yes"
                return ""

            def verdict(value):
                """Read the outcome, not the first negative word in the sentence.

                A student who writes "did not fire on the first attempt, so I added
                the phrase and then it fired" ran a better experiment than the
                reference answer, and must not be marked down for saying so.
                """
                clauses = [c for c in re.split(r";|--|—|–|,|\.\s", value) if c.strip()]
                if not clauses:
                    return ""
                first = score(clauses[0])
                last = ""
                for clause in reversed(clauses):
                    last = score(clause)
                    if last:
                        break
                if first and last and first != last:
                    ending = clauses[-1] if score(clauses[-1]) == last else value
                    if re.search(r"\b(then|after|afterwards|eventually|finally|second|"
                                 r"again|retry|retried|once|now)\b", ending, re.I):
                        return last
                return first or last

            named = verdict(state(1, "invoked by name", "by name"))
            generic = verdict(state(2, "helps with code", "generic"))
            rewritten = verdict(state(3, "rewritten in the words", "rewritten in words",
                                      "spoken words"))
            if named != "yes":
                bad.append("ROUTING.md does not record the skill firing when it was named. "
                           "If naming it does not work the file is the bug, not the "
                           "description -- fix that before testing the routing")
            if generic == "no":
                notes.append("the generic description stopped routing")
            elif generic:
                # Selection is probabilistic. A student who honestly watches the
                # generic description fire anyway has made an observation, not a
                # mistake, and a checker that fails them teaches them to write down
                # the result it wanted. The hint stays; the accusation does not.
                notes.append("the generic description fired anyway -- if that surprises "
                             "you, check the skill was not named in the question and that "
                             "state 2 ran in a fresh session, because frontmatter is read "
                             "at startup")
            if rewritten != "yes":
                bad.append("ROUTING.md does not record the rewrite firing again. Until it "
                           "fires on a question that never names it, the rewrite is not yet "
                           "in the words anyone would use")
            if named == "yes" and generic == "no" and rewritten == "yes":
                notes.append("routing recorded in three states, and the middle one is negative")

            # One question, asked three times, and it never names the skill. Three
            # typed verdicts with no question under them are a guess, not a run.
            question = said("question I asked", "question")
            if len(question.split()) < 5:
                bad.append("ROUTING.md does not record the question you typed. The three "
                           "states only mean something if it was the same sentence every "
                           "time, so it has to be in the file verbatim")
            else:
                named_in = [s.parent.name for s in skills
                            if len(s.parent.name) >= 8 and (
                                s.parent.name.lower() in question.lower()
                                or s.parent.name.replace("-", " ").replace("_", " ").lower()
                                in question.lower())]
                if named_in:
                    bad.append(f"the question in ROUTING.md names {named_in[0]}. Naming it is "
                               "state 1 and nothing else -- states 2 and 3 test whether the "
                               "description gets chosen, which a question that names the "
                               "skill never asks")

            missing = said("generic one was missing", "was missing", "missing")
            if len(missing.split()) < 12:
                bad.append("ROUTING.md does not say what the generic description was missing. "
                           "Name the words in your question that the rewrite matches and "
                           "`helps with code` does not; that sentence is the finding")

            quoted = said("rewritten description", "in full")
            quoted_words = content_words(quoted)
            best = (0.0, 0.0)
            for desc in descriptions:
                live = content_words(desc)
                if not quoted_words or not live:
                    continue
                shared = len(quoted_words & live)
                pair = (shared / len(quoted_words), shared / len(live))
                if min(pair) > min(best):
                    best = pair
            from_live, of_live = best
            if not quoted_words:
                bad.append("ROUTING.md does not paste the winning description in full -- the "
                           "record is worth nothing if the wording is not in it")
            elif from_live < 0.6:
                bad.append("the description quoted in ROUTING.md is not the one in SKILL.md. "
                           "The record is of a state the project is no longer in")
            elif of_live < 0.6:
                bad.append("ROUTING.md quotes a fragment of the description, not the whole "
                           "value. The wording that did the routing is the record, and half "
                           "of it does not route")
            else:
                notes.append("the quoted rewrite is the description that is live in SKILL.md")

    # ---- 3. which script is which? --------------------------------------
    # Classify the hooks by the event they are wired to rather than by their
    # extension: Part 2 asks for a formatter and never says bash.
    settings = d / ".claude" / "settings.json"
    config = {}
    if settings.exists():
        try:
            config = json.loads(settings.read_text())
        except json.JSONDecodeError as e:
            bad.append(f"settings.json does not parse: {e}")
    hooks_cfg = (config.get("hooks") or {}) if isinstance(config, dict) else {}
    if not isinstance(hooks_cfg, dict):
        hooks_cfg = {}

    def invokes(command, script):
        """Does this command line actually run this script?

        `true  # no-type-hints.py` names the file and runs nothing, so the token
        has to survive comment-stripping and resolve to the file on disk.
        """
        for token in command.split("#", 1)[0].split():
            raw = token.strip("\"'`;|&()<>").replace('"', "").replace("'", "")
            raw = raw.replace("${CLAUDE_PROJECT_DIR}", str(d))
            raw = raw.replace("$CLAUDE_PROJECT_DIR", str(d))
            raw = raw.replace("${CLAUDE_PLUGIN_ROOT}", str(d))
            if not raw.endswith(script.name):
                continue
            path = Path(raw)
            if not path.is_absolute():
                path = d / raw
            try:
                if path.exists() and path.samefile(script):
                    return True
            except OSError:
                continue
        return False

    def entries_of(event):
        return [e for e in (hooks_cfg.get(event) or []) if isinstance(e, dict)]

    def wiring(event, script):
        """(entry, hook) for the first <event> entry that runs <script>."""
        for entry in entries_of(event):
            for h in entry.get("hooks") or []:
                if isinstance(h, dict) and invokes(str(h.get("command") or ""), script):
                    return entry, h
        return None, None

    def wired(event):
        return [s for s in scripts if wiring(event, s)[0] is not None]

    pre, post = wired("PreToolUse"), wired("PostToolUse")
    formatters = post or [s for s in scripts if s.suffix in (".sh", ".bash")]
    candidates = list(pre)
    for script in scripts:
        if script.suffix == ".py" and script not in candidates:
            candidates.append(script)
    candidates = candidates[:6]

    def invocation(script):
        if script.suffix == ".py":
            return [sys.executable, str(script)]
        if script.suffix in (".sh", ".bash", ""):
            return ["/bin/bash", str(script)]
        return [str(script)] if os.access(script, os.X_OK) else ["/bin/bash", str(script)]

    # Never run a student's hook against the student's own files: a formatter
    # hook rewrites whatever path it is handed, and grading has to be repeatable.
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "project"
        (work / "trainer").mkdir(parents=True)
        fixture = code / "trainer" / "navigation.py"
        py = work / "trainer" / "navigation.py"
        py.write_text(fixture.read_text() if fixture.exists()
                      else "def normalize_index(value, length):\n    return 0\n")
        (work / "README.md").write_text("# fixture\n")
        empty = Path(tmp) / "empty"
        empty.mkdir()

        def feed(script, payload, timeout=30):
            try:
                return run(invocation(script), cwd=work, env={"PATH": str(empty)},
                           stdin=payload, timeout=timeout)
            except subprocess.TimeoutExpired:
                return None

        def event(path, event_name="PreToolUse", **tool_input):
            tool = "Edit" if "new_string" in tool_input else "Write"
            return json.dumps({"session_id": "lab07", "cwd": str(work),
                               "hook_event_name": event_name, "tool_name": tool,
                               "tool_input": dict(tool_input, file_path=str(path))})

        # ---- 4. and does anything actually say no? --------------------
        # The gate is graded first: the formatter list below excludes it, so a
        # Python gate wired alongside a Python formatter is never confused for
        # one. The findings are reported in the order the README asks for them.
        gate_notes, gate_bad = [], []
        cases = [
            ("annotated Write", 2,
             event(py, content="def normalize_index(value: int, length: int) -> int:\n    return 0\n")),
            ("annotated module constant", 2, event(py, content='KEY: str = "line_index"\n')),
            ("annotated Edit", 2, event(py, old_string="def next(self):",
                                        new_string='def next(self) -> str:\n    return ""\n')),
            ("a signature split over several lines", 2,
             event(py, content="def normalize_index(\n    value: int,\n    length,\n):\n    return 0\n")),
            ("clean Write", 0, event(py, content="def normalize_index(value, length):\n    return 0\n")),
            ("an annotation inside a string and a comment", 0,
             event(py, content='LABEL = "count: int"\n# def parse(value: int) -> int\n'
                               'def parse(value):\n    return int(value)\n')),
            ("a file that is not Python", 0,
             event(work / "README.md", content="def f(x: int) -> int: ...\n")),
            ("source that does not parse yet", 0, event(py, content="def f(:\n")),
        ]

        def behaviour(script):
            """Every case, unless one hangs -- then stop, and say so once.

            A hook that waits for input it will never get would otherwise hold up
            grading for as many timeouts as there are cases.
            """
            out = {}
            for label, _, payload in cases:
                r = feed(script, payload, timeout=20)
                if r is None:
                    for rest, _, _ in cases:
                        out.setdefault(rest, (None, ""))
                    return out
                out[label] = (r.returncode, (r.stderr or "").strip())
            return out

        blocker, seen = None, {}
        for script in candidates:
            result = behaviour(script)
            if result.get("annotated Write", (None,))[0] == 2:
                blocker, seen = script, result
                break
            if script in pre and result.get("clean Write", (0,))[0] is None:
                gate_bad.append(f"{script.name}: wired as PreToolUse and hangs on an ordinary "
                                "Write. Every matching tool call waits for it")

        if not candidates:
            gate_bad.append("no PreToolUse gate in .claude/hooks/ -- PostToolUse fires after the "
                            "write has landed and cannot take it back. A convention you want "
                            "enforced needs PreToolUse and exit code 2")
        elif blocker is None:
            names = ", ".join(p.name for p in candidates)
            gate_bad.append(f"{names}: fed a PreToolUse event whose content annotates its "
                            "arguments, nothing exited 2. Exit 0 is approval and exit 1 is a "
                            "warning; only 2 stops the tool call")
        else:
            broken = []
            hung = [label for label, _, _ in cases if seen.get(label, (None,))[0] is None]
            if hung:
                broken.append(f"{blocker.name}: hung on {hung[0]} and never returned. A "
                              "PreToolUse hook runs before every matching edit, so a hang is "
                              "not a slow check, it is an outage")
            for label, want, _ in cases:
                got = seen.get(label, (None, ""))[0]
                if got is None:
                    continue
                if got != want and want == 2:
                    broken.append(f"{blocker.name}: exits {got} on {label}, so that one goes "
                                  "through. An ast walk has to look at AnnAssign, "
                                  "arg.annotation and FunctionDef.returns, and at new_string "
                                  "as well as content")
                elif got != want:
                    broken.append(f"{blocker.name}: exits {got} on {label}. A gate that refuses "
                                  "work it was never asked to judge gets switched off within a "
                                  "day, and then it is guarding nothing")
            if not hung and not seen["annotated Write"][1]:
                broken.append(f"{blocker.name}: exits 2 but writes nothing to stderr. Exit 2 "
                              "hands stderr back to the model as the reason; without it the "
                              "refusal is indistinguishable from a broken tool")
            gate_bad += broken
            if not broken:
                gate_notes.append(f"{blocker.name}: exit 2 on annotations, exit 0 on clean code, "
                                  "unparseable source, strings, comments and non-Python files")

            entry, hook_cfg = wiring("PreToolUse", blocker)
            if not settings.exists():
                gate_bad.append("no .claude/settings.json -- the script refuses annotated code "
                                "when you run it by hand, and nothing will ever run it")
            elif entry is None and wiring("PostToolUse", blocker)[0] is not None:
                gate_bad.append(f"{blocker.name} is wired as PostToolUse. It exits 2 when "
                                "you run it by hand, but PostToolUse fires after the write "
                                "has landed: the annotations are already on disk and the "
                                "exit code only complains about them")
            elif not entries_of("PreToolUse"):
                gate_bad.append("settings.json has no PreToolUse block, so the gate never "
                                "runs. PostToolUse would report the annotations after they "
                                "were written")
            elif entry is None:
                gate_bad.append(f"settings.json wires a PreToolUse hook, but no command in it "
                                f"runs {blocker.name} -- naming the file in a comment or an echo "
                                "leaves the one script that actually refuses unwired")
            elif hook_cfg.get("type") not in (None, "command"):
                gate_bad.append(f"the PreToolUse hook that runs {blocker.name} has "
                                f"type: {hook_cfg.get('type')!r}, and only type: command runs a "
                                "script")
            else:
                head = str(hook_cfg.get("command") or "").split("#", 1)[0].split()
                if head and head[0].strip("\"'").endswith(blocker.name) \
                        and not os.access(blocker, os.X_OK):
                    gate_bad.append(f"{blocker.name} is the command itself and is not "
                                    "executable (chmod +x), so the hook never starts and "
                                    "the tool call it was meant to stop goes through")
                matcher = str(entry.get("matcher", ""))
                if matcher.strip() in ("*", "") or re.search(r"\b(Write|Edit)\b", matcher):
                    gate_notes.append(f"PreToolUse runs {blocker.name} on a matcher that selects "
                                      "Edit and Write")
                else:
                    why = (" A matcher is the whole tool name, so NotebookEdit is not Edit."
                           if re.search(r"Edit|Write", matcher) else "")
                    gate_bad.append(f"the PreToolUse entry that runs {blocker.name} matches "
                                    f"{matcher!r}, which does not select Edit or Write, so "
                                    "the gate watches tool calls that never touch a "
                                    "file." + why)

        # ---- 5. does the formatter degrade quietly? --------------------
        # Run this after the gate so a Python gate is never mistaken for
        # the formatter it was wired alongside.
        for hook in [f for f in formatters if f != blocker]:
            r = feed(hook, event(py, event_name="PostToolUse"))
            if r is None:
                bad.append(f"{hook.name}: hung with no formatter on the PATH. A hook that "
                           "waits runs on every matching edit, so a hang is an outage")
            elif r.returncode != 0:
                bad.append(f"{hook.name}: exits {r.returncode} when its tool is not installed. "
                           "A hook that fails on a machine without the tool turns every edit "
                           "into an error for someone who never asked for the check")
            else:
                other = feed(hook, event(work / "README.md", event_name="PostToolUse"))
                if other is not None and other.returncode != 0:
                    bad.append(f"{hook.name}: exits {other.returncode} on a file that is not "
                               "Python. The rule was .py only, and everything else is work "
                               "it was never asked to do")
                else:
                    notes.append(f"{hook.name}: exits 0 when the tool is absent")
            body = hook.read_text()
            live = [line for line in body.splitlines()
                    if line.strip() and not line.strip().startswith("#")]
            if len(live) < 3:
                bad.append(f"{hook.name} does nothing but exit. A hook that runs no tool and "
                           "reads no path passes every test a hook can be given and formats "
                           "nothing")
            elif not re.search(r"ruff|black|format|lint|isort", body, re.I):
                bad.append(f"{hook.name} never names a formatter or a linter, so whatever "
                           "it does on a .py file, it is not the check you asked for")
            elif not re.search(r"file_path|tool_input|CLAUDE_", body):
                bad.append(f"{hook.name} never reads file_path out of the event, so it "
                           "cannot know which file was just written")
            if not os.access(hook, os.X_OK):
                bad.append(f"{hook.name} is not executable (chmod +x)")

        if not [f for f in formatters if f != blocker]:
            bad.append("no formatter hook of its own -- Part 2's hook runs after the write "
                       "lands and reports; Part 4's refuses before it. They are two "
                       "scripts on two events, not one")

        notes += gate_notes
        bad += gate_bad

    if bad:
        return FAIL, "Skill or hook is there but not yet correct.", bad
    return PASS, "Description routes, degrades quietly, and the gate refuses instead of reporting.", notes


# --------------------------------------------------------------------------
# lab 08 -- what a capability costs
# --------------------------------------------------------------------------

def _seed(lab):
    """Write the little database if it is not there.

    It is generated, never committed, so a fresh clone arrives without it. The
    student runs seed.py; running it here too means the reference answer checks
    out and passes on a machine that has never seen this lab.
    """
    script = lab / "seed.py"
    if not script.exists():
        return False
    run([sys.executable, str(script)], cwd=lab, timeout=60)
    return (lab / "library.db").exists()


NONCE_TITLE = "Aurora Interstice"          # invented here, at run time
NONCE_AUTHOR = "Wren Calloway"


def _server_answers(server):
    """Drive the server the way the stdio transport does, and see if it replies.

    The whole lab runs against a copy in a temp directory, with a book the
    checker invents inserted into the copied database a moment before. A server
    that answers from the database returns it; a server that hardcodes the
    answer to make the check go green cannot, because the title did not exist
    when the student wrote it.
    """
    import shutil
    import sqlite3

    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp) / "lab"
        shutil.copytree(server.parent, sandbox,
                        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        db = sandbox / "library.db"
        if db.exists():
            conn = sqlite3.connect(db)
            conn.execute("INSERT INTO book VALUES (?, ?, ?, ?)",
                         (NONCE_TITLE, NONCE_AUTHOR, 2031, "sf"))
            conn.commit()
            conn.close()

        lines = [
            '{"jsonrpc":"2.0","id":1,"method":"initialize",'
            '"params":{"protocolVersion":"2024-11-05"}}',
            '{"jsonrpc":"2.0","method":"notifications/initialized"}',
            '{"jsonrpc":"2.0","id":2,"method":"tools/list"}',
            '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":'
            '{"name":"find_books","arguments":{"author":"Jemisin"}}}',
            '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":'
            '{"name":"find_books","arguments":{"author":"%s"}}}' % NONCE_AUTHOR,
            '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":'
            '{"name":"find_books","arguments":{"author":"Pratchett"}}}',
        ]
        result = run([sys.executable, str(sandbox / server.name)], cwd=sandbox,
                     stdin="\n".join(lines) + "\n", timeout=30)

    replies = {}
    for line in result.stdout.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "id" in message:
            replies[message["id"]] = message
    return replies, (result.stderr or "").strip()


def lab08(d):
    notes_file = d / "MCP.md"
    if not notes_file.exists():
        return TODO, "No MCP.md yet.", [
            "Connect the server, then read /context all before you use it. The bill "
            "arrives at connection time, not at call time.",
        ]

    text = notes_file.read_text()
    left = template_left(text)
    if left:
        return TODO, f"MCP.md still has {left} in it.", [
            "Two readings of /context all, for the same capability reached two ways. "
            "That pair is the whole lab.",
        ]

    notes, bad = [], []

    # ---- 1. does the server still work? ----------------------------------
    server = d / "mcp_server.py"
    if not server.exists():
        server = ROOT / "exercises" / "lab08_mcp" / "mcp_server.py"
    if not (server.parent / "library.db").exists() and not _seed(server.parent):
        bad.append("library.db is not there and seed.py did not write it -- the server "
                   "has nothing to read")
    else:
        replies, stderr = _server_answers(server)
        if 1 not in replies:
            bad.append("the server did not answer initialize" + (f": {stderr}" if stderr else ""))
        elif "result" not in replies[1] or "protocolVersion" not in replies[1]["result"]:
            bad.append("the initialize reply has no protocolVersion, so no client will "
                       "finish the handshake")
        if 2 in replies and replies[2].get("result", {}).get("tools"):
            notes.append(f"{len(replies[2]['result']['tools'])} tools advertised")
        else:
            bad.append("tools/list came back empty -- a server with no tools is a "
                       "connection you pay for and cannot use")
        answer = json.dumps(replies.get(3, {}).get("result", {}))
        nonce = json.dumps(replies.get(4, {}).get("result", {}))
        empty = json.dumps(replies.get(5, {}).get("result", {}))
        missing = [t for t in ("The Fifth Season", "The Obelisk Gate", "The Stone Sky")
                   if t not in answer]
        if not replies.get(3, {}).get("result", {}).get("content"):
            bad.append("tools/call did not return content")
        elif missing:
            bad.append("tools/call answered but left out " + ", ".join(missing)
                       + " -- it is not reading the shelf, or not filtering it")
        elif NONCE_TITLE not in nonce:
            bad.append("a book inserted into the database a moment ago did not come "
                       "back, so the answers are not coming from the database")
        elif "Zzz" in empty or "The Fifth Season" in empty:
            bad.append("an author who is not on the shelves got books back")
        else:
            notes.append("handshake, a filtered query, and a book invented at run time")

    # ---- 2. is there a skill, and is its description an interface? -------
    skills = sorted((d / ".claude" / "skills").glob("*/SKILL.md")) \
        if (d / ".claude" / "skills").is_dir() else []
    if not skills:
        bad.append("no .claude/skills/*/SKILL.md -- the second half of the lab is the "
                   "comparison, and without it there is one number")
    else:
        for skill in skills:
            try:
                meta, _, _ = frontmatter(skill)
            except ValueError as e:
                bad.append(f"{skill.parent.name}/SKILL.md: {e}")
                continue
            description = str(meta.get("description") or "")
            if not meta.get("name"):
                bad.append(f"{skill.parent.name}: no name in the frontmatter")
            if len(description.split()) < 8:
                bad.append(f"{skill.parent.name}: the description is too short to route "
                           "on. It is the whole interface -- say when to use it, in the "
                           "words someone would use")
            elif not re.search(r"\b(book|librar|shelf|shelves|author)\w*\b",
                               description, re.I):
                bad.append(f"{skill.parent.name}: the description never mentions what it "
                           "is about, so nothing a user says will match it")
            else:
                notes.append(f"skill {skill.parent.name}, description routes")

    # ---- 3. two numbers, and a verdict that uses them ---------------------
    numbers = [_tokens(m) for m in
               re.findall(r"\*\*Context cost[^:]*:\*\*\s*([^\n]+)", text)]
    numbers = [n for n in numbers if n]
    if len(numbers) < 2:
        bad.append(f"{len(numbers)} context reading(s), not 2 -- the comparison needs "
                   "both, measured the same way")
    else:
        notes.append(f"server {numbers[0]:,} tokens, skill {numbers[1]:,}")
        m = re.search(r"\*\*Ratio between the two:\*\*\s*([\d.,]+)", text)
        if m and numbers[1]:
            claimed = float(m.group(1).replace(",", ""))
            real = numbers[0] / numbers[1]
            if abs(claimed - real) > max(0.3, real * 0.15):
                bad.append(f"the ratio is written as {claimed:.1f} but "
                           f"{numbers[0]:,} / {numbers[1]:,} is {real:.1f}")

    verdict = re.search(r"\*\*I would ship:\*\*\s*(.+)", text)
    if not verdict or not re.search(r"server|skill|cli", verdict.group(1), re.I):
        bad.append("no verdict -- say which of the two you would ship")
    because = re.search(r"\*\*Because:\*\*\s*(.+?)(?:\n\s*\n|\Z)", text, re.S)
    if not because or len(because.group(1).split()) < 10:
        bad.append("the verdict has no reason under it")
    switch = re.search(r"\*\*When I would switch to the other one:\*\*\s*(.+)", text)
    if not switch or len(switch.group(1).split()) < 5:
        bad.append("no condition for switching -- a preference you cannot falsify is "
                   "not a decision")

    if bad:
        return FAIL, "Connected, but the trade is not measured yet.", notes + bad
    return PASS, "One capability, two ways, and a verdict with numbers under it.", notes


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

    # ---- 1. is the file a contract, or just another session? -------------
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

    # The shipped placeholders, spelled out. Testing for a bare "<" instead is
    # what fails a reason that quotes `if len(rules) < 4` -- and this lab is a
    # triage of source code, so reasons quote source code.
    TEMPLATE = ("<from /context>", "<subtract", "<the directory", "<one line",
                "<accept / reject>")
    # A path, a line, or the sentence you found there. Anything a reader could
    # go and look at for themselves.
    EVIDENCE = re.compile(r"`|\.py\b|:\d+|\bline \d+|\"[^\"]{4,}\"")

    def unfilled(s):
        return any(marker in s for marker in TEMPLATE)

    def thin(s, least):
        """Distinct words, not words. A word count is not a check: thirteen
        copies of the word "cost" clears any threshold you set on length."""
        return len(set(re.findall(r"[a-z0-9_./:-]+", s.lower()))) < least

    # ---- 2. what the delegation did to the main window -------------------
    delegation = d / "DELEGATION.md"
    if not delegation.exists():
        if bad:
            return FAIL, "One subagent is good; others have problems.", notes + bad
        return TODO, "A subagent, but nothing measured yet.", notes + [
            "Delegation is a context strategy, and an unmeasured strategy is a "
            "preference. Two rounds of the same survey, four /context readings, "
            "into DELEGATION.md.",
        ]

    try:
        text = delegation.read_text()
    except (OSError, UnicodeDecodeError) as e:
        bad.append(f"DELEGATION.md cannot be read: {e}")
        return FAIL, "DELEGATION.md is there and unreadable.", notes + bad

    if "<from /context>" in text or "<subtract" in text:
        if bad:
            return FAIL, "One subagent is good; others have problems.", notes + bad
        return TODO, "DELEGATION.md is still the template.", notes + [
            "The readings are yours to take -- /context on each side of each round, "
            "same files, same question, or the two numbers are not comparable.",
        ]

    rounded = set()

    def reading(label):
        """One /context reading out of the table.

        _row is the shared reader and it takes the last cell and drops the sign.
        Both are wrong here. A saving can be negative -- the README says out loud
        that delegating often costs more -- and /context prints a percentage
        beside the count, which a student transcribes along with it.
        """
        for line in text.splitlines():
            if not line.strip().startswith("|"):
                continue
            cells = [c.strip().strip("*") for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            flat = re.sub(r"[^a-z0-9]+", " ", cells[0].lower()).strip()
            if label not in flat:
                continue
            for cell in cells[1:]:
                found = re.search(r"([-−–(])?\s*(\d[\d,]*(?:\.\d+)?\s*k?)\b",
                                  cell, re.I)
                if not found:
                    continue
                number = _tokens(found.group(2).replace(" ", ""))
                if number is None:
                    continue
                if re.search(r"~|\d\s*k\b", cell, re.I):
                    rounded.add(label)
                # "-2,000", "(2,000)" and "2,000 more" are the same result.
                if found.group(1) or re.search(r"\bmore\b", cell, re.I):
                    number = -number
                return number
        return None

    before_a = reading("round a before")
    after_a = reading("round a after")
    before_b = reading("round b before")
    after_b = reading("round b after")
    saving = reading("saving")

    missing = [name for name, value in
               (("round A before", before_a), ("round A after", after_a),
                ("round B before", before_b), ("round B after", after_b),
                ("saving", saving)) if value is None]
    if saving is None and re.search(r"^\|[^|\n]*saving", text, re.I | re.M):
        bad.append("the saving row is there but no number came out of it -- if "
                   "delegating cost more, the saving is negative and it still has "
                   "to be a number: write -2,000 or (2,000), not a word")
        missing = [name for name in missing if name != "saving"]
    if missing:
        bad.append("no number read for: " + ", ".join(missing)
                   + " -- the label goes in the left cell of the row and a token "
                   "count in one of the others; a row with no digits reads as blank")
    else:
        cost_a, cost_b = after_a - before_a, after_b - before_b
        notes.append(f"inline {cost_a:,} tokens, delegated {cost_b:,}")
        implausible = [name for name, value in
                       (("round A before", before_a), ("round A after", after_a),
                        ("round B before", before_b), ("round B after", after_b))
                       if not 1000 <= value <= 2000000]
        if implausible:
            bad.append("not a /context reading: " + ", ".join(implausible)
                       + " -- the system prompt, the tool definitions and the memory "
                       "files are several thousand tokens before you ask anything, so "
                       "a reading that size was not taken off /context")
        elif cost_a <= 0:
            bad.append("round A cost nothing -- surveying a codebase in the main session "
                       "has to move /context. Either one of those two readings was not "
                       "taken, or the session compacted between them, in which case the "
                       "round is not comparable and wants taking again")
        if cost_b < 0:
            bad.append("round B came out negative -- inside one uninterrupted session "
                       "/context does not go down, so either the two readings are the "
                       "wrong way round or the session compacted mid-round; a compacted "
                       "round has to be taken again")
        if before_a == before_b and after_a == after_b and not rounded:
            bad.append("round B is round A's row copied down -- both readings agree to "
                       "the token, and a comparison needs two measurements")
        if abs((cost_a - cost_b) - saving) > max(50, 0.02 * max(abs(saving), 1)):
            bad.append(f"the saving is written as {saving:,} but {cost_a:,} - {cost_b:,} "
                       f"is {cost_a - cost_b:,}. One of the five numbers was copied "
                       "rather than measured")
        elif cost_b > cost_a:
            notes.append("delegating cost more here than doing it inline -- a real "
                         "result, and the more interesting one; say why in the sentence "
                         "below the table")
        elif cost_b == cost_a:
            notes.append("the saving came out at zero -- the result the lab says is worth "
                         "more than a big one; the tokens were still spent, somewhere else")

    surveyed = re.search(r"\*\*What I surveyed:\*\*\s*(.+?)(?:\n\s*\n|\Z)", text, re.S)
    if not surveyed or unfilled(surveyed.group(1)) or thin(surveyed.group(1), 5):
        bad.append("DELEGATION.md never says what was surveyed -- two rounds only compare "
                   "if they asked the same question of the same files")
    elif not re.search(r"[`/]|\.py\b", surveyed.group(1)):
        bad.append("the surveyed sentence names no files -- a directory or a path, so the "
                   "two rounds can be shown to have read the same thing and not two "
                   "different things")
    unsaved = re.search(r"\*\*What delegating did not save:\*\*\s*(.+?)(?:\n\s*\n|\Z)",
                        text, re.S)
    if not unsaved or unfilled(unsaved.group(1)) or thin(unsaved.group(1), 10):
        bad.append("no sentence on what delegating did not save -- the subagent opened the "
                   "same files and ran the same searches, that work was paid for, and none "
                   "of it is anywhere in your table")
    elif not re.search(r"token|read|search|grep|spent|spend|burn|cost|paid|bill|"
                       r"own context|own window|transcript|again|twice", unsaved.group(1), re.I):
        bad.append("the sentence about what delegating did not save never names the work "
                   "that happened out of sight -- it is the same reading, billed somewhere "
                   "you cannot see it")
    else:
        notes.append("the half of the bill that moved out of sight is written down")

    # ---- 3. the third cost, which is the one nobody budgets for ----------
    triage = d / "TRIAGE.md"
    if not triage.exists():
        if bad:
            return FAIL, "Measured, but the numbers do not hold together yet.", notes + bad
        return TODO, "Measured, but the report was never triaged.", notes + [
            "python3 triage.py report.txt splits what came back into findings you have "
            "to answer one at a time. A report you did not triage is a report you did "
            "not verify.",
        ]

    try:
        report = triage.read_text()
    except (OSError, UnicodeDecodeError) as e:
        bad.append(f"TRIAGE.md cannot be read: {e}")
        return FAIL, "TRIAGE.md is there and unreadable.", notes + bad

    blocks = re.split(r"^##\s+Finding\s+\d+.*$", report, flags=re.M)[1:]
    if not blocks:
        bad.append("TRIAGE.md has no '## Finding N' blocks -- run triage.py over the "
                   "report instead of summarising it by hand; splitting it is the part "
                   "that stops you agreeing with all of it at once")
    elif all("<accept / reject>" in block for block in blocks):
        if bad:
            return FAIL, "Delegated and measured, but something in it does not hold up.", notes + bad
        return TODO, "TRIAGE.md is still the tool's output.", notes + [
            f"{len(blocks)} findings, each waiting for a verdict and a reason. At least "
            "one of them is wrong, and the only way to find out which is to open the "
            "file it names.",
        ]
    else:
        header = re.search(r"^(\d+) findings?, split out of", report, re.M)
        if not header:
            bad.append("TRIAGE.md did not come out of triage.py -- the header line the "
                       "tool writes is gone. Run it over report.txt rather than writing "
                       "the blocks yourself; the split is the part that stops you "
                       "agreeing with all of it at once")
        elif int(header.group(1)) != len(blocks):
            bad.append(f"TRIAGE.md says {header.group(1)} findings and holds {len(blocks)} "
                       "-- blocks were added or dropped after the split, and a finding "
                       "you deleted is a finding you did not answer")
        verdicts, checked = [], 0
        for number, block in enumerate(blocks, 1):
            quoted = [l for l in block.splitlines() if l.strip().startswith(">")]
            claim = " ".join(l.strip().lstrip(">").strip() for l in quoted)
            said = re.search(r"\*\*Verdict:\*\*\s*(.+)", block)
            why = re.search(r"\*\*Because:\*\*\s*(.+?)(?:\n\s*\n|\Z)", block, re.S)
            word = None
            if said and not unfilled(said.group(1)):
                word = re.search(r"accept|reject", said.group(1), re.I)
            if not quoted:
                bad.append(f"finding {number}: nothing quoted under it -- a verdict on a "
                           "claim you did not copy down is a verdict on your memory of it")
            elif thin(claim, 5):
                bad.append(f"finding {number}: the quote under it is too short to be a "
                           "claim -- paste back what the report actually said, or the "
                           "verdict is on your paraphrase of it and not on the claim")
            if not word:
                bad.append(f"finding {number}: no verdict, or one that is neither accept "
                           "nor reject")
            else:
                verdicts.append(word.group(0).lower())
            if not why or unfilled(why.group(1)):
                bad.append(f"finding {number}: no reason under the verdict -- the reason "
                           "is the evidence that you checked rather than skimmed")
                continue
            # A short reason that names a line beats a long one that names nothing,
            # so evidence buys the floor down rather than being asked for on top.
            shown = bool(EVIDENCE.search(why.group(1)))
            if thin(why.group(1), 5 if shown else 8):
                bad.append(f"finding {number}: no reason under the verdict -- the reason "
                           "is the evidence that you checked rather than skimmed")
                continue
            if shown:
                checked += 1
            elif word and word.group(0).lower() == "reject":
                bad.append(f"finding {number}: rejected, and the reason names nothing you "
                           "opened -- a reject is a claim of your own, so it needs the "
                           "path, the line or the sentence you found there instead")
        if len(blocks) < 2:
            bad.append("one finding is not a triage -- ask for the whole report back, not "
                       "its headline")
        elif checked < 2:
            bad.append("the reasons name nothing you opened -- a path, a line number or "
                       "the sentence you found there. Verdicts with no file under them "
                       "are the report agreed with a second time, not checked")
        if verdicts and "reject" not in verdicts:
            bad.append(f"{len(verdicts)} findings and not one rejected. A review you agreed "
                       "with in full is a review you read, not one you checked -- take the "
                       "claim you are least sure of and go and open the file it names")
        elif verdicts and "accept" not in verdicts and len(verdicts) > 2:
            notes.append(f"{len(verdicts)} findings and all of them rejected -- worth a "
                         "second look; a report that got nothing right is as unlikely as "
                         "one that got everything right")
        elif verdicts:
            notes.append(f"{len(verdicts)} findings triaged, "
                         f"{verdicts.count('reject')} rejected")

    if bad:
        return FAIL, "Delegated and measured, but something in it does not hold up.", notes + bad
    return PASS, "A contract, two rounds of what it saved, and a report that was checked.", notes


# --------------------------------------------------------------------------
# lab 10 / 11 / 13                                                 MANUAL
# --------------------------------------------------------------------------

def lab10(d):
    spec = d / "SPEC.md"
    if not spec.exists():
        return TODO, "No SPEC.md yet.", [
            "The issue is eight bullets and one of them is the work. Cutting it down "
            "is the first job, not a preliminary to it.",
        ]

    text = spec.read_text()
    left = template_left(text)
    if left:
        return TODO, f"SPEC.md still has {left} in it.", [
            "One sentence for the slice, then four sections. Postconditions and "
            "invariants each name the test that proves them.",
        ]

    notes, bad = [], []

    # ---- 1. one slice, and a refusal list --------------------------------
    slice_line = re.search(r"\*\*One sentence:\*\*\s*(.+)", text)
    if not slice_line or len(slice_line.group(1).split()) < 6:
        bad.append("no one-sentence slice")
    else:
        said = slice_line.group(1)
        if re.search(r"\band\b", said, re.I) and "," in said:
            notes.append("slice sentence uses 'and' -- check it is one slice")
        notes.append("slice named")
    left = re.search(r"\*\*Left in the backlog:\*\*\s*(.+?)(?:\n\s*\n|\Z)", text, re.S)
    if not left or len(left.group(1).split()) < 5:
        bad.append("nothing listed as left in the backlog -- the refusal is the part "
                   "that survives review")

    # ---- 2. four sections, each with something in it ---------------------
    for heading in ("postconditions", "preconditions", "invariants", "negative criteria"):
        block = re.search(rf"^##\s+{heading}\s*$(.*?)(?=^##\s|\Z)",
                          text, re.I | re.M | re.S)
        bullets = re.findall(r"^\s*[-*]\s+\S.*", block.group(1), re.M) if block else []
        if not bullets:
            bad.append(f"{heading}: nothing written down")
        else:
            notes.append(f"{heading}: {len(bullets)}")

    # ---- 3. the gate itself ----------------------------------------------
    gate = d / "pr_gate.py"
    if not gate.exists():
        bad.append("pr_gate.py is not in this folder")
    else:
        result = run([sys.executable, str(gate)], cwd=d, timeout=180)
        if result.returncode != 0:
            tail = [l for l in result.stdout.splitlines() if "UNPROVEN" in l][:4]
            bad.append("the gate is red: " + (tail[0].strip() if tail else "see pr_gate.py"))
            for line in tail[1:]:
                bad.append("             " + line.strip())
        else:
            m = re.search(r"(\d+) contract lines, all proven", result.stdout)
            notes.append(f"gate green over {m.group(1) if m else '?'} contract lines")

    # ---- 4. the two things the module will not let you skip --------------
    pr = d / "PR.md"
    if not pr.exists():
        bad.append("no PR.md -- the handoff is the deliverable, not the diff")
    else:
        body = pr.read_text()
        broke = re.search(r"\*\*Which contract line it broke:\*\*\s*(.+)", body)
        if not broke or len(broke.group(1).split()) < 4 or "<" in broke.group(1):
            bad.append("PR.md does not name the contract line the plan traded away. If "
                       "the plan really broke nothing, say that instead -- but read it "
                       "against the contract once more first")
        bare = re.search(r"\*\*Difference:\*\*\s*(.+?)(?:\n\s*\n|\Z)", body, re.S)
        if not bare or len(bare.group(1).split()) < 10 or "<" in bare.group(1):
            bad.append("PR.md does not record what --bare changed")
        else:
            notes.append("plan correction and the --bare difference both recorded")

    if bad:
        return FAIL, "A contract exists, but it is not proven yet.", notes + bad
    return PASS, "One slice, a contract that names its tests, and a green gate.", notes


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
    ("lab00_scales", "the three scales", lab00),
    ("lab01_first_contact", "first contact", lab01),
    ("lab02_five_jobs", "the five jobs", lab02),
    ("lab03_session", "the window, measured", lab03),
    ("lab04_audit", "auditing the evidence", lab04),
    ("lab05_memory", "project memory", lab05),
    ("lab06_permissions", "permissions", lab06),
    ("lab07_skills", "skills and hooks", lab07),
    ("lab08_mcp", "what a capability costs", lab08),
    ("lab09_subagents", "subagents", lab09),
    ("lab10_spec", "the contract and the gate", lab10),
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
        if not d.is_dir() and fn.__name__ not in ("lab01", "lab11", "lab13"):
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
