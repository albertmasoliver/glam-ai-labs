import pytest

from trainer.lines import LINES
from trainer.navigation import LineTrainer, normalize_index


class TestLineTrainer:
    def test_starts_at_the_first_line_by_default(self):
        trainer = LineTrainer(LINES)
        assert trainer.current_index == 0
        assert trainer.current_line == LINES[0]

    def test_advances_to_the_next_line(self):
        trainer = LineTrainer(LINES)
        assert trainer.next() == LINES[1]
        assert trainer.current_index == 1

    def test_wraps_at_the_end(self):
        trainer = LineTrainer(LINES, len(LINES) - 1)
        assert trainer.next() == LINES[0]
        assert trainer.current_index == 0

    def test_resumes_from_a_valid_initial_index(self):
        trainer = LineTrainer(LINES, 5)
        assert trainer.current_index == 5
        assert trainer.current_line == LINES[5]

    def test_a_full_cycle_returns_to_the_start(self):
        trainer = LineTrainer(LINES)
        for _ in range(len(LINES)):
            trainer.next()
        assert trainer.current_index == 0


class TestNormalizeIndex:
    def test_keeps_a_valid_index(self):
        assert normalize_index(7, len(LINES)) == 7

    @pytest.mark.parametrize(
        "bad",
        ["not-a-number", -1, 99, 1.5, None, True, [], {}],
        ids=["string", "negative", "too-big", "float", "none", "bool", "list", "dict"],
    )
    def test_falls_back_to_zero_for_invalid_values(self, bad):
        assert normalize_index(bad, len(LINES)) == 0

    def test_falls_back_at_the_boundary(self):
        assert normalize_index(len(LINES), len(LINES)) == 0
        assert normalize_index(len(LINES) - 1, len(LINES)) == len(LINES) - 1
