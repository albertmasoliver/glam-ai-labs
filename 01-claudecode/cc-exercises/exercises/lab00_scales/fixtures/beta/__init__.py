"""Public surface of the slug library.

Only the names re-exported here are public. Everything else is internal and
may change without a major version bump -- see CHANGELOG.md.
"""

from .slug import slugify, SlugError

__all__ = ["slugify", "SlugError"]
__version__ = "2.3.0"
