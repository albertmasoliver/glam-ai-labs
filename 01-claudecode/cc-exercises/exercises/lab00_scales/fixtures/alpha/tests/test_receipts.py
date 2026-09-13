import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from receipts import format_table, totals_by_category


def test_sums_rows_that_share_a_category():
    rows = [{"category": "Food", "amount": "10"}, {"category": "food", "amount": "5"}]
    assert totals_by_category(rows) == {"food": 15.0}


def test_skips_amounts_that_are_not_numbers():
    rows = [{"category": "food", "amount": "oops"}, {"category": "food", "amount": "2"}]
    assert totals_by_category(rows) == {"food": 2.0}


def test_missing_category_falls_back():
    assert totals_by_category([{"amount": "3"}]) == {"uncategorised": 3.0}


def test_empty_input_says_so():
    assert format_table({}) == "nothing to total"
