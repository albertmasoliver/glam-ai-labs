"""Request handlers. Each returns (status, body)."""

from .rendering import truncate
from .validation import validate_code, validate_url

PREVIEW_WIDTH = 40


def create_link(store, payload):
    problem = validate_url(payload.get("url"))
    if problem:
        return 400, {"error": problem}

    code = store.save(payload["url"])
    return 200, {"code": code, "url": truncate(payload["url"], PREVIEW_WIDTH)}


def preview_link(store, payload):
    problem = validate_code(payload.get("code"))
    if problem:
        return 400, {"error": problem}

    url = store.resolve(payload["code"])
    if url is None:
        return 404, {"error": "no such code"}
    return 200, {"url": truncate(url, PREVIEW_WIDTH)}
