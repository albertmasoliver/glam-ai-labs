import json
import threading
import urllib.request
from http.server import HTTPServer

import pytest

from invoicing.api import Handler


@pytest.fixture
def server():
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def _post(base, path, payload):
    req = urllib.request.Request(base + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


PAYLOAD = {
    "issuer": {"code": "ACME", "name": "Acme Iberia SL", "vat_number": "ESB00000000"},
    "customer": {"code": "C1", "name": "Cliente Uno"},
    "lines": [{"description": "widget", "quantity": 2, "unit_price_cents": 1000}],
}


def test_preview_returns_totals(server):
    status, body = _post(server, "/invoices/preview", PAYLOAD)
    assert status == 200
    assert body["gross"] == 24.20


def test_unknown_route(server):
    status, _ = _post(server, "/nope", PAYLOAD)
    assert status == 404
