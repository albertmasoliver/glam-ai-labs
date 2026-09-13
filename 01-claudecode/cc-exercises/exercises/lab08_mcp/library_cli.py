#!/usr/bin/env python3
"""The same two capabilities as the MCP server, as a command line tool.

    python3 library_cli.py author Jemisin
    python3 library_cli.py shelves

Twelve lines of logic against the same database. Whether this is better than
the server depends entirely on what you measured, which is the lab.

Run it:  python3 library_cli.py <author NAME | shelves>
"""

import sys

from mcp_server import call_tool


def main(argv):
    if len(argv) >= 3 and argv[1] == "author":
        print(call_tool("find_books", {"author": " ".join(argv[2:])}))
        return 0
    if len(argv) >= 2 and argv[1] == "shelves":
        print(call_tool("count_by_shelf", {}))
        return 0
    print(__doc__.strip().splitlines()[-1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
