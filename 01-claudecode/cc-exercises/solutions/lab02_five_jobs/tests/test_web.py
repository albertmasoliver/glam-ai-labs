import pytest

from notes.store import Store
from notes.web import create_note


@pytest.fixture
def store():
    return Store()


def test_create_returns_the_new_id(store):
    status, body = create_note(store, {"title": "Groceries", "body": "milk"})
    assert status == 200
    assert body["id"] == 1


def test_create_rejects_a_long_body(store):
    status, body = create_note(store, {"title": "Groceries", "body": "y" * 10_001})
    assert status == 400
    assert body["error"] == "body is too long"


def test_create_rejects_empty_title(store):
    status, body = create_note(store, {"title": "", "body": "milk"})
    assert status == 400
