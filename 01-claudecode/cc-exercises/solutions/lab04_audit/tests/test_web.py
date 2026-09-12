import pytest

from shortener.rendering import truncate
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
    assert status == 400


# -- added by the audit: the edge cases the original suite never covered ------

@pytest.mark.parametrize("url", ["", " ", "   ", "\t\n"])
def test_create_rejects_every_blank_url(store, url):
    status, _ = create_link(store, {"url": url})
    assert status == 400


@pytest.mark.parametrize("url", [123, None, [], {}, True])
def test_create_rejects_a_non_string_url_without_crashing(store, url):
    status, _ = create_link(store, {"url": url})
    assert status == 400


def test_create_still_accepts_a_valid_url(store):
    status, body = create_link(store, {"url": "https://example.com/"})
    assert status == 200


def test_truncate_never_exceeds_its_limit():
    assert len(truncate("x" * 50, 40)) == 40
    assert truncate("short", 40) == "short"


def test_preview_rejects_a_bad_code(store):
    status, _ = preview_link(store, {"code": "nope"})
    assert status == 400


def test_preview_resolves(store):
    _, body = create_link(store, {"url": "https://example.com/"})
    status, out = preview_link(store, {"code": body["code"]})
    assert status == 200
