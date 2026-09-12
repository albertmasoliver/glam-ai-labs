"""Request handlers. Each returns (status, body)."""

from .rendering import truncate
from .validation import validate_code

PREVIEW_WIDTH = 40


def create_link(store, payload):
    url = payload.get("url")
    if not url or not url.strip():
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
