#!/usr/bin/env python3
"""A whole MCP server, in one file and with no dependencies.

It speaks JSON-RPC 2.0 over stdin and stdout -- one JSON object per line,
which is all the stdio transport is -- and exposes two tools over a local
SQLite file. No network, no credentials, nothing to leak.

It is small on purpose. The interesting question in this lab is not how to
write a server; it is what connecting one costs you, and whether a ten-line
CLI would have done.

Run it:  python3 mcp_server.py      (then type a JSON-RPC line, or let
                                     Claude Code drive it)
"""

import json
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent / "library.db"

TOOLS = [
    {
        "name": "find_books",
        "description": "Books in the local library by an author. Use when asked "
                       "what a particular author has on the shelves.",
        "inputSchema": {
            "type": "object",
            "properties": {"author": {"type": "string",
                                      "description": "Full or partial author name"}},
            "required": ["author"],
        },
    },
    {
        "name": "count_by_shelf",
        "description": "How many books sit on each shelf of the local library. "
                       "Use for totals and breakdowns, not for individual titles.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def query(sql, params=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params)]
    finally:
        conn.close()


def call_tool(name, arguments):
    if name == "find_books":
        rows = query(
            "SELECT title, year, shelf FROM book WHERE author LIKE ? ORDER BY year",
            (f"%{arguments.get('author', '')}%",),
        )
        if not rows:
            return "No books by that author on these shelves."
        return "\n".join(f"{r['year']}  {r['title']}  [{r['shelf']}]" for r in rows)
    if name == "count_by_shelf":
        rows = query("SELECT shelf, COUNT(*) n FROM book GROUP BY shelf ORDER BY n DESC")
        return "\n".join(f"{r['shelf']}: {r['n']}" for r in rows)
    raise ValueError(f"no tool called {name!r}")


def handle(request):
    """Return a response object, or None for a notification."""
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        asked = (request.get("params") or {}).get("protocolVersion")
        return {
            "protocolVersion": asked or "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "library", "version": "0.1.0"},
        }
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        params = request.get("params") or {}
        try:
            text = call_tool(params.get("name"), params.get("arguments") or {})
            return {"content": [{"type": "text", "text": text}], "isError": False}
        except Exception as exc:
            return {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    if request_id is None:
        return None  # a notification we do not care about, e.g. initialized
    raise LookupError(method)


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            result = handle(request)
        except LookupError as exc:
            reply = {"jsonrpc": "2.0", "id": request.get("id"),
                     "error": {"code": -32601, "message": f"method not found: {exc}"}}
        else:
            if result is None:
                continue
            reply = {"jsonrpc": "2.0", "id": request.get("id"), "result": result}
        sys.stdout.write(json.dumps(reply) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
