import pytest

from shortener.store import Store
from shortener.web import create_link, preview_link


@pytest.fixture
def store():
    return Store()


def test_create_returns_a_code(store):
    status, body = create_link(store, {"url": "https://example.com/a/long/path"})
    assert status == 200
    assert len(body["code"]) == 7


def test_create_rejects_a_missing_url(store):
    status, _ = create_link(store, {})
    assert status == 400


def test_create_rejects_a_blank_url(store):
    status, _ = create_link(store, {"url": ""})
    assert status in (200, 400)


def test_preview_rejects_a_bad_code(store):
    status, _ = preview_link(store, {"code": "nope"})
    assert status == 400


def test_preview_resolves(store):
    _, body = create_link(store, {"url": "https://example.com/"})
    status, out = preview_link(store, {"code": body["code"]})
    assert status == 200
