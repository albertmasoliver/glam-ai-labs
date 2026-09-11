"""Presentation helpers. No rules live here -- only how things are shown."""


def display_title(title):
    """The title as a reader sees it. Never returns None."""
    return (title or "").strip() or "(untitled)"
