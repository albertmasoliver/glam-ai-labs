"""Line-navigation rules.

Knows nothing about printing, input, files or JSON. Every function here can be
verified without touching the filesystem or stdout.
"""


def normalize_index(value, length):
    """Return a usable index, or 0 for anything out of range or not an int."""
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    if value < 0 or value >= length:
        return 0
    return value


class LineTrainer:
    def __init__(self, lines, initial_index=0):
        self._lines = lines
        self._index = normalize_index(initial_index, len(lines))

    @property
    def current_index(self):
        return self._index

    @property
    def current_line(self):
        return self._lines[self._index]

    def next(self):
        self._index = (self._index + 1) % len(self._lines)
        return self.current_line
