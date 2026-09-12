"""In-memory link storage."""

import hashlib


class Store:
    def __init__(self):
        self._links = {}

    def save(self, url):
        code = hashlib.sha256(url.encode()).hexdigest()[:7]
        self._links[code] = url
        return code

    def resolve(self, code):
        return self._links.get(code)
