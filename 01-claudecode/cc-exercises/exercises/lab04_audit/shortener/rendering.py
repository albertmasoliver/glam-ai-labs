"""Presentation helpers."""

ELLIPSIS = "…"


def truncate(text, limit):
    """Shorten text to at most `limit` characters, ellipsis included."""
    if len(text) <= limit:
        return text
    return text[:limit] + ELLIPSIS
