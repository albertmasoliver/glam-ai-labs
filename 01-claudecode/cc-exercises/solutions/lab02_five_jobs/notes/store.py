"""In-memory note storage. Knows nothing about requests or status codes."""


class Store:
    def __init__(self):
        self._notes = {}
        self._next_id = 1

    def save(self, note):
        stored = {**note, "id": self._next_id}
        self._notes[self._next_id] = stored
        self._next_id += 1
        return stored

    def update(self, note_id, fields):
        if note_id not in self._notes:
            return None
        self._notes[note_id] = {**self._notes[note_id], **fields}
        return self._notes[note_id]

    def get(self, note_id):
        return self._notes.get(note_id)
