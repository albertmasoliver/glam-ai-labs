import pytest

from beta import SlugError, slugify


def test_lowercases_and_joins_with_hyphens():
    assert slugify("Hello There World") == "hello-there-world"


def test_folds_characters_that_ascii_would_drop():
    assert slugify("Straße") == "strasse"


def test_never_ends_on_a_hyphen():
    assert not slugify("  spaced  out  ").endswith("-")


def test_cuts_on_a_word_boundary():
    assert slugify("alpha beta gamma delta", max_length=12) == "alpha-beta"


def test_a_title_with_nothing_sluggable_is_an_error():
    with pytest.raises(SlugError):
        slugify("!!!")
