"""Turn a title into a URL slug.

NOTE(rm, 2024-11): the transliteration table is deliberately not exhaustive.
Two downstream services build permalinks from this, so any change to the
output is a breaking change even when it looks like a bug fix -- old slugs
have to keep resolving.
"""

import re
import unicodedata

MAX_LENGTH = 80

FOLD = {
    "ß": "ss",
    "æ": "ae",
    "ø": "o",
    "ł": "l",
    "ð": "d",
}


class SlugError(ValueError):
    """Raised when a title cannot produce a usable slug."""


def _fold(text):
    for source, replacement in FOLD.items():
        text = text.replace(source, replacement)
    return unicodedata.normalize("NFKD", text)


def slugify(title, max_length=MAX_LENGTH):
    if not isinstance(title, str):
        raise SlugError("a title must be a string")
    folded = _fold(title.strip().lower())
    ascii_only = folded.encode("ascii", "ignore").decode("ascii")
    collapsed = re.sub(r"[^a-z0-9]+", "-", ascii_only).strip("-")
    if not collapsed:
        raise SlugError(f"{title!r} has no characters that survive slugging")
    if len(collapsed) <= max_length:
        return collapsed
    cut = collapsed[:max_length].rsplit("-", 1)[0]
    return cut or collapsed[:max_length]
