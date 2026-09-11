from trainer.storage import KEY, JsonFileStorage, load_saved_index, save_index


class FakeStorage:
    """The whole point of the injected parameter: no disk, no JSON, no tmpdir."""

    def __init__(self, state=None):
        self.state = state

    def read(self):
        return self.state

    def write(self, state):
        self.state = state


class TestLoadSavedIndex:
    def test_returns_zero_when_nothing_is_stored(self):
        assert load_saved_index(FakeStorage(None), 14) == 0

    def test_returns_the_stored_index_when_valid(self):
        assert load_saved_index(FakeStorage({KEY: 6}), 14) == 6

    def test_falls_back_for_an_out_of_range_index(self):
        assert load_saved_index(FakeStorage({KEY: 99}), 14) == 0

    def test_falls_back_for_a_corrupt_value(self):
        assert load_saved_index(FakeStorage({KEY: "abc"}), 14) == 0

    def test_falls_back_when_the_state_is_not_a_mapping(self):
        assert load_saved_index(FakeStorage("garbage"), 14) == 0

    def test_falls_back_when_storage_raises(self):
        class Exploding:
            def read(self):
                raise OSError("disk on fire")

        assert load_saved_index(Exploding(), 14) == 0


class TestSaveIndex:
    def test_round_trips(self):
        storage = FakeStorage()
        save_index(storage, 9)
        assert load_saved_index(storage, 14) == 9


class TestJsonFileStorage:
    """The one place that touches the disk, so the one place that needs tmp_path."""

    def test_round_trips_through_a_real_file(self, tmp_path):
        storage = JsonFileStorage(tmp_path / "state.json")
        save_index(storage, 4)
        assert load_saved_index(storage, 14) == 4

    def test_missing_file_reads_as_none(self, tmp_path):
        assert JsonFileStorage(tmp_path / "nope.json").read() is None

    def test_corrupt_file_reads_as_none(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("not json at all")
        assert JsonFileStorage(p).read() is None
