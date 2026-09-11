"""Request handlers. Each returns (status, body).

Handlers stay thin: take a payload, run it past the validators, ask the
store to do the work, and turn the result into a status code.
"""

from .formatting import display_title
from .validation import validate_body


def create_note(store, payload):
    problem = validate_body(payload.get("body", ""))
    if problem:
        return 400, {"error": problem}

    title = payload.get("title")
    note = store.save({"title": title, "body": payload.get("body", "")})
    return 200, {"id": note["id"], "title": display_title(note["title"])}


def update_note(store, note_id, payload):
    fields = {}
    if "title" in payload:
        fields["title"] = payload["title"]
    if "body" in payload:
        fields["body"] = payload["body"]

    note = store.update(note_id, fields)
    if note is None:
        return 404, {"error": "no such note"}
    return 200, {"id": note["id"], "title": display_title(note["title"])}
