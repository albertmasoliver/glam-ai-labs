"""Request handlers. Each returns (status, body).

Handlers stay thin: take a payload, run it past the validators, ask the
store to do the work, and turn the result into a status code.
"""

from .formatting import display_title
from .validation import validate_body, validate_title


def _check(payload, fields):
    """Run every validator that applies to the fields this request carries."""
    checks = {"title": validate_title, "body": validate_body}
    for name in fields:
        problem = checks[name](payload.get(name))
        if problem:
            return problem
    return None


def create_note(store, payload):
    problem = _check(payload, ("title", "body"))
    if problem:
        return 400, {"error": problem}

    note = store.save({"title": payload.get("title"), "body": payload.get("body", "")})
    return 200, {"id": note["id"], "title": display_title(note["title"])}


def update_note(store, note_id, payload):
    present = tuple(f for f in ("title", "body") if f in payload)
    problem = _check(payload, present)
    if problem:
        return 400, {"error": problem}

    fields = {f: payload[f] for f in present}
    note = store.update(note_id, fields)
    if note is None:
        return 404, {"error": "no such note"}
    return 200, {"id": note["id"], "title": display_title(note["title"])}
