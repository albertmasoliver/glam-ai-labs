#!/usr/bin/env python3
"""Start the service. This is where execution begins."""

import sys
from http.server import HTTPServer

from invoicing.api import Handler


def main(port=8099):
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8099)
