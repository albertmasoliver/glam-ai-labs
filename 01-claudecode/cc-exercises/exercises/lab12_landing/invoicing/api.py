"""HTTP surface. Thin by policy: routes parse, delegate, and serialise.

Execution starts in `scripts/serve.py`, not here -- this module only builds
the handler class. There is no framework; the 2019 rewrite removed it and
nobody has put one back.
"""

import json
from http.server import BaseHTTPRequestHandler

from . import numbering, service
from .models import Invoice, LineItem, Party


def _parse_invoice(payload):
    issuer = Party(**payload["issuer"])
    customer = Party(**payload["customer"])
    lines = [LineItem(**l) for l in payload.get("lines", [])]
    number = payload.get("number") or numbering.reserve(issuer.code)
    return Invoice(number, issuer, customer, lines,
                   currency=payload.get("currency", "EUR"))


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        raw = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid json"})

        if self.path == "/invoices/preview":
            return self._send(200, service.render(_parse_invoice(payload)))

        if self.path == "/invoices/confirm":
            invoice = _parse_invoice(payload)
            try:
                result = service.confirm(invoice)
            except service.InvoiceError as exc:
                return self._send(422, {"error": str(exc)})
            return self._send(200, {**service.render(invoice), **result})

        self._send(404, {"error": "no such route"})

    def log_message(self, *args):
        pass
